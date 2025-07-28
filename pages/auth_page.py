# pages/auth_page.py
import pyotp
from playwright.sync_api import Page
from utils.base_test import BaseTest
from utils.logger import logger

class AuthPage:
    URL = "https://godex.io/sign-in"
    
    # Локаторы для формы входа
    EMAIL_INPUT = 'input[name="email"]'
    PASSWORD_INPUT = 'input[name="password"]'
    LOGIN_BTN = 'button:has-text("Log in")'
    
    # Локаторы для 2FA
    TWOFA_CONTAINER = 'div.gdx-2-step-verification'
    TWOFA_INPUT = 'input[name="code 2-fa"]'
    TWOFA_CONFIRM_BTN = 'button.form-verification-code__btn-yes:has-text("Confirm")'

    def __init__(self, page: Page):
        self.page = page
        self.base = BaseTest(page)

    def login_without_2fa(self, email: str, password: str) -> None:
        """
        Вход без 2FA. Ожидает переход на страницу транзакций.
        
        Args:
            email (str): Email пользователя
            password (str): Пароль пользователя
        """
        logger.info(f"Вход без 2FA для пользователя: {email}")
        
        # Открытие страницы логина (использует улучшенный open_url из base_test)
        self.base.open_url(self.URL, timeout=60000)
        
        # Заполнение формы
        self.base.fill_input(self.EMAIL_INPUT, email)
        self.base.fill_input(self.PASSWORD_INPUT, password)
        
        # Клик по кнопке Log in
        self.base.click(self.LOGIN_BTN)
        
        # Ожидание перехода на страницу транзакций
        try:
            self.page.wait_for_url("https://godex.io/stats/transactions", timeout=15000)
            logger.info(f"Успешный вход. Текущий URL: {self.page.url}")
        except TimeoutError:
            current_url = self.page.url
            logger.error(f"Не удалось перейти на страницу транзакций. Текущий URL: {current_url}")
            raise AssertionError(f"Ожидался переход на /dashboard/transactions, но URL стал: {current_url}")

    def login_with_2fa(self, email: str, password: str, secret: str) -> None:
        """
        Вход с 2FA. Ожидает переход на страницу транзакций после подтверждения 2FA.
        
        Args:
            email (str): Email пользователя
            password (str): Пароль пользователя
            secret (str): Секретный ключ 2FA
        """
        logger.info(f"Вход с 2FA для пользователя: {email}")
        
        # Открытие страницы логина (использует улучшенный open_url из base_test)
        self.base.open_url(self.URL, timeout=60000)
        
        # Заполнение формы
        self.base.fill_input(self.EMAIL_INPUT, email)
        self.base.fill_input(self.PASSWORD_INPUT, password)
        
        # Клик по кнопке Log in
        self.base.click(self.LOGIN_BTN)
        
        # Ожидание появления 2FA-попапа
        logger.info("Ожидание появления 2FA-попапа...")
        try:
            self.page.wait_for_selector(self.TWOFA_CONTAINER, timeout=15000, state="visible")
            logger.info("2FA-попап появился")
        except TimeoutError:
            raise AssertionError("2FA-попап не появился за 15 секунд")
        
        # Генерация и ввод 2FA-кода
        code = pyotp.TOTP(secret).now()
        logger.info(f"Сгенерирован 2FA-код: {code}")
        
        # Ввод кода
        try:
            self.page.fill(self.TWOFA_INPUT, code)
            logger.info("2FA-код введен")
        except Exception as e:
            logger.warning(f"Ошибка при вводе кода через fill(): {e}")
            # Альтернативный способ через JS
            self.page.eval_on_selector(self.TWOFA_INPUT, """
                (el, value) => {
                    el.value = value;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }""", code)
            logger.info("2FA-код введен через JS")
        
        # Клик по кнопке подтверждения
        self.base.click(self.TWOFA_CONFIRM_BTN)
        
        # Ожидание перехода на страницу транзакций
        try:
            self.page.wait_for_url("https://godex.io/stats/transactions", timeout=20000)
            logger.info("Успешный вход с 2FA. Переход на страницу транзакций")
            # Ожидание полной загрузки страницы
            self.page.wait_for_load_state("networkidle", timeout=10000)
            logger.info("Страница транзакций полностью загружена")
        except TimeoutError:
            current_url = self.page.url
            raise AssertionError(f"Не удалось перейти на страницу транзакций после 2FA. Текущий URL: {current_url}")