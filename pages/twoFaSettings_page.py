from playwright.sync_api import Page
from utils.base_test import BaseTest

class TwoFaSettingsPage:
    URL = "https://godex.io/dashboard/profile"

    ENABLE_BTN = 'button:has-text("Enable")'
    DISABLE_BTN = 'button:has-text("Disable")'
    SECRET_TEXT = 'p.key-manually'

    ENABLE_OTP_INPUT = 'input.form-verification-code__input[placeholder="Verification Code"]'
    CONFIRM_ENABLE_BTN = 'div.gdx-2-step-verification button:has-text("Enable")'

    DISABLE_PASSWORD_INPUT = 'input[name="password"]'
    DISABLE_OTP_INPUT = 'input[name="verification code"]'
    CONFIRM_DISABLE_BTN = 'button.gdx-gray-card__form-btn:has-text("Disable")'

    def __init__(self, page: Page):
        self.page = page
        self.base = BaseTest(page)

    def go_to_profile_enable(self) -> None:
        """Перейти в профиль и дождаться кнопки Enable (2FA выключен)."""
        self.base.open_url(self.URL, wait_until="networkidle", timeout=60000)
        self.base.wait_for_element(self.ENABLE_BTN, timeout=10000)

    def enable(self) -> str:
        """Нажать Enable, дождаться появления секрета и вернуть его."""
        self.base.click(self.ENABLE_BTN)
        self.base.wait_for_element(self.SECRET_TEXT, timeout=10000)
        return self.page.locator(self.SECRET_TEXT).inner_text().strip()

    def confirm_enable(self, code: str) -> None:
        """Ввести код в попапе Enable и дождаться появления Disable."""
        self.base.fill_input(self.ENABLE_OTP_INPUT, code)
        self.base.click(self.CONFIRM_ENABLE_BTN)
        self.base.wait_for_element(self.DISABLE_BTN, timeout=10000)

    def go_to_profile_disable(self) -> None:
        """Перейти в профиль и дождаться кнопки Disable (2FA включен)."""
        self.base.open_url(self.URL, wait_until="networkidle", timeout=60000)
        # Ждем полной загрузки
        self.page.wait_for_load_state("networkidle", timeout=10000)
        # Небольшая пауза для обновления UI
        self.page.wait_for_timeout(2000)
        # Ждем кнопку Disable
        self.base.wait_for_element(self.DISABLE_BTN, timeout=15000)

    def disable(self, password: str, code: str) -> None:
        """Ввести пароль+код и подождать появления Enable (кнопка Disable уже нажата)."""
        # Ждем появления полей ввода
        self.base.wait_for_element(self.DISABLE_PASSWORD_INPUT, timeout=10000)
        self.base.wait_for_element(self.DISABLE_OTP_INPUT, timeout=10000)
        
        # Вводим данные
        self.base.fill_input(self.DISABLE_PASSWORD_INPUT, password)
        self.base.fill_input(self.DISABLE_OTP_INPUT, code)
        
        # Нажимаем Confirm
        self.base.click(self.CONFIRM_DISABLE_BTN)
        
        # Ждем появления кнопки Enable
        self.base.wait_for_element(self.ENABLE_BTN, timeout=15000)