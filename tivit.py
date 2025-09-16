from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
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
        wait = utilidades.WebDriverWait(driver, 15)

        xpath_menu_pesquisa = "//*[@id='nav']/li[1]/a"
        xpath_submenu_ctrc = "//*[@id='nav']/li[1]/ul/li[1]/a"
        xpath_link_final = "//*[@id='nav']/li[1]/ul/li[1]/ul/li[1]/a"

        menu_pesquisa = wait.until(
            EC.element_to_be_clickable((By.XPATH, xpath_menu_pesquisa)))
        menu_pesquisa.click()

        submenu_ctrc = wait.until(
            EC.element_to_be_clickable((By.XPATH, xpath_submenu_ctrc)))
        submenu_ctrc.click()
        time.sleep(.25)

        link_final = wait.until(
            EC.element_to_be_clickable((By.XPATH, xpath_link_final)))
        link_final.click()
        print("Navegação para a tela de consulta de conhecimentos concluída.")

    except TimeoutException:
        print("FALHA: Não foi possível encontrar ou clicar em um dos elementos do menu de navegação.")
        raise


def consulta_tivit(driver, cte_atual: str, pasta_trabalho: str) -> bool:
    """
    Realiza a consulta de um contrato no Tivit e verifica se o download do PDF foi iniciado.
    Retorna True se o download foi iniciado, False caso contrário.
    """
    print(f"Iniciando do cte no Tivit: {cte_atual}")

    cte_clean = cte_atual.replace("-", "").strip().upper()
    if len(cte_clean) < 4:
        print(f"AVISO: CTE '{cte_atual}' parece inválido. Pulando.")
        return True

    try:
        campo_filial_conhecimento = utilidades.wait_until_present(
            driver, (By.ID, "ContentPlaceHolder1_txtSiglaFilialOrigem"))
        campo_filial_conhecimento.send_keys(Keys.CONTROL + "a")
        campo_filial_conhecimento.send_keys(Keys.BACKSPACE)
        campo_filial_conhecimento.send_keys(cte_clean[:3])

        campo_numero_conhecimento = utilidades.wait_until_present(
            driver, (By.ID, "ContentPlaceHolder1_TxtConhecimento"))
        campo_numero_conhecimento.send_keys(Keys.CONTROL + "a")
        campo_numero_conhecimento.send_keys(Keys.BACKSPACE)
        campo_numero_conhecimento.send_keys(cte_clean[3:])

        campo_pesquisa_conhecimento = utilidades.wait_until_present(
            driver, (By.ID, "ContentPlaceHolder1_Button1"))
        campo_pesquisa_conhecimento.click()

        utilidades.wait_and_click(driver, (By.ID, "btnConsultar"))
        print(f"Consulta para o CTE {cte_atual} realizada.")

        try:
            utilidades.wait_and_click(
                driver, (By.CSS_SELECTOR, "img[title='Clique para efetuar o download da Imagem']"), timeout=3)
            print("Download do PDF iniciado.")
            return True
        except:
            pesquisa_nao_localizada = utilidades.element_is_present(
                driver, (By.ID, "ContentPlaceHolder1_lblAlerta"))
            if pesquisa_nao_localizada:
                print(
                    f"AVISO: A pesquisa para o CTE {cte_atual} não foi localizada.")
            return False
    except Exception as e:
        print(f"ERRO: Ocorreu um erro ao consultar o CTE {cte_atual}: {e}")
        return False


if __name__ == "__main__":

    USER_TIVIT_TESTE = "jessica.infante"
    PWD_TIVIT_TESTE = "#We05je06"

    print("--- MODO DE TESTE DO TIVIT.PY ---")

    try:
        print("Configurando ambiente de teste...")
        path_desktop = gerenciador_arquivos.obter_path_desktop()
        PASTA_TESTE = os.path.join(path_desktop, "tivit_teste_downloads")
        os.makedirs(PASTA_TESTE, exist_ok=True)
        driver = utilidades.get_driver(PASTA_TESTE)

        login_tivit(driver, USER_TIVIT_TESTE, PWD_TIVIT_TESTE)
        navegar_para_consulta_tivit(driver)
        consulta_tivit(driver, "SAO115093733", PASTA_TESTE)
        print("\n--- Teste finalizado com sucesso! O navegador permanecerá aberto. ---")
        time.sleep(60)
    except Exception as e:
        print(f"\n--- Ocorreu um erro durante o teste: {e} ---")
