import os
import re
import time
from typing import Optional, List
import winreg # Windows Registry
import fitz  # PyMuPDF
import pytesseract # OCR
import io 
from PIL import Image # Pillow
import shutil # Mover arquivos 
import zipfile # Manipular Zips para extrair PDFs do lms
import requests # Baixar arquivos via HTTP para o tivit

# --- CONFIGURAÇÃO MANUAL DO TESSERACT ---
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def obter_path_desktop() -> str:
    """
    Lê o Registro do Windows para encontrar o caminho real da Área de Trabalho.
    """
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders')
        desktop_path_raw = winreg.QueryValueEx(key, 'Desktop')[0]
        desktop_path = os.path.expandvars(desktop_path_raw)
        winreg.CloseKey(key)
        return desktop_path
    except FileNotFoundError:
        return os.path.join(os.path.expanduser('~'), 'Desktop')

def verificar_novo_download(pasta_download: str, timestamp_antes: float, timeout: int = 5) -> Optional[str]:
    """Monitora uma pasta por um novo arquivo .zip e retorna seu caminho ou None."""
    print(f"Monitorando '{os.path.basename(pasta_download)}' por um novo arquivo .zip (máx. {timeout}s)...")
    tempo_final = time.time() + timeout
    while time.time() < tempo_final:
        for nome_arquivo in os.listdir(pasta_download):
            if nome_arquivo.lower().endswith('.zip') and not nome_arquivo.lower().endswith('.crdownload'):
                caminho_arquivo = os.path.join(pasta_download, nome_arquivo)
                if os.path.getmtime(caminho_arquivo) > timestamp_antes:
                    print(f"Download confirmado: Novo arquivo '{nome_arquivo}' encontrado.")
                    time.sleep(2)
                    return caminho_arquivo
        time.sleep(1)
    
    print("Nenhum novo arquivo .zip detectado no tempo limite.")
    return None

def encontrar_ultimo_pdf_baixado(pasta_ctes: str) -> Optional[str]:
    """
    Encontra o PDF mais recente na pasta "ctes" no Desktop.
    """
    time.sleep(3) # Pequena pausa para o arquivo ser salvo no disco

    arquivos_pdf = [f for f in os.listdir(pasta_ctes) if f.endswith('.pdf')]
    if not arquivos_pdf:
        print("Nenhum arquivo PDF encontrado na pasta de ctes.")
        return None

    caminho_completo = [os.path.join(pasta_ctes, f) for f in arquivos_pdf]
    arquivo_mais_recente = max(caminho_completo, key=os.path.getmtime)
    
    print(f"Arquivo mais recente encontrado: {os.path.basename(arquivo_mais_recente)}")
    return arquivo_mais_recente

def extrair_e_mover_pdfs_do_zip(caminho_zip: str, pasta_destino: str) -> List[str]:
    """Extrai todos os PDFs de um arquivo .zip para uma pasta de destino e apaga o .zip."""
    caminhos_pdfs_extraidos = []
    try:
        print(f"Extraindo PDFs de '{os.path.basename(caminho_zip)}' para '{os.path.basename(pasta_destino)}'...")
        with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
            for nome_arquivo_no_zip in zip_ref.namelist():
                if nome_arquivo_no_zip.lower().endswith('.pdf'):
                    # Extrai o arquivo para a pasta de destino
                    zip_ref.extract(nome_arquivo_no_zip, pasta_destino)
                    caminho_final_pdf = os.path.join(pasta_destino, os.path.basename(nome_arquivo_no_zip))
                    caminhos_pdfs_extraidos.append(caminho_final_pdf)
                    print(f" - Arquivo '{os.path.basename(nome_arquivo_no_zip)}' extraído.")
        
        # Apaga o arquivo .zip após a extração bem-sucedida
        os.remove(caminho_zip)
        print(f"Arquivo '{os.path.basename(caminho_zip)}' removido.")

    except Exception as e:
        print(f"Ocorreu um erro ao extrair o arquivo zip: {e}")

    return caminhos_pdfs_extraidos

