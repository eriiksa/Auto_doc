Este é um aplicativo desenvolvido em Python para otimizar e acelerar a busca,o download de documentos de transporte (CTES) e renomeação dos arquivos pelo número da NF.

A ferramenta foi criada para eliminar a necessidade de consultar manualmente cada sistema, processando uma lista de documentos de forma automática e organizada.

## 💻 Instalação
   https://github.com/eriiksa/Auto_doc/releases/download/v1.2.0/AutoDoc.exe
   * Baixe o app pelo link acima e execute-o com um duplo clique, em cerca de 20s o app será iniciado.
   * Caso haja alguma dificuldade com o download / instalação do app, me contate pelo teams: erik.sa@fedex.com

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
    * Ao final do processo, uma lista dos documentos que não foram baixados estarão em um .txt na pasta **"ctes"**

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3
* **Automação Web:** Selenium
* **Interface Gráfica:** Tkinter 
* **Leitura de PDF:** PyMuPDF
* **OCR:** Tesseract (via `pytesseract`)
* **Armazenamento Seguro de Senhas:** Keyring
* **Empacotamento:** PyInstaller

---
