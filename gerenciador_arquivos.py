import os
import re
import time
import winreg
from typing import Optional
import fitz  # PyMuPDF
import pytesseract
import io
from PIL import Image

# --- CONFIGURAÇÃO MANUAL DO TESSERACT ---
# Garante que o script encontre o executável do Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def obter_caminho_area_de_trabalho() -> str:
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

def encontrar_ultimo_pdf_baixado(pasta_ctes: str) -> Optional[str]:
    """
    Encontra o PDF mais recente na pasta. Se a pasta não existir, ela é criada.
    """
    os.makedirs(pasta_ctes, exist_ok=True)
    time.sleep(3) # Pequena pausa para o arquivo ser salvo no disco

    arquivos_pdf = [f for f in os.listdir(pasta_ctes) if f.endswith('.pdf')]
    if not arquivos_pdf:
        print("Nenhum arquivo PDF encontrado na pasta de ctes.")
        return None

    caminho_completo = [os.path.join(pasta_ctes, f) for f in arquivos_pdf]
    arquivo_mais_recente = max(caminho_completo, key=os.path.getmtime)
    
    print(f"Arquivo mais recente encontrado: {os.path.basename(arquivo_mais_recente)}")
    return arquivo_mais_recente

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
        match_nf = re.findall(r"NF: [0]*(\d+)", texto_completo_ocr) 
        match_ne = re.findall(r"NE: [0]*(\d+)", texto_completo_ocr) 
        match_decl = re.findall(r"Declaração\s*(\d+)", texto_completo_ocr)
        nfs_juntas = match_nf + match_ne + match_decl
    
        if nfs_juntas:
            nome_arquivo_base = "-".join(nfs_juntas)
            print(f"Números de Documento encontrados: {nome_arquivo_base}")
            
            # Define o novo caminho baseado no nome do arquivo combinado
            diretorio = os.path.dirname(caminho_do_pdf)
            novo_nome = f"{nome_arquivo_base}.pdf"
            novo_caminho = os.path.join(diretorio, novo_nome)
            
            # A lógica de renomeação foi movida para DENTRO deste bloco
            if os.path.exists(novo_caminho):
                print(f"Aviso: Já existe um arquivo chamado '{novo_nome}'.")
            else:
                doc.close()
                doc = None 
                os.rename(caminho_do_pdf, novo_caminho)
                print(f"Arquivo renomeado para '{novo_nome}'")
        else:
            # Este 'else' agora corresponde corretamente ao 'if nfs_juntas'
            print("Nenhum padrão de documento ('NF:', 'NE:' ou 'Declaração') foi encontrado no texto do OCR.")

    except Exception as e:
        print(f"Ocorreu um erro ao processar o PDF com OCR: {e}")
    finally:
        if doc:
            doc.close()