import time
import data
from helpers import create_chrome_driver, get_sms_code_from_logs
from selenium.webdriver.common.by import By
from pages import UrbanRoutesPage

class TestUrbanRoutes:
    driver = None
    page: UrbanRoutesPage = None

    @classmethod
    def setup_class(cls):
        # Inicializa o driver com logging para capturar o código do SMS
        cls.driver = create_chrome_driver(performance_logging=True)
        # Wait implícito
        cls.driver.implicitly_wait(5)

    @classmethod
    def teardown_class(cls):
        if cls.driver:
            cls.driver.quit()

    def _open(self):
        self.driver.get(data.URBAN_ROUTES_URL)
        self.page = UrbanRoutesPage(self.driver)

    # ========== TESTE 1: Definir rota ==========
    def test_01_set_route(self):
        self._open()
        self.page.set_route(data.ADDRESS_FROM, data.ADDRESS_TO)
        assert self.page.get_from() == data.ADDRESS_FROM
        assert self.page.get_to() == data.ADDRESS_TO

    # ========== TESTE 2: Selecionar tarifa ==========
    def test_02_select_tariff(self):
        # Assume que a rota já está preenchida do teste anterior (mesma sessão)
        self.page.choose_tariff(data.TARIFF_NAME)
        selected = self.page.get_selected_tariff_text()
        assert data.TARIFF_NAME.lower() in selected.lower()

    # ========== TESTE 3: Cadastrar telefone e confirmar por SMS ==========
    def test_03_register_phone(self):
        self.page.open_phone_modal()
        self.page.fill_phone_and_request_code(data.PHONE_NUMBER)

        # Dá um tempo para a API responder e o log capturar
        time.sleep(2)

        sms_code = get_sms_code_from_logs(self.driver)
        assert sms_code is not None, "Não foi possível capturar o código SMS pelos logs."
        self.page.submit_sms_code(sms_code)
        assert self.page.is_phone_confirmed(), "Telefone não foi confirmado visualmente."

    # ========== TESTE 4: Adicionar cartão ==========
    def test_04_add_card(self):
        self.page.open_payment()
        self.page.add_card(data.CARD_NUMBER, data.CARD_CODE)
        masked = self.page.get_masked_card_text()
        # Verifica se os últimos dígitos do cartão aparecem mascarados corretamente
        assert any(end in masked for end in [data.CARD_NUMBER[-4:], data.CARD_NUMBER.replace(" ", "")[-4:]])

    # ========== TESTE 5: Mensagem para o motorista ==========
    def test_05_message_for_driver(self):
        self.page.set_driver_message(data.MESSAGE_FOR_DRIVER)
        assert data.MESSAGE_FOR_DRIVER in self.page.get_driver_message()

    # ========== TESTE 6: Seleção de opções (cobertor, lenços) ==========
    def test_06_options_selection(self):
        self.page.toggle_blanket()
        self.page.toggle_handkerchief()
        assert self.page.is_any_option_selected(), "Nenhuma opção ficou marcada."

    # ========== TESTE 7: Adição de sorvetes ==========
    def test_07_add_ice_creams(self):
        self.page.add_ice_creams(data.ICE_CREAMS_COUNT)
        count_text = self.page.get_ice_creams_count_text()
        # aceita número “2”, “x2”, etc.
        assert any(str(data.ICE_CREAMS_COUNT) in s for s in [count_text, count_text.replace("x", "")])

    # ========== TESTE 8: Verificação do popup de busca ==========
    def test_08_search_popup(self):
        self.page.click_order()
        assert self.page.is_searching_popup_visible(), "Popup de busca não apareceu após clicar em Order." 