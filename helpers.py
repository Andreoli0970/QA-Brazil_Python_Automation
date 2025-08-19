import json
import re
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def create_chrome_driver(performance_logging: bool = True):
    """
    Cria e retorna um ChromeDriver com opções recomendadas e, se desejado,
    logging de performance habilitado para capturar o código SMS.
    """
    options = Options()
    if performance_logging:
        # Habilita logs de performance (CDP) p/ capturar SMS pelo network
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    # Inicia maximizado para evitar problemas de click
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def get_sms_code_from_logs(driver, pattern: str = r'(?<!\d)\d{4,6}(?!\d)') -> Optional[str]:
    """
    Percorre os logs de performance do Chrome (CDP) procurando por respostas de rede
    que contenham um código numérico (4 a 6 dígitos). Ajuste o regex se sua API
    retornar o código em outro formato.
    """
    try:
        logs = driver.get_log("performance")
    except Exception:
        logs = []

    code_regex = re.compile(pattern)

    # Primeiro, tenta capturar de JSON bruto nos logs
    for entry in logs:
        try:
            message = entry.get("message", "")
            data = json.loads(message)
        except Exception:
            continue

        msg = data.get("message", {})
        method = msg.get("method", "")
        params = msg.get("params", {})

        # Heurísticas: urls ou bodies relacionadas a verificação/sms/otp
        if method == "Network.responseReceived":
            res = params.get("response", {})
            url = res.get("url", "")
            if any(key in url.lower() for key in ["sms", "otp", "verify", "code"]):
                # Tenta puxar o body via CDP (pode falhar dependendo do site)
                request_id = params.get("requestId")
                if request_id:
                    try:
                        body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                        content = body.get("body", "")
                        m = code_regex.search(content)
                        if m:
                            return m.group(0)
                    except Exception:
                        # segue procurando
                        pass

        # Plano B: tenta achar números diretamente no conteúdo do log
        m2 = code_regex.search(json.dumps(params))
        if m2:
            return m2.group(0)

    # Não achou
    return None 