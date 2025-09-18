from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time 
from gerenciador_arquivos import verificar_novo_download, extrair_e_mover_pdfs_do_zip
from utilidades import wait_and_click, wait_until_present, wait_until_element_clickable


def login_lms(driver, user: str, pwd: str):
    """Realiza o login no sistema LMS."""
    print("Iniciando login no LMS...")
    driver.get("https://lms.lac.fedex.com/lmsa/view/login")
    wait_until_present(driver, (By.ID, "usuario")).send_keys(user)
    wait_until_present(driver, (By.ID, "senha")).send_keys(pwd)

    wait_and_click(
        driver, (By.XPATH, "//a[contains(., 'Eu concordo') and @href='#']"))
    wait_and_click(
        driver, (By.CSS_SELECTOR, ".btn.btn-primary.btn-lg[value='Entrar']"))
    time.sleep(5)  # Espera a página carregar completamente

def consulta_sim(driver):
    """Navega até a tela de consulta SIM no LMS."""
    toggle_menu = wait_until_present(driver, (By.XPATH, "//button[@class='navbar-toggle' and contains(@ng-click, 'toggleMenu')]"), timeout=20)
    print("Login no LMS realizado com sucesso.")
    toggle_menu.click()

    botao_sim = wait_until_present(driver, (By.XPATH, "//a[contains(text(),'SIM') ]"))
    botao_sim.click()
    
    consultas_relatorios = wait_until_present(driver, (By.XPATH, "//a[contains(text(),'Consultas e Relatórios') ]"))
    consultas_relatorios.click()

    consultar_localizacoes = wait_until_present(driver, (By.XPATH, "//a[contains(text(),'Consultar Localizações de Mercadoria (Novo)') ]"))
    consultar_localizacoes.click()


def consulta_lms(driver, cte: str, pasta_trabalho: str) -> List[str]:
    """
    Busca o CTe no LMS, clica em Imagem, verifica o download do .zip,
    extrai o PDF para a pasta de trabalho e retorna os caminhos dos PDFs.
    """
    print(f"Consultando CTE {cte} no LMS...")
    try:
        campo_docto = wait_until_element_clickable(
            driver, (By.ID, "doctoServico"))
        time.sleep(1)
        campo_docto.send_keys(Keys.CONTROL + 'a')
        campo_docto.send_keys(Keys.DELETE)
        campo_docto.send_keys(cte.replace("-", "").strip() + Keys.ENTER)
        time.sleep(1)
        wait_and_click(driver, (By.ID, "consultar"), timeout=15)
        time.sleep(2)  
        wait = WebDriverWait(driver, 3) #3s para acompanhar delay do LMS

        xpath_combinado = "//*[contains(text(), 'Arquivo não encontrado')] | //a[@permission='imagem']"
        
        elemento_encontrado = wait.until(
            EC.presence_of_element_located((By.XPATH, xpath_combinado))
        )
        if "Arquivo não encontrado" in elemento_encontrado.text:
            print("FALHA: Mensagem 'Arquivo não encontrado.' detectada no LMS.")
            return []

        botao_imagem = elemento_encontrado
        timestamp_antes_do_clique = time.time()
        botao_imagem.click()
        print("Botão 'Imagem' clicado. Verificando o download do .zip...")

        caminho_zip = verificar_novo_download(pasta_trabalho, timestamp_antes_do_clique)

        if caminho_zip:
            return extrair_e_mover_pdfs_do_zip(caminho_zip, pasta_trabalho)
        else:
            return []

    except TimeoutException:
        print(f"FALHA: Não foi possível encontrar nem o botão 'Imagem' nem a mensagem de erro no LMS para o CTE {cte}.")
        return []
    except Exception as e:
        print(f"Ocorreu um erro ao consultar o CTE no LMS: {e}")
        return []


def rerun_consulta(driver):
    elemento_consulta = wait_until_present(
        driver, (By.XPATH, "//a[@data-ng-click='aba.click()' and contains(., 'Consulta')]"), timeout=15)
    driver.execute_script("arguments[0].click();", elemento_consulta)
    time.sleep(1) # se der problema,voltar pro 2s
