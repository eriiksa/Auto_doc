import os
import re
import time
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import gerenciador_arquivos
import utilidades 
from lms import login_lms, consulta_sim, consulta_lms, rerun_consulta
from tivit import login_tivit, navegar_para_consulta_tivit, consulta_tivit

def login_enfase(driver, user_enfase, pwd_enfase):
    """Realiza o login no sistema Enfase e navega até a tela de relatório."""
    print("Iniciando login no Enfase...")
    driver.get("https://enfase.lac.fedex.com/enfaseweb/")
    
    utilidades.wait_until_present(driver, (By.ID, "Login")).send_keys(user_enfase)
    driver.find_element(By.ID, "Password").send_keys(pwd_enfase + Keys.ENTER)

    utilidades.wait_and_click(driver, (By.XPATH, "//button[contains(text(),'Consulta')]"))
    utilidades.wait_and_click(driver, (By.XPATH, "//a[@href='/enfaseweb/CTE/Relatorio']"))
    print("Login no Enfase realizado com sucesso.")

def consulta_cte_enfase(driver, cte: str) -> bool:
    """Preenche os dados do CTE, executa a consulta e clica em download."""
    print("-" * 50)
    print(f"Iniciando consulta para o CTE: {cte}")
    
    cte_clean = cte.replace("-", "").strip().upper()
    if len(cte_clean) < 4:
        print(f"AVISO: CTE '{cte}' parece inválido. Pulando.")
        return True

    cte_sem_filial = cte_clean[3:]
    filial_cte = cte_clean[:3]

    try:
        campo_cte = utilidades.wait_until_present(driver, (By.ID, "CTE"))
        campo_cte.send_keys(Keys.CONTROL + "a")
        campo_cte.send_keys(cte_sem_filial)

        serie_input = utilidades.wait_until_present(driver, (By.ID, "SerieCTE"))
        serie_input.send_keys("0000")
        
        driver.find_element(By.ID, "Filial").send_keys(filial_cte + Keys.ENTER)
        utilidades.wait_and_click(driver, (By.ID, "btnLocalizar"))
        print(f"Consulta para o CTE {cte} realizada.")
        
        try:
            utilidades.wait_and_click(driver, (By.CSS_SELECTOR, "a[title='Download']"), timeout=3)
            print("Download do PDF iniciado.")
            return True 
        except TimeoutException:
            print(f"FALHA: Botão de download para o CTE {cte} não foi encontrado.")
            return False
            
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a consulta do CTE {cte}: {e}")
        return True

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
    
    lista_de_ctes = [cte.strip() for cte in re.split(r'[,\s\n]+', raw_input) if cte.strip()]
    return lista_de_ctes

