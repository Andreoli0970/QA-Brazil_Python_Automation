from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class UrbanRoutesPage:
    """
    Page Object central. Mapeia seletores e provê métodos de interação.
    Observação: alguns seletores usam XPaths “tolerantes” para se adaptar a variações
    comuns do app (id/name/placeholder/aria-label). Caso seu app tenha atributos
    específicos (data-testid, etc.), ajuste aqui.
    """

    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

        # ====== Rotas (From / To) ======
        self.FROM_INPUT = (By.XPATH, '//input[@id="from" or @name="from" or @placeholder="From" or @placeholder="De" or contains(@aria-label,"From")]')
        self.TO_INPUT = (By.XPATH, '//input[@id="to" or @name="to" or @placeholder="To" or @placeholder="Para" or contains(@aria-label,"To")]')
        self.SUGGESTION_FIRST = (By.XPATH, '(//li[contains(@class,"suggest") or contains(@class,"item") or contains(@class,"autocomplete")] | //div[contains(@class,"suggest")]/*)[1]')

        # ====== Tarifas ======
        # Um container de tarifas onde clicamos por texto (Comfort, Economy, etc.)
        self.TARIFF_CONTAINER = (By.XPATH, '//*[contains(@class,"tariff") or contains(@class,"Tariff") or contains(@class,"rate")]')
        # Item selecionado (classe com "selected")
        self.TARIFF_SELECTED = (By.XPATH, '//*[contains(@class,"tariff") and contains(@class,"selected")]')

        # ====== Telefone / SMS ======
        self.PHONE_OPEN = (By.XPATH, '//*[self::button or self::a][contains(translate(.,"PHONEFONE","phonefone"), "phone") or contains(., "Telefone") or contains(@data-test,"phone")]')
        self.PHONE_INPUT = (By.XPATH, '//input[contains(@type,"tel") or @id="phone" or contains(@name,"phone")]')
        self.PHONE_NEXT = (By.XPATH, '//button[contains(.,"Next") or contains(.,"Avançar") or contains(.,"Confirm") or contains(.,"Continue")]')
        self.SMS_CODE_INPUTS = (By.XPATH, '//input[contains(@name,"code") or contains(@id,"code") or @inputmode="numeric" or @type="tel" or @maxlength="1"]')
        self.SMS_CONFIRM = (By.XPATH, '//button[contains(.,"Confirm") or contains(.,"OK") or contains(.,"Done")]')
        self.PHONE_CONFIRMED_BADGE = (By.XPATH, '//*[contains(., "Phone confirmed") or contains(., "Telefone confirmado") or contains(@class,"phone-confirmed")]')

        # ====== Pagamento / Cartão ======
        self.PAYMENT_OPEN = (By.XPATH, '//*[self::button or self::div or self::a][contains(., "Payment") or contains(., "Pagamento") or contains(@data-test,"payment")]')
        self.CARD_ADD_BUTTON = (By.XPATH, '//*[self::button or self::a][contains(., "Add card") or contains(., "Adicionar cartão")]')
        self.CARD_NUMBER_INPUT = (By.XPATH, '//input[contains(@placeholder,"Card") or contains(@name,"card") or @id="number"]')
        self.CARD_CODE_INPUT = (By.XPATH, '//input[contains(@placeholder,"CVC") or contains(@placeholder,"CVV") or contains(@name,"cvc") or contains(@name,"cvv") or contains(@id,"code")]')
        self.CARD_SAVE = (By.XPATH, '//button[contains(.,"Save") or contains(.,"Adicionar") or contains(.,"Salvar")]')
        self.CARD_MASKED = (By.XPATH, '//*[contains(@class,"card") and (contains(., "****") or contains(., "••••"))]')

        # ====== Mensagem ao motorista ======
        self.DRIVER_MESSAGE_INPUT = (By.XPATH, '//textarea | //input[contains(@placeholder,"Message") or contains(@placeholder,"Mensagem") or contains(@name,"message")]')

        # ====== Opções (cobertor / lenços) ======
        self.OPTION_BLANKET = (By.XPATH, '//*[self::label or self::button or self::div][contains(., "Blanket") or contains(., "Cobertor")]')
        self.OPTION_HANDKERCHIEF = (By.XPATH, '//*[self::label or self::button or self::div][contains(., "Handkerchief") or contains(., "Lenço") or contains(., "Lenços")]')
        self.OPTION_SELECTED_MARK = (By.XPATH, '//*[contains(@class,"selected") or contains(@class,"active")][.//*[contains(., "Blanket") or contains(., "Cobertor") or contains(., "Handkerchief") or contains(., "Lenço")]]')

        # ====== Sorvetes (contador) ======
        # Considera um item com texto "Ice cream" e um botão + próximo
        self.ICE_CREAM_PLUS = (By.XPATH, '(//*[contains(., "Ice cream") or contains(., "Sorvete")]//following::*[self::button or self::div][contains(@class,"plus") or contains(@class,"increment")])[1]')
        self.ICE_CREAM_COUNT = (By.XPATH, '(//*[contains(., "Ice cream") or contains(., "Sorvete")]//following::*[contains(@class,"count") or self::span or self::div][1])')

        # ====== Pedido / Popup de busca ======
        self.ORDER_BUTTON = (By.XPATH, '//button[contains(.,"Order") or contains(.,"Pedir") or contains(.,"Solicitar")]')
        self.SEARCHING_POPUP = (By.XPATH, '//*[contains(., "Searching for a car") or contains(., "Buscando") or contains(@class,"searching")]')

    # ---------- utilidades ----------
    def _clear_and_type(self, locator, text):
        el = self.wait.until(EC.element_to_be_clickable(locator))
        el.clear()
        el.send_keys(text)

    def _click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def _wait_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    # ---------- rotas ----------
    def set_route(self, address_from: str, address_to: str):
        self._clear_and_type(self.FROM_INPUT, address_from)
        # seleciona a 1ª sugestão
        try:
            self._click(self.SUGGESTION_FIRST)
        except Exception:
            pass

        self._clear_and_type(self.TO_INPUT, address_to)
        try:
            self._click(self.SUGGESTION_FIRST)
        except Exception:
            pass

    def get_from(self) -> str:
        return self._wait_visible(self.FROM_INPUT).get_attribute("value") or ""

    def get_to(self) -> str:
        return self._wait_visible(self.TO_INPUT).get_attribute("value") or ""

    # ---------- tarifa ----------
    def choose_tariff(self, name: str):
        # Clica no item de tarifa pelo texto
        xpath = f'//*[contains(@class,"tariff") or contains(@class,"rate")][.//*[contains(., "{name}")]]'
        self._click((By.XPATH, xpath))

    def get_selected_tariff_text(self) -> str:
        try:
            el = self._wait_visible(self.TARIFF_SELECTED)
            return el.text.strip()
        except Exception:
            # fallback: tenta capturar por atributo aria-selected
            el = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@aria-selected="true" and (contains(@class,"tariff") or contains(@class,"rate"))]')))
            return el.text.strip()

    # ---------- telefone / sms ----------
    def open_phone_modal(self):
        self._click(self.PHONE_OPEN)

    def fill_phone_and_request_code(self, phone: str):
        self._clear_and_type(self.PHONE_INPUT, phone)
        self._click(self.PHONE_NEXT)

    def submit_sms_code(self, code: str):
        # Muitos apps usam vários inputs (um por dígito)
        inputs = self.driver.find_elements(*self.SMS_CODE_INPUTS)
        if inputs:
            for i, ch in enumerate(code.strip()):
                if i < len(inputs):
                    inputs[i].clear()
                    inputs[i].send_keys(ch)
        else:
            # fallback: um campo só
            self._clear_and_type(self.SMS_CODE_INPUTS, code)

        # Confirmar
        try:
            self._click(self.SMS_CONFIRM)
        except Exception:
            pass

    def is_phone_confirmed(self) -> bool:
        try:
            self._wait_visible(self.PHONE_CONFIRMED_BADGE)
            return True
        except Exception:
            return False

    # ---------- pagamento / cartão ----------
    def open_payment(self):
        self._click(self.PAYMENT_OPEN)

    def add_card(self, number: str, code: str):
        # Alguns fluxos têm botão "Add card" antes de inputs
        try:
            self._click(self.CARD_ADD_BUTTON)
        except Exception:
            pass
        self._clear_and_type(self.CARD_NUMBER_INPUT, number)
        self._clear_and_type(self.CARD_CODE_INPUT, code)
        try:
            self._click(self.CARD_SAVE)
        except Exception:
            pass

    def get_masked_card_text(self) -> str:
        try:
            return self._wait_visible(self.CARD_MASKED).text.strip()
        except Exception:
            return ""

    # ---------- mensagem ----------
    def set_driver_message(self, message: str):
        self._clear_and_type(self.DRIVER_MESSAGE_INPUT, message)
        # Confirma com TAB/ENTER se necessário
        try:
            self.driver.switch_to.active_element.send_keys(Keys.TAB)
        except Exception:
            pass

    def get_driver_message(self) -> str:
        el = self._wait_visible(self.DRIVER_MESSAGE_INPUT)
        value = el.get_attribute("value")
        return (value or el.text or "").strip()

    # ---------- opções ----------
    def toggle_blanket(self):
        self._click(self.OPTION_BLANKET)

    def toggle_handkerchief(self):
        self._click(self.OPTION_HANDKERCHIEF)

    def is_any_option_selected(self) -> bool:
        try:
            self._wait_visible(self.OPTION_SELECTED_MARK)
            return True
        except Exception:
            return False

    # ---------- sorvetes ----------
    def add_ice_creams(self, count: int):
        for _ in range(max(0, count)):
            self._click(self.ICE_CREAM_PLUS)

    def get_ice_creams_count_text(self) -> str:
        try:
            return self._wait_visible(self.ICE_CREAM_COUNT).text.strip()
        except Exception:
            return ""

    # ---------- pedido / popup ----------
    def click_order(self):
        self._click(self.ORDER_BUTTON)

    def is_searching_popup_visible(self) -> bool:
        try:
            self._wait_visible(self.SEARCHING_POPUP)
            return True
        except Exception:
            return False 