def renomear_pdf_pela_nf(caminho_do_pdf: str):
    """
    Abre o PDF, extrai as imagens e usa pytesseract DIRETAMENTE para
    realizar o OCR e encontrar o número do documento.
    """
    if not caminho_do_pdf or not os.path.exists(caminho_do_pdf):
        print(f"Erro: O arquivo '{caminho_do_pdf}' não foi encontrado para renomear.")
        return

    doc = None
    try:
        for i in range(15):
            try:
                doc = fitz.open(caminho_do_pdf)
                print("PDF aberto com sucesso!")
                break
            except Exception:
                time.sleep(1)
        
        if not doc:
            raise Exception("Não foi possível abrir o arquivo PDF após várias tentativas.")

        texto_completo_ocr = ""
        print("Iniciando extração de imagens e OCR manual...")

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            image_list = page.get_images(full=True)
            
            if not image_list:
                print(f"Nenhuma imagem encontrada na página {page_num + 1}.")
                continue

            print(f"Encontradas {len(image_list)} imagens na página {page_num + 1}. Processando...")

            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))
                texto_da_imagem = pytesseract.image_to_string(image, lang='por', timeout=30)
                texto_completo_ocr += texto_da_imagem + "\n"
        #--------------------DEBUG OCR---------------------------#
        print("\n--- INÍCIO DO TEXTO EXTRAÍDO VIA OCR ---")
        print(texto_completo_ocr)
        print("--- FIM DO TEXTO EXTRAÍDO VIA OCR ---\n")
        #--------------------------------------------------------#
        match = None
        
        #Padrões OCR#
        numeros_nf = re.findall(r"NF: [0]*(\d+)", texto_completo_ocr)
        numeros_ne = re.findall(r"NE: [0]*(\d+)", texto_completo_ocr)
        numeros_decl = re.findall(r"Declaração\s*(\d+)", texto_completo_ocr)
        numeros_fiscais = re.findall(r"Notas Fiscais:?\s*(\d+)", texto_completo_ocr, re.IGNORECASE)
        nfs_juntas = numeros_nf + numeros_ne + numeros_decl + numeros_fiscais

        if nfs_juntas:
            nome_arquivo_base = "-".join(nfs_juntas)
            print(f"Números de Documento encontrados: {nome_arquivo_base}")
            
            diretorio = os.path.dirname(caminho_do_pdf)
            novo_nome = f"{nome_arquivo_base}.pdf"
            novo_caminho = os.path.join(diretorio, novo_nome)
            
            if os.path.exists(novo_caminho):
                print(f"Aviso: Já existe um arquivo chamado '{novo_nome}'. Substituindo o arquivo existente.")
                doc.close()
                doc = None
                os.remove(caminho_do_pdf)
            else:
                doc.close()
                doc = None 
                shutil.move(caminho_do_pdf, novo_caminho)
                print(f"Arquivo renomeado para '{novo_nome}'")
        else:
            print("Nenhum padrão de documento ('NF:', 'NE:' ou 'Declaração') foi encontrado no texto do OCR.")

    except Exception as e:
        print(f"Ocorreu um erro ao processar o PDF com OCR: {e}")
    finally:
        if doc:
            doc.close()
def baixar_pdf_de_url(url_pdf: str, pasta_destino: str, nome_arquivo_base: str) -> Optional[str]:
    """
    Baixa um arquivo PDF a partir de uma URL e o salva na pasta de destino.
    Retorna o caminho do arquivo salvo em caso de sucesso.
    """
    try:
        print(f"Baixando PDF da URL: {url_pdf[:50]}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        resposta = requests.get(url_pdf, headers=headers, timeout=30, verify=False)
        resposta.raise_for_status()

        nome_arquivo_seguro = f"{re.sub(r'[^a-zA-Z0-9-]', '', nome_arquivo_base)}.pdf"
        caminho_completo = os.path.join(pasta_destino, nome_arquivo_seguro)

        with open(caminho_completo, 'wb') as f:
            f.write(resposta.content)
        
        print(f"Arquivo PDF salvo com sucesso em: {caminho_completo}")
        return caminho_completo

    except requests.exceptions.RequestException as e:
        print(f"ERRO: Falha ao baixar o PDF da URL. Erro: {e}")
        return None
