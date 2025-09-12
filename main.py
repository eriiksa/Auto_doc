
import os
import re
import time
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.common.exceptions import TimeoutException
import gerenciador_arquivos

def get_driver(pasta_download: str) -> webdriver.Edge:
    """Configura e inicializa o navegador Edge com uma pasta de download específica."""
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

def login_enfase(driver, user, password):
    """Realiza o login no sistema Enfase e navega até a tela de relatório."""
    print("Iniciando login no Enfase...")
    driver.get("https://enfase.lac.fedex.com/enfaseweb/")
    
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.ID, "Login"))).send_keys(user)
    driver.find_element(By.ID, "Password").send_keys(password + Keys.ENTER)

    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Consulta')]"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/enfaseweb/CTE/Relatorio']"))).click()
    print("Login realizado com sucesso.")

def consulta_cte_enfase(driver, cte: str) -> bool:
    """
    Preenche os dados do CTE, executa a consulta e clica em download.
    Retorna True se o download foi iniciado, False caso o botão de download não seja encontrado.
    """
    print("-" * 50)
    print(f"Iniciando consulta para o CTE: {cte}")
    wait = WebDriverWait(driver, 20)
    
    cte_clean = cte.replace("-", "").strip().upper()
    if len(cte_clean) < 4:
        print(f"AVISO: CTE '{cte}' parece inválido. Pulando.")
        return True # Retorna True para não adicionar à lista de falhas por erro de digitação

    cte_sem_filial = cte_clean[3:]
    filial_cte = cte_clean[:3]

    try:
        campo_cte = wait.until(EC.presence_of_element_located((By.ID, "CTE")))
        campo_cte.send_keys(Keys.CONTROL + "a")
        campo_cte.send_keys(cte_sem_filial)

        serie_input = wait.until(EC.presence_of_element_located((By.ID, "SerieCTE")))
        serie_input.send_keys("0000")
        
        driver.find_element(By.ID, "Filial").send_keys(filial_cte + Keys.ENTER)
        driver.find_element(By.ID, "btnLocalizar").click()
        print(f"Consulta para o CTE {cte} realizada.")
        time.sleep(1)  
        
        try:
            download_wait = WebDriverWait(driver, 1) 
            botao_download = download_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[title='Download']")))
            botao_download.click()
            print("Download do PDF iniciado.")
            return True 
        except TimeoutException:
            print(f"FALHA: Botão de download para o CTE {cte} não foi encontrado.")
            return False  # Falha: Sinaliza para adicionar à lista
            
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a consulta do CTE {cte}: {e}")
        return True # Sucesso para não adicionar à lista de falhas por um erro genérico

def obter_lista_ctes() -> List[str]:
    """Solicita ao usuário que cole uma lista de CTEs e retorna uma lista limpa."""
    print("\nCOLE AQUI OS CTES (um por linha, separados por espaço ou vírgula):")
    print("Após colar, pressione Enter em uma linha vazia para iniciar.")
    
    lines = []
    while True:
        line = input()
        if line:
            lines.append(line)
        else:
            break
    raw_input = "\n".join(lines)
    
    # Limpa e separa os CTEs em uma lista, removendo itens vazios
    lista_de_ctes = [cte.strip() for cte in re.split(r'[,\s\n]+', raw_input) if cte.strip()]
    return lista_de_ctes

# --- BLOCO DE EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    user = "6360955"
    password = "fedex0955"
    
    caminho_desktop = gerenciador_arquivos.obter_caminho_area_de_trabalho()
    PASTA_CTES = os.path.join(caminho_desktop, "ctes")

    print(f"Pasta de destino configurada para: {PASTA_CTES}")

    lista_de_ctes = obter_lista_ctes()
    ctes_nao_encontrados = []

    if not lista_de_ctes:
        print("Nenhum CTE inserido. Encerrando o programa.")
    else:
        print(f"\n{len(lista_de_ctes)} CTEs para processar. Iniciando automação...")
        driver = get_driver(PASTA_CTES)
        
        try:
            login_enfase(driver, user, password)
            
            # --- LOOP PRINCIPAL ---
            for cte_atual in lista_de_ctes:
                sucesso_consulta = consulta_cte_enfase(driver, cte=cte_atual)
                
                if sucesso_consulta:
                    print("Aguardando download...")
                    caminho_pdf = gerenciador_arquivos.encontrar_ultimo_pdf_baixado(PASTA_CTES)
                    if caminho_pdf:
                        gerenciador_arquivos.renomear_pdf_pela_nf(caminho_pdf)
                else:
                    ctes_nao_encontrados.append(cte_atual)
                
                time.sleep(2) # Pausa entre as consultas para não sobrecarregar o sistema

        except Exception as e:
            print(f"Ocorreu um erro fatal no script: {e}")
        finally:
            # --- RELATÓRIO FINAL ---
            print("\n" + "="*50)
            print("--- PROCESSO FINALIZADO ---")
            if ctes_nao_encontrados:
                print(f"\nATENÇÃO: {len(ctes_nao_encontrados)} CTE(s) não foram encontrados para download:")
                for cte in ctes_nao_encontrados:
                    print(f" - {cte}")
            else:
                print("\nTodos os CTEs foram processados com sucesso!")
            print("="*50)