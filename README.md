Este é um aplicativo de automação de processos (RPA) desenvolvido em Python para otimizar e acelerar a busca e o download de documentos de transporte (como Conhecimentos de Transporte Eletrônico - CTEs) a partir de múltiplos portais web.

A ferramenta foi criada para eliminar a necessidade de consultar manualmente cada sistema, processando uma lista de documentos de forma automática e organizada.

## ✨ Funcionalidades Principais

* **Interface Gráfica Amigável:** Possui uma interface simples criada com Tkinter, permitindo que qualquer usuário cole uma lista de documentos e inicie o processo com um clique.
* **Consulta em Múltiplos Sistemas:** Realiza uma busca sequencial e inteligente em três portais web diferentes (Enfase, LMS e Tivit). Se um documento é encontrado no primeiro portal, o software o processa e avança para o próximo item da lista, economizando tempo.
* **Renomeação Automática de Arquivos:** Utiliza tecnologia de Reconhecimento Óptico de Caracteres (OCR) com Tesseract para ler o conteúdo do PDF baixado, encontrar o número da Nota Fiscal (NF) e renomear o arquivo de forma inteligente.
* **Gerenciamento Seguro de Credenciais:** As senhas de acesso aos portais não ficam expostas no código. Elas são salvas de forma segura no Cofre de Credenciais do Windows, e o aplicativo possui uma aba de "Configurações" para gerenciá-las.
* **Controle de Execução:** A interface permanece responsiva durante a automação, exibindo o status atual e permitindo que o usuário interrompa o processo a qualquer momento através do botão "Parar Automação".
* **Executável Simples:** O projeto é compilado em um único arquivo `.exe` com PyInstaller, eliminando a necessidade de instalar Python ou qualquer biblioteca nas máquinas dos usuários.

## 🚀 Como Usar (Versão `.exe`)

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
