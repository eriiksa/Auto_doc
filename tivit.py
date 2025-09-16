from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import utilidades
import gerenciador_arquivos


def login_tivit(driver, user: str, pwd: str):
    """Realiza o login no sistema Tivit."""
    print("Iniciando login no Tivit...")
    driver.get("https://ecm.tivit.com/portal/principal_rh.aspx")

    utilidades.wait_until_present(
        driver, (By.ID, "txtCliente")).send_keys("TNT")
    utilidades.wait_until_present(
        driver, (By.ID, "txtUsuario")).send_keys(user)
    utilidades.wait_until_present(driver, (By.ID, "txtSenha")).send_keys(pwd)
    utilidades.wait_until_element_clickable(
        driver, (By.CSS_SELECTOR, "button.btn.btn-primary")).click()

    print("Login no Tivit realizado com sucesso.")


def navegar_para_consulta_tivit(driver):
    """Navega pelos menus usando cliques sequenciais para abrir os submenus."""
    print("Navegando pelos menus do Tivit via cliques...")
    try:
        wait = WebDriverWait(driver, 15)
        time.sleep(.5)
        xpath_menu_pesquisa = "//*[@id='nav']/li[1]/a"
        xpath_submenu_ctrc = "//*[@id='nav']/li[1]/ul/li[1]/a"
        xpath_link_final = "//*[@id='nav']/li[1]/ul/li[1]/ul/li[1]/a"

        wait.until(EC.element_to_be_clickable(
            (By.XPATH, xpath_menu_pesquisa))).click()
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, xpath_submenu_ctrc))).click()
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, xpath_link_final))).click()
        time.sleep(.5)
        print("Navegação para a tela de consulta de conhecimentos concluída.")

    except TimeoutException:
        print("FALHA: Não foi possível encontrar ou clicar em um dos elementos do menu de navegação.")
        raise


def consulta_tivit(driver, cte_atual: str, pasta_trabalho: str):
    """
    Realiza a consulta de um contrato no Tivit e verifica se o download do PDF foi iniciado.
    Retorna True se o download foi iniciado, False caso contrário.
    """
    print(f"Iniciando do cte no Tivit: {cte_atual}")
    cte_clean = cte_atual.replace("-", "").strip().upper()

    try:
        campo_filial_conhecimento = utilidades.wait_until_present(
            driver, (By.ID, "ContentPlaceHolder1_txtSiglaFilialOrigem"))
        campo_filial_conhecimento.send_keys(Keys.CONTROL + 'a', Keys.BACKSPACE)
        campo_filial_conhecimento.send_keys(cte_clean[:3])

        campo_numero_conhecimento = utilidades.wait_until_present(
            driver, (By.ID, "ContentPlaceHolder1_TxtConhecimento"))
        campo_numero_conhecimento.send_keys(Keys.CONTROL + 'a', Keys.BACKSPACE)
        campo_numero_conhecimento.send_keys(cte_clean[3:])

        campo_pesquisa_conhecimento = utilidades.wait_until_present(
            driver, (By.ID, "ContentPlaceHolder1_Button1"))
        campo_pesquisa_conhecimento.click()
        print(
            f"Consulta para o CTE {cte_atual} realizada. Verificando resultado...")

        aba_principal = driver.current_window_handle
        try:
            utilidades.wait_and_click(
                driver, (By.CSS_SELECTOR, "img[title='Clique para efetuar o download da Imagem']"), timeout=5)
            print("Lupa de download clicada. Aguardando nova aba...")
            time.sleep(3)  # Pausa para a nova aba carregar

            url_pdf_download = [
                aba for aba in driver.window_handles if aba != aba_principal][0]
            driver.switch_to.window(url_pdf_download)

            url_pdf_download = driver.current_url
            caminho_salvo = gerenciador_arquivos.baixar_pdf_de_url(
                url_pdf_download, pasta_trabalho, cte_clean)

            driver.close()
            driver.switch_to.window(aba_principal)

            return caminho_salvo
        except TimeoutException:
            alerta_locator = (
                By.XPATH, "//span[@id='ContentPlaceHolder1_lblAlerta' and contains(text(), 'Pesquisa não localizada.')]")
            if utilidades.element_is_present(driver, alerta_locator):
                print(
                    f"AVISO: O Arquivo do CTE {cte_atual} não está no Tivit")
                return False
            else:
                print(
                    f"FALHA: Não foi encontrado nem o botão de download nem a mensagem de alerta para o CTE {cte_atual}.")
            return None

    except Exception as e:
        print(f"ERRO: Ocorreu um erro ao consultar o CTE {cte_atual}: {e}")
        return None


if __name__ == "__main__":

    USER_TIVIT_TESTE = "jessica.infante"
    PWD_TIVIT_TESTE = "#We05je06"

    try:
        path_desktop = gerenciador_arquivos.obter_path_desktop()
        PASTA_TESTE = os.path.join(path_desktop, "ctes")
        os.makedirs(PASTA_TESTE, exist_ok=True)
        print(f"Pasta de teste configurada para: {PASTA_TESTE}")
        driver = utilidades.get_driver(PASTA_TESTE)

        login_tivit(driver, USER_TIVIT_TESTE, PWD_TIVIT_TESTE)
        navegar_para_consulta_tivit(driver)

        caminho_do_pdf_baixado = consulta_tivit(driver, "CJR789263", PASTA_TESTE)
        
        if caminho_do_pdf_baixado:
            print(f"\nIniciando processo de renomeação para: {os.path.basename(caminho_do_pdf_baixado)}")
            gerenciador_arquivos.renomear_pdf_pela_nf(caminho_do_pdf_baixado)
        print("\n--- Teste finalizado com sucesso! O navegador permanecerá aberto. ---")
        
    except Exception as e:
        print(f"\n--- Ocorreu um erro durante o teste: {e} ---")
