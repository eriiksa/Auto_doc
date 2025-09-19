# main.py
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
import tkinter as tk
from interface import AutomationGUI


def login_enfase(driver, user_enfase, pwd_enfase):
    driver.get("https://enfase.lac.fedex.com/enfaseweb/")
    utilidades.wait_until_present(driver, (By.ID, "Login")).send_keys(user_enfase)
    driver.find_element(By.ID, "Password").send_keys(pwd_enfase + Keys.ENTER)
    utilidades.wait_and_click(driver, (By.XPATH, "//button[contains(text(),'Consulta')]"))
    utilidades.wait_and_click(driver, (By.XPATH, "//a[@href='/enfaseweb/CTE/Relatorio']"))

def consulta_cte_enfase(driver, cte: str) -> bool:
    cte_clean = cte.replace("-", "").strip().upper()
    if len(cte_clean) < 4: return True
    cte_sem_filial, filial_cte = cte_clean[3:], cte_clean[:3]
    try:
        campo_cte = utilidades.wait_until_present(driver, (By.ID, "CTE"))
        campo_cte.send_keys(Keys.CONTROL + "a"); campo_cte.send_keys(cte_sem_filial)
        utilidades.wait_until_present(driver, (By.ID, "SerieCTE")).send_keys("0000")
        driver.find_element(By.ID, "Filial").send_keys(filial_cte + Keys.ENTER)
        utilidades.wait_and_click(driver, (By.ID, "btnLocalizar"))
        try:
            utilidades.wait_and_click(driver, (By.CSS_SELECTOR, "a[title='Download']"), timeout=3)
            return True 
        except TimeoutException: return False
    except Exception: return True

def run_automation_logic(ctes_raw, stop_event, status_queue, creds):
    user_enfase, pwd_enfase = creds['Enfase']
    user_lms, pwd_lms = creds['LMS']
    user_tivit, pwd_tivit = creds['Tivit']
    
    path_desktop = gerenciador_arquivos.obter_path_desktop()
    PASTA_CTES = os.path.join(path_desktop, "ctes")
    os.makedirs(PASTA_CTES, exist_ok=True)
    status_queue.put(f'Pasta de destino: "{PASTA_CTES}"')

    lista_de_ctes = [cte.strip() for cte in re.split(r'[,\s\n]+', ctes_raw) if cte.strip()]
    ctes_nao_encontrados = []
    driver = None

    try:
        status_queue.put("Iniciando navegador...")
        driver = utilidades.get_driver(PASTA_CTES)
        
        aba_enfase = driver.current_window_handle
        aba_lms, lms_logado = None, False
        aba_tivit, tivit_logado = None, False
        
        status_queue.put("Realizando login no Enfase...")
        login_enfase(driver, user_enfase, pwd_enfase)
        
        for i, cte_atual in enumerate(lista_de_ctes):
            if stop_event.is_set():
                status_queue.put("Automação interrompida pelo usuário.")
                break
            
            status_queue.put(f"Processando {i+1}/{len(lista_de_ctes)}: {cte_atual} no Enfase...")
            driver.switch_to.window(aba_enfase)

            if consulta_cte_enfase(driver, cte=cte_atual):
                caminho_pdf = gerenciador_arquivos.encontrar_ultimo_pdf_baixado(PASTA_CTES)
                if caminho_pdf: gerenciador_arquivos.renomear_pdf_pela_nf(caminho_pdf)
                time.sleep(1); continue

            if stop_event.is_set(): break
            status_queue.put(f"{cte_atual} não encontrado no Enfase. Verificando LMS...")
            
            if not aba_lms:
                abas_antes = set(driver.window_handles); driver.execute_script("window.open('');")
                aba_lms = (set(driver.window_handles) - abas_antes).pop()
                driver.switch_to.window(aba_lms)
                status_queue.put("Realizando login no LMS...")
                login_lms(driver, user_lms, pwd_lms); consulta_sim(driver)
                lms_logado = True
            else:
                driver.switch_to.window(aba_lms); rerun_consulta(driver)
            
            caminhos_pdfs_lms = consulta_lms(driver, cte_atual, PASTA_CTES)
            if caminhos_pdfs_lms:
                for pdf_path in caminhos_pdfs_lms: gerenciador_arquivos.renomear_pdf_pela_nf(pdf_path)
                time.sleep(1); continue

            if stop_event.is_set(): break
            status_queue.put(f"{cte_atual} não encontrado no LMS. Verificando Tivit...")

            if not aba_tivit:
                abas_antes = set(driver.window_handles); driver.execute_script("window.open('');")
                aba_tivit = (set(driver.window_handles) - abas_antes).pop()
                driver.switch_to.window(aba_tivit)
                status_queue.put("Realizando login no Tivit...")
                login_tivit(driver, user_tivit, pwd_tivit); navegar_para_consulta_tivit(driver)
                tivit_logado = True
            else:
                driver.switch_to.window(aba_tivit)

            caminho_pdf_tivit = consulta_tivit(driver, cte_atual, PASTA_CTES)
            if caminho_pdf_tivit:
                gerenciador_arquivos.renomear_pdf_pela_nf(caminho_pdf_tivit)
                time.sleep(1); continue

            status_queue.put(f"ATENÇÃO: {cte_atual} não encontrado em nenhum sistema.")
            ctes_nao_encontrados.append(cte_atual)
            time.sleep(1)

    except Exception as e:
        status_queue.put(f"ERRO FATAL: {e}")
    finally:
        if driver: driver.quit()
        # Envia o resultado para a GUI processar
        resultado_final = ":".join(ctes_nao_encontrados)
        status_queue.put(f"RESULT:{resultado_final}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AutomationGUI(root, start_callback=run_automation_logic)
    root.mainloop()