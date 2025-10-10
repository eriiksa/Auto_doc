from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium import webdriver
from selenium.webdriver.common.by import By
import sys
import os
import time

def resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, funcionando para dev e para o .exe do PyInstaller """
    try:
        base_path = sys._MEIPASS #type: ignore
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_driver(pasta_download: str, use_tivit: bool) -> WebDriver:
    """
    Configura e inicializa o navegador Edge.
    O navegador será headless apenas se a opção de usar o Tivit estiver DESMARCADA.
    """
    print("Configurando o driver do navegador...")
    options = EdgeOptions()
    options.add_experimental_option("detach", True)
    prefs = {"download.default_directory": pasta_download}
    options.add_experimental_option("prefs", prefs)
    
    # Se a caixa do Tivit NÃO estiver marcada, o navegador será headless.
    # Se estiver marcada, ele abrirá a janela normalmente para visualização.
    if not use_tivit:
        print("Aba invisível ativada (Tivit não será usado).")
        options.add_argument("--headless")
    else:
        print("Modo com janela ativado (Tivit será usado).")

    
    service = EdgeService() 
    driver = webdriver.Edge(service=service, options=options)
    
    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {
            "behavior": "allow",
            "downloadPath": pasta_download
        }
    )

    driver.maximize_window()
    driver.set_window_size(1920, 1080)
    
    return driver   
    print("Configurando o driver do navegador...")
    options = EdgeOptions()
    options.add_experimental_option("detach", True)
    prefs = {"download.default_directory": pasta_download}
    options.add_experimental_option("prefs", prefs)
    
    
    options.add_argument("--headless")
    
    service = EdgeService() 
    driver = webdriver.Edge(service=service, options=options)
    
    # FEATURE: Habilita o download no modo headless
    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {
            "behavior": "allow",
            "downloadPath": pasta_download
        }
    )

    # BUG FIX: Garante que a janela seja maximizada para evitar erros de elemento não encontrado
    driver.maximize_window()
    driver.set_window_size(1920, 1080) # Também define um tamanho para o modo headless
    
    return driver

def wait_and_click(driver: WebDriver, locator: tuple, timeout: int = 20) -> None:
    wait = WebDriverWait(driver, timeout)
    elem = wait.until(EC.element_to_be_clickable(locator))
    elem.click()

def wait_until_present(driver: WebDriver, locator: tuple, timeout: int = 20) -> WebElement:
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located(locator))

def wait_until_element_clickable(driver: WebDriver, locator: tuple, timeout: int = 20) -> WebElement:
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.element_to_be_clickable(locator))

def element_is_present(driver: WebDriver, locator: tuple, timeout: int = 3) -> bool:
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))
        return True
    except TimeoutException:
        return False

def scroll_and_click(driver: WebDriver, locator: tuple, timeout: int = 20) -> None:
    """Espera um elemento estar presente, rola a tela até ele ficar visível e então clica nele."""
    wait = WebDriverWait(driver, timeout)
    elem = wait.until(EC.presence_of_element_located(locator))
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elem)
    time.sleep(1) 
    elem = wait.until(EC.element_to_be_clickable(locator))
    elem.click()

# redirecionar prints para a interface
class QueueLogger:
    """Um objeto que se comporta como um console, mas redireciona todas as mensagens para uma fila da GUI."""
    def __init__(self, queue):
        self.queue = queue
    def write(self, text):
        if text.strip():
            self.queue.put(text.strip())
    def flush(self):
        pass