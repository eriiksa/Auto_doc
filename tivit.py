from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import utilidades
import gerenciador_arquivos
import requests


def login_tivit(driver, user: str, pwd: str):
    """Realiza o login no sistema Tivit."""
    print("Iniciando login no Tivit...")
    driver.get("https://ecm.tivit.com/portal/principal_rh.aspx")

    utilidades.wait_until_present( driver, (By.ID, "txtCliente")).send_keys("TNT")
    utilidades.wait_until_present( driver, (By.ID, "txtUsuario")).send_keys(user)
    time.sleep(.5)
    utilidades.wait_until_present(driver, (By.ID, "txtSenha")).send_keys(pwd)
    time.sleep(.3)
    utilidades.wait_until_element_clickable(driver, (By.CSS_SELECTOR, "button.btn.btn-primary")).click()

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
        abas_antes_do_clique = driver.window_handles
        try:
            utilidades.wait_and_click(
                driver, (By.CSS_SELECTOR, "img[title='Clique para efetuar o download da Imagem']"), timeout=5)
            print("Lupa de download clicada. Aguardando nova aba...")
            wait = WebDriverWait(driver, 15)
            wait.until(EC.number_of_windows_to_be(len(driver.window_handles)))

            aba_pdf_handle = [aba for aba in driver.window_handles if aba not in abas_antes_do_clique][0]
            driver.switch_to.window(aba_pdf_handle)

            url_pdf_download = driver.current_url
            print("Iniciando download do PDF em segundo plano...")
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

