import keyring

SERVICE_NAME_PREFIX = "AutomationApp"
SERVICES = ["Enfase", "LMS", "Tivit"]

def save_credentials(service, username, password):
    """Salva as credenciais de um serviço específico no Cofre do Windows."""
    service_id = f"{SERVICE_NAME_PREFIX}_{service}"
    try:
        keyring.set_password(service_id, username, password)
        print(f"Credenciais para {service} salvas com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao salvar credenciais para {service}: {e}")
        return False

def load_credentials(service):
    """Carrega as credenciais de um serviço. Retorna (username, password) ou (None, None)."""
    service_id = f"{SERVICE_NAME_PREFIX}_{service}"
    try:
        stored_combo = keyring.get_password(service_id, service) # Usamos o nome do serviço como username fixo
        if stored_combo and "|||" in stored_combo:
            username, password = stored_combo.split("|||", 1)
            return username, password
        return None, None
    except Exception as e:
        print(f"Erro ao carregar credenciais para {service}: {e}")
        return None, None

def check_all_credentials_exist():
    """Verifica se as credenciais para todos os serviços estão salvas."""
    for service in SERVICES:
        user, pwd = load_credentials(service)
        if not user or not pwd:
            return False
    return True