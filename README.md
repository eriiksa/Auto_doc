Este é um aplicativo de automação de processos (RPA) desenvolvido em Python para otimizar e acelerar a busca e o download de documentos de transporte (como Conhecimentos de Transporte Eletrônico - CTEs) a partir de múltiplos portais web.

A ferramenta foi criada para eliminar a necessidade de consultar manualmente cada sistema, processando uma lista de documentos de forma automática e organizada.

https://github.com/eriiksa/download_doc/releases/download/v1.0.0/Auto.doc.exe

Para instalar, baixe o app e clique duas vezes no Auto doc.exe, em cerca de 20s ele abrirá e você pode seguir esse passo a passo.

## 🚀 Como Usar

1.  **Primeiro Uso - Configuração:**
    * Ao abrir o aplicativo pela primeira vez, uma mensagem solicitará a configuração das credenciais.
    * Vá para a aba **"Configurações"**.
    * Preencha o login e a senha para cada um dos três sistemas: **Enfase**, **LMS** e **Tivit**.
    * Clique em **"Salvar Credenciais"**. Você só precisa fazer isso uma vez.

2.  **Realizando uma Consulta:**
    * Vá para a aba **"Consulta de CTEs"**.
    * Cole a lista de números de documentos no campo de texto. Eles podem ser separados por quebra de linha, espaço ou vírgula.
    * Clique no botão **"Iniciar Automação"**.
    * Acompanhe o progresso na barra de status na parte inferior da janela.

3.  **Resultados:**
    * Os documentos encontrados serão baixados e renomeados automaticamente.
    * Todos os arquivos serão salvos em uma pasta chamada **"ctes"**, localizada na sua Área de Trabalho (Desktop).
    * Ao final do processo, uma mensagem exibirá um resumo dos documentos que não foram encontrados em nenhum dos portais.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3
* **Automação Web:** Selenium
* **Interface Gráfica:** Tkinter 
* **Leitura de PDF:** PyMuPDF
* **OCR:** Tesseract (via `pytesseract`)
* **Armazenamento Seguro de Senhas:** Keyring
* **Empacotamento:** PyInstaller

---
