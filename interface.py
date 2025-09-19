# interface.py
import tkinter as tk
from tkinter import scrolledtext, messagebox, font, ttk
import threading
import queue
import gerenciador_credenciais 

class AutomationGUI:
    def __init__(self, root, start_callback):
        self.root = root
        self.start_callback = start_callback
        self.stop_event = threading.Event()
        self.status_queue = queue.Queue()
        self.setup_ui()
        self.check_initial_config()

    def setup_ui(self):
        self.root.title("Automação de Consulta de CTEs")
        self.root.geometry("480x520")

        # --- Cria o sistema de Abas ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        # --- Aba 1: Consulta ---
        self.tab_consulta = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_consulta, text='Consulta de CTEs')
        self.create_consulta_tab()

        # --- Aba 2: Configurações ---
        self.tab_config = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_config, text='Configurações')
        self.create_config_tab()

        self.root.eval('tk::PlaceWindow . center')

    def create_consulta_tab(self):
        label = tk.Label(self.tab_consulta, text="Cole a lista de CTEs abaixo (um por linha):")
        label.pack(pady=(0, 5), anchor="w")
        self.text_area = scrolledtext.ScrolledText(self.tab_consulta, wrap=tk.WORD, height=15, width=50)
        self.text_area.pack(pady=5, fill=tk.BOTH, expand=True)
        info_font = font.Font(family="Arial", size=10)
        info_label = tk.Label(self.tab_consulta, text='Aviso: Os arquivos serão salvos na pasta "ctes" na sua Área de Trabalho.', fg="black",font=info_font)
        info_label.pack(pady=(5, 10), anchor="w")
        button_frame = tk.Frame(self.tab_consulta)
        button_frame.pack(fill=tk.X)
        self.start_button = tk.Button(button_frame, text="Iniciar Automação", command=self.start_automation, font=("Arial", 10, "bold"), bg="#4CAF50", fg="white")
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        self.stop_button = tk.Button(button_frame, text="Parar Automação", command=self.stop_automation, font=("Arial", 10, "bold"), bg="#f44336", fg="white", state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
        self.status_label = tk.Label(self.tab_consulta, text="Status: Aguardando início", bd=1, relief=tk.SUNKEN, anchor="w", padx=5)
        self.status_label.pack(fill=tk.X, pady=(10, 0))

    def create_config_tab(self):
        # --- Cria os campos para cada serviço ---
        self.entries = {}
        for service in gerenciador_credenciais.SERVICES:
            frame = tk.LabelFrame(self.tab_config, text=f"Credenciais {service}", padx=10, pady=10)
            frame.pack(fill=tk.X, pady=5)
            
            tk.Label(frame, text="Login:").grid(row=0, column=0, sticky="w", pady=2)
            user_entry = tk.Entry(frame, width=30)
            user_entry.grid(row=0, column=1, sticky="ew")

            tk.Label(frame, text="Senha:").grid(row=1, column=0, sticky="w", pady=2)
            pass_entry = tk.Entry(frame, show="*", width=30)
            pass_entry.grid(row=1, column=1, sticky="ew")
            
            self.entries[service] = (user_entry, pass_entry)
            frame.columnconfigure(1, weight=1)

        # --- Botão de Salvar e Status ---
        save_button = tk.Button(self.tab_config, text="Salvar Credenciais", command=self.save_all_credentials)
        save_button.pack(pady=10)
        self.config_status_label = tk.Label(self.tab_config, text="")
        self.config_status_label.pack()

        self.load_credentials_to_form()

    def save_all_credentials(self):
        try:
            for service, (user_entry, pass_entry) in self.entries.items():
                username = user_entry.get()
                password = pass_entry.get()
                if username and password:
                    # Combina "user|||pass" para salvar no keyring
                    combo = f"{username}|||{password}"
                    gerenciador_credenciais.keyring.set_password(f"{gerenciador_credenciais.SERVICE_NAME_PREFIX}_{service}", service, combo)
            self.config_status_label.config(text="Credenciais salvas com sucesso!", fg="green")
            self.root.after(3000, lambda: self.config_status_label.config(text=""))
        except Exception as e:
            self.config_status_label.config(text=f"Erro ao salvar: {e}", fg="red")

    def load_credentials_to_form(self):
        for service, (user_entry, pass_entry) in self.entries.items():
            user, pwd = gerenciador_credenciais.load_credentials(service)
            if user:
                user_entry.delete(0, tk.END); user_entry.insert(0, user)
            if pwd:
                pass_entry.delete(0, tk.END); pass_entry.insert(0, pwd)

    def check_initial_config(self):
        if not gerenciador_credenciais.check_all_credentials_exist():
            messagebox.showwarning("Configuração Necessária", 
                                   "É a sua primeira vez usando o app ou faltam credenciais. Por favor, preencha e salve suas informações na aba 'Configurações'.")
            self.notebook.select(self.tab_config) # Muda para a aba de configurações
    
    def start_automation(self):
        # Verifica as credenciais antes de iniciar
        if not gerenciador_credenciais.check_all_credentials_exist():
            self.check_initial_config()
            return
            
        ctes_raw = self.text_area.get("1.0", tk.END).strip()
        if not ctes_raw:
            messagebox.showerror("Erro", "A lista de CTEs não pode estar vazia.")
            return

        self.start_button.config(state=tk.DISABLED); self.stop_button.config(state=tk.NORMAL)
        self.text_area.config(state=tk.DISABLED)
        self.stop_event.clear()

        # Carrega as credenciais para passar para a thread
        creds = {s: gerenciador_credenciais.load_credentials(s) for s in gerenciador_credenciais.SERVICES}

        threading.Thread(target=self.start_callback, args=(ctes_raw, self.stop_event, self.status_queue, creds)).start()
        self.root.after(100, self.check_queue)
    
    # ... (o resto das funções: stop_automation, check_queue, reset_ui, show_result permanecem as mesmas de antes)
    def stop_automation(self):
        self.status_label.config(text="Status: Parando automação... Aguarde o CTE atual.")
        self.stop_event.set()
        self.stop_button.config(state=tk.DISABLED)

    def check_queue(self):
        try:
            message = self.status_queue.get_nowait()
            if message == "DONE": self.reset_ui()
            elif message.startswith("RESULT"):
                _, *data = message.split(":", 1)
                ctes_nao_encontrados = data[0].split(',') if data and data[0] else []
                self.reset_ui(); self.show_result(ctes_nao_encontrados)
            else: self.status_label.config(text=f"Status: {message}")
        except queue.Empty: pass
        finally: self.root.after(100, self.check_queue)

    def reset_ui(self):
        self.start_button.config(state=tk.NORMAL); self.stop_button.config(state=tk.DISABLED)
        self.text_area.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Processo finalizado. Pronto para iniciar.")

    def show_result(self, ctes_nao_encontrados):
        if not ctes_nao_encontrados: messagebox.showinfo("Processo Finalizado", "Todos os CTEs foram processados com sucesso!")
        else:
            quantidade = len(ctes_nao_encontrados)
            termo_cte = "CTE não foi encontrado" if quantidade == 1 else "CTEs não foram encontrados"
            mensagem = f"{quantidade} {termo_cte} para download:\n\n" + "\n".join([f" - {cte}" for cte in ctes_nao_encontrados])
            messagebox.showwarning("Processo Finalizado com Avisos", mensagem)