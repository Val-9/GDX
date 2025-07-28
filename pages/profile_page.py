# pages/profile_page.py
from playwright.sync_api import Page
from utils.base_test import BaseTest
from utils.logger import logger

class ProfilePage:
    URL = "https://godex.io/dashboard/profile"

    # Локаторы для навигации
    PROFILE_MENU_ITEM = 'a[href="/dashboard/profile"]'
    TRANSACTIONS_MENU_ITEM = 'a[href="/dashboard/transactions"]'
    
    # Локаторы для кнопок Enable/Disable 2FA
    ENABLE_BTN = 'button.gdx-gray-card__btn-enable:has-text("Enable")'
    DISABLE_BTN = 'button.gdx-gray-card__form-btn:has-text("Disable")'

    # Локаторы для 2FA модального окна
    TWOFA_MODAL = 'div.gdx-2-step-verification'
    SECRET_TEXT = 'p.key-manually'
    ENABLE_OTP_INPUT = 'input.gdx-2-step-verification__code[placeholder="Verification Code"]'
    CONFIRM_ENABLE_BTN = 'div.gdx-2-step-verification button.form-verification-code__btn-yes:has-text("Enable")'

    # Локаторы для отключения 2FA
    DISABLE_PASSWORD_INPUT = 'input[name="password"]'
    DISABLE_OTP_INPUT = 'input[name="verification code"]'
    CONFIRM_DISABLE_BTN = 'button.gdx-gray-card__form-btn:has-text("Disable")'
    
    # Локаторы для проверки состояния 2FA
    TWOFA_ENABLED_BLOCK = 'div.gdx-2-fa-on-off-block:has-text("2-Step Verification is On")'
    TWOFA_DISABLED_BLOCK = 'div.gdx-2-fa-on-off-block:has-text("2-Step Verification is Off")'

    def __init__(self, page: Page):
        self.page = page
        self.base = BaseTest(page)

    def go_to_profile_from_transactions(self) -> None:
        """
        Переход на страницу профиля со страницы транзакций.
        Имитирует реальный пользовательский поток - клик по кнопке Profile в меню.
        """
        logger.info("Клик по кнопке Profile в навигационном меню")
        # Кликаем по ссылке "Profile" в меню
        self.base.click(self.PROFILE_MENU_ITEM)
        
        # Ждем перехода на страницу профиля
        self.page.wait_for_url("**/dashboard/profile", timeout=15000)
        
        # Ждем загрузки страницы профиля
        self.page.wait_for_load_state("networkidle", timeout=10000)
        
        # Ждем появления одной из кнопок 2FA для подтверждения загрузки
        self.page.wait_for_selector(f"{self.ENABLE_BTN}, {self.DISABLE_BTN}", state="visible", timeout=15000)
        
        logger.info("Страница профиля успешно загружена")

    def navigate_to(self) -> None:
        """Прямой переход на страницу профиля по URL."""
        logger.info("Прямой переход на страницу профиля")
        self.base.open_url(self.URL)
        # Дождемся загрузки страницы и появления одной из кнопок 2FA
        self.page.wait_for_selector(f"{self.ENABLE_BTN}, {self.DISABLE_BTN}", state="visible", timeout=15000)
        logger.info("Страница профиля загружена")

    def wait_for_enable_state(self) -> None:
        """Дождаться состояния страницы, когда 2FA можно включить (кнопка Enable видна)."""
        logger.info("Ожидание состояния включения 2FA")
        self.base.wait_for_element(self.ENABLE_BTN, timeout=15000)

    def wait_for_disable_state(self) -> None:
        """Дождаться состояния страницы, когда 2FA включена и можно отключить (кнопка Disable видна)."""
        logger.info("Ожидание состояния отключения 2FA")
        self.base.wait_for_element(self.DISABLE_BTN, timeout=15000)

    def enable_2fa(self) -> str:
        """
        Включить 2FA:
        1. Дождаться кнопки Enable
        2. Нажать кнопку Enable
        3. Дождаться появления QR-кода и секретного ключа
        4. Вернуть секретный ключ
        """
        logger.info("Начало процесса включения 2FA")
        # Шаг 1: Дождаться состояния "можно включить"
        self.wait_for_enable_state()
        
        # Шаг 2: Нажать кнопку Enable
        logger.info("Нажатие кнопки Enable")
        self.base.click(self.ENABLE_BTN)
        
        # Шаг 3: Дождаться модального окна 2FA
        logger.info("Ожидание модального окна 2FA")
        self.base.wait_for_element(self.TWOFA_MODAL, timeout=15000)
        self.base.wait_for_element(self.SECRET_TEXT, timeout=10000)
        
        # Шаг 4: Вернуть секрет
        secret = self.page.locator(self.SECRET_TEXT).inner_text().strip()
        logger.info(f"Секрет 2FA получен: {secret[:10]}...")
        return secret

    def confirm_enable_2fa(self, code: str) -> None:
        """
        Подтвердить включение 2FA:
        1. Ввести код подтверждения
        2. Нажать кнопку Enable в попапе
        3. Дождаться появления кнопки Disable и блока с включенным 2FA
        """
        logger.info(f"Подтверждение включения 2FA с кодом: {code}")
        
        # Ввод кода
        self.base.fill_input(self.ENABLE_OTP_INPUT, code)
        
        # Клик по кнопке подтверждения в попапе
        self.base.click(self.CONFIRM_ENABLE_BTN)
        
        # Дождаться закрытия модального окна
        try:
            self.page.wait_for_selector(self.TWOFA_MODAL, state="detached", timeout=10000)
            logger.info("Модальное окно 2FA закрыто")
        except:
            logger.warning("Модальное окно 2FA не закрылось, продолжаем...")
        
        # Дождаться появления блока с включенным 2FA
        self.base.wait_for_element(self.TWOFA_ENABLED_BLOCK, timeout=15000)
        logger.info("Блок с включенным 2FA отображен")
        
        # Дождаться состояния "2FA включена"
        self.wait_for_disable_state()
        logger.info("2FA успешно включена")

    def initiate_disable_2fa(self) -> None:
        """
        Инициировать процесс отключения 2FA:
        1. Дождаться кнопки Disable
        2. Нажать кнопку Disable
        3. Дождаться появления полей ввода пароля и кода
        """
        logger.info("Начало процесса отключения 2FA")
        # Шаг 1: Дождаться состояния "2FA включена"
        self.wait_for_disable_state()
        
        # Шаг 2: Нажать кнопку Disable
        logger.info("Нажатие кнопки Disable")
        self.base.click(self.DISABLE_BTN)
        
        # Шаг 3: Дождаться полей ввода
        logger.info("Ожидание полей ввода для отключения")
        self.base.wait_for_element(self.DISABLE_PASSWORD_INPUT, timeout=10000)
        self.base.wait_for_element(self.DISABLE_OTP_INPUT, timeout=10000)

    def confirm_disable_2fa(self, password: str, code: str) -> None:
        """
        Подтвердить отключение 2FA:
        1. Ввести пароль и код подтверждения
        2. Нажать кнопку Confirm
        3. Дождаться появления кнопки Enable и блока с выключенным 2FA
        """
        logger.info("Подтверждение отключения 2FA")
        
        # Ввод данных
        self.base.fill_input(self.DISABLE_PASSWORD_INPUT, password)
        self.base.fill_input(self.DISABLE_OTP_INPUT, code)
        
        # Клик по кнопке подтверждения
        self.base.click(self.CONFIRM_DISABLE_BTN)
        
        # Дождаться появления блока с выключенным 2FA
        self.base.wait_for_element(self.TWOFA_DISABLED_BLOCK, timeout=15000)
        logger.info("Блок с выключенным 2FA отображен")
        
        # Дождаться состояния "2FA выключена"
        self.wait_for_enable_state()
        logger.info("2FA успешно отключена")

    # Упрощенный метод для полного цикла отключения (если нужно)
    def disable_2fa(self, password: str, code: str) -> None:
        """
        Полный процесс отключения 2FA:
        1. Инициировать отключение
        2. Подтвердить отключение
        """
        self.initiate_disable_2fa()
        self.confirm_disable_2fa(password, code)