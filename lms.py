from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time 
from gerenciador_arquivos import verificar_novo_download, extrair_e_mover_pdfs_do_zip
import utilidades
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

def consulta_lms(driver, cte: str, pasta_trabalho: str) -> List[str] | str:
    """
    Busca o CTe no LMS seguindo o fluxo de duas etapas de carregamento e 
    verificação de resultado (download ou alerta).
    """
    print(f"Consultando CTE {cte} no LMS...")
    try:
        campo_docto = wait_until_element_clickable(driver, (By.ID, "doctoServico"))
        time.sleep(1)
        campo_docto.send_keys(Keys.CONTROL + 'a'); campo_docto.send_keys(Keys.DELETE)
        campo_docto.send_keys(cte.replace("-", "").strip() + Keys.TAB)
        time.sleep(.5)
        wait_and_click(driver, (By.ID, "consultar"), timeout=15)
        print("Aguardando a busca inicial no LMS ser concluída...")

        XPATH_LOADER = "//img[@src='/lmsa/img/ajax-loader.gif']"
        wait_busca = WebDriverWait(driver, 20)
        wait_busca.until(EC.invisibility_of_element_located((By.XPATH, XPATH_LOADER)))
        
        print("Busca inicial concluída. Clicando no botão 'Imagem'...")

        botao_imagem = wait_until_element_clickable(driver, (By.XPATH, "//a[@permission='imagem']"), timeout=10)
        timestamp_antes_do_clique = time.time()
        botao_imagem.click()

        print("Aguardando o processamento do download...")
        wait_download = WebDriverWait(driver, 25) 
        wait_download.until(EC.invisibility_of_element_located((By.XPATH, XPATH_LOADER)))
        
        print("Processamento finalizado. Verificando o resultado...")

        # Verificar o resultado (Download OU Alerta)
        caminho_zip = verificar_novo_download(pasta_trabalho, timestamp_antes_do_clique, timeout=3)
        if caminho_zip:
            return extrair_e_mover_pdfs_do_zip(caminho_zip, pasta_trabalho)
        else:
            xpath_alerta = "//div[contains(@class, 'alert-danger')]//span[contains(text(), 'Arquivo não encontrado.')]"
            if utilidades.element_is_present(driver, (By.XPATH, xpath_alerta), timeout=2):
                print("AVISO: Alerta 'Arquivo não encontrado.' detectado.")
                try:
                    close_button = driver.find_element(By.XPATH, "//div[contains(@class, 'alert-danger')]//button[@class='close']")
                    close_button.click()
                except Exception:
                    pass
                return []
            else:
                # Se nem o download nem o alerta foram encontrados, retorna falha.
                print(f"FALHA: O loader desapareceu, mas o download do CTE {cte} não iniciou e nenhum alerta foi encontrado.")
                return []

    except TimeoutException:
        print(f"ERRO CRÍTICO: LMS travou ou demorou demais no CTE {cte}. A aba será reiniciada.")
        return "TIMEOUT_CRASH"
    
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao consultar o CTE no LMS: {e}")
        return []

def rerun_consulta(driver):
    elemento_consulta = wait_until_present(
        driver, (By.XPATH, "//a[@data-ng-click='aba.click()' and contains(., 'Consulta')]"), timeout=15)
    driver.execute_script("arguments[0].click();", elemento_consulta)
    time.sleep(1) # se der problema,voltar pro 2s
