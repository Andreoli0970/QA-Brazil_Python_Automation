# helpers.py
# Este arquivo fornece uma função auxiliar para verificar se a URL do servidor está acessível.
# NÃO MODIFIQUE este arquivo, conforme instruções do projeto.

import requests

def is_url_reachable(url: str, timeout: int = 5) -> bool:
    """
    Retorna True se a URL responder com código 200 dentro do timeout.
    Retorna False em caso de URL vazia, erro de conexão ou status diferente de 200.
    """
    if not url:
        return False
    try:
        resp = requests.get(url, timeout=timeout)
        return resp.status_code == 200
    except Exception:
        return False
      Add helpers.py