# --- BLOCO DE EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    user_enfase = "6360955"
    pwd_enfase = "fedex0955"
    user_lms = "eriksb"
    pwd_lms = "1234fedex.2025"
    user_tivit = "jessica.infante"
    pwd_tivit = "#We05je06"

    #Configuração pasta de download
    path_desktop = gerenciador_arquivos.obter_path_desktop()
    PASTA_CTES = os.path.join(path_desktop, "ctes")
    os.makedirs(PASTA_CTES, exist_ok=True)  
    print(f"Pasta de destino configurada para: {PASTA_CTES}")

    lista_de_ctes = obter_lista_ctes()
    ctes_nao_encontrados = []

    if not lista_de_ctes:
        print("Nenhum CTE inserido. Encerrando o programa.")
    else:
        print(f"\n{len(lista_de_ctes)} CTEs para processar. Iniciando automação...")
        driver = utilidades.get_driver(PASTA_CTES) # Define a pasta de download
        
        # Gerenciadores de abas
        aba_enfase = driver.current_window_handle
        aba_lms, lms_logado = None, False
        aba_tivit, tivit_logado = None, False
        
        #----------------------ENFASE-------------------------------#
        try:
            login_enfase(driver, user_enfase, pwd_enfase)
            
            for cte_atual in lista_de_ctes:
                driver.switch_to.window(aba_enfase)

                # ETAPA 1: Tentar encontrar no ENFASE
                if consulta_cte_enfase(driver, cte=cte_atual):
                    print("Aguardando download do Enfase...")
                    caminho_pdf = gerenciador_arquivos.encontrar_ultimo_pdf_baixado(PASTA_CTES)
                    if caminho_pdf:
                        gerenciador_arquivos.renomear_pdf_pela_nf(caminho_pdf)
                    time.sleep(1)
                    continue  # SUCESSO: Pula para o próximo CTE

                # Se chegou aqui, não encontrou no Enfase.
                print(f"CTE {cte_atual} não encontrado no Enfase. Verificando no LMS...")

                # ETAPA 2: Tentar encontrar no LMS
                # Gerencia a aba e o login do LMS
                if not aba_lms:
                    abas_antes = set(driver.window_handles)
                    driver.execute_script("window.open('');")
                    aba_lms = (set(driver.window_handles) - abas_antes).pop()
                    driver.switch_to.window(aba_lms)
                    login_lms(driver, user_lms, pwd_lms)
                    consulta_sim(driver)
                    lms_logado = True
                else:
                    # Para os próximos CTEs, apenas troca de aba e volta para a consulta
                    driver.switch_to.window(aba_lms)
                    rerun_consulta(driver)

                # Executa a consulta no LMS (apenas uma vez) e processa o resultado
                caminhos_pdfs_lms = consulta_lms(driver, cte_atual, PASTA_CTES)
                if caminhos_pdfs_lms:
                    print(f"PDF(s) extraído(s) do LMS para o CTE {cte_atual}.")
                    for pdf_path in caminhos_pdfs_lms:
                        gerenciador_arquivos.renomear_pdf_pela_nf(pdf_path)
                    time.sleep(1)
                    continue  

                # Se chegou aqui, não encontrou no LMS.
                print(f"CTE {cte_atual} não encontrado no LMS. Verificando no Tivit...")

                # ETAPA 3: Tentar encontrar no TIVIT
                # Gerencia a aba e o login do Tivit
                if not aba_tivit:
                    abas_antes = set(driver.window_handles)
                    driver.execute_script("window.open('');")
                    aba_tivit = (set(driver.window_handles) - abas_antes).pop()
                    driver.switch_to.window(aba_tivit)
                    login_tivit(driver, user_tivit, pwd_tivit)
                    navegar_para_consulta_tivit(driver)
                    tivit_logado = True
                else:
                    driver.switch_to.window(aba_tivit)

                # Executa a consulta no Tivit (apenas uma vez) e processa o resultado
                caminho_pdf_tivit = consulta_tivit(driver, cte_atual, PASTA_CTES)
                if caminho_pdf_tivit:
                    print(f"PDF baixado do Tivit para o CTE {cte_atual}.")
                    gerenciador_arquivos.renomear_pdf_pela_nf(caminho_pdf_tivit)
                    time.sleep(1)
                    continue  # SUCESSO: Pula para o próximo CTE

                # ETAPA 4: FALHA FINAL
                # Se chegou até aqui, o CTE não foi encontrado em nenhum sistema.
                print(f"ATENÇÃO: CTE {cte_atual} não encontrado em nenhum dos sistemas.")
                ctes_nao_encontrados.append(cte_atual)

                time.sleep(1)
                time.sleep(2) # Pausa entre CTEs para evitar sobrecarga   
        except Exception as e:
            print(f"Ocorreu um erro fatal no script: {e}")
            #----------------------FINALIZAÇÃO-------------------------------#CJR789263
        finally:
            print("\n" + "="*50)
            print("--- PROCESSO FINALIZADO ---")
            if ctes_nao_encontrados:
                print(f"\nATENÇÃO: {len(ctes_nao_encontrados)} CTE(s) não foram encontrados para download:")
                for cte in ctes_nao_encontrados:
                    print(f" - {cte}")
            else:
                print("\nTodos os CTEs foram processados com sucesso!")
            print("="*50)