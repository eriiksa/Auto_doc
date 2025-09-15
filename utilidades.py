
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium import webdriver

def get_driver(pasta_download: str) -> WebDriver:
    """Configura e inicializa o navegador Edge com uma pasta de download específica."""
    print("Configurando o driver do navegador...")
    options = EdgeOptions()
    options.add_experimental_option("detach", True)
    prefs = {"download.default_directory": pasta_download}
    options.add_experimental_option("prefs", prefs)
    
    try:
        service = EdgeService()
        driver = webdriver.Edge(service=service, options=options)
    except Exception:
        service = EdgeService(executable_path="msedgedriver.exe")
        driver = webdriver.Edge(service=service, options=options)  

    driver.maximize_window()
    return driver

def wait_and_click(driver: WebDriver, locator: tuple, timeout: int = 20) -> None:
    """Espera um elemento se tornar clicável e então clica nele."""
    wait = WebDriverWait(driver, timeout)
    elem = wait.until(EC.element_to_be_clickable(locator))
    elem.click()

def wait_until_present(driver: WebDriver, locator: tuple, timeout: int = 20) -> WebElement:
    """Espera um elemento estar presente na página e o retorna."""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located(locator))

def wait_until_element_clickable(driver: WebDriver, locator: tuple, timeout: int = 20) -> WebElement:
    """Espera um elemento ser clicável e o retorna."""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.element_to_be_clickable(locator))