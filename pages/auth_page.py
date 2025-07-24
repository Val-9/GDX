import pyotp
from playwright.sync_api import Page
from utils.base_test import BaseTest
from utils.logger import logger

class AuthPage:
    URL = "https://godex.io/sign-in"
    EMAIL_SELECTOR = 'input[name="email"]'
    PASSWORD_SELECTOR = 'input[name="password"]'
    LOGIN_BTN = 'button:has-text("Log in")'

    TWOFA_CONTAINER = 'div.gdx-2-step-verification'
    TWOFA_INPUT = 'input[name="code 2-fa"]'  # Исправленный селектор
    TWOFA_CONFIRM_BTN = 'button.form-verification-code__btn-yes:has-text("Confirm")'

    def __init__(self, page: Page):
        self.page = page
        self.base = BaseTest(page)

    def go_to_sign_in(self) -> None:
        logger.info("Открытие страницы логина")
        self.base.open_url(self.URL, wait_until="networkidle", timeout=60000)

    def login(self, email: str, password: str) -> None:
        assert email, "Email не задан"
        assert password, "Password не задан"
        self.base.fill_input(self.EMAIL_SELECTOR, email)
        self.base.fill_input(self.PASSWORD_SELECTOR, password)

    def submit_login(self) -> None:
        # Нажать Log in и дождаться либо редиректа на профиль, либо появления попапа 2FA
        self.base.click(self.LOGIN_BTN)
        try:
            self.page.wait_for_url("**/dashboard/**", timeout=8000)
        except:
            self.base.wait_for_element(self.TWOFA_CONTAINER, timeout=10000)

    def confirm_2fa(self, code: str) -> None:
        # Заполнить поле через JS и подтвердить
        self.base.wait_for_element(self.TWOFA_CONTAINER, timeout=10000)
        self.base.wait_for_element(self.TWOFA_INPUT, timeout=10000)
        self.page.eval_on_selector(
            self.TWOFA_INPUT,
            """
            (el, value) => {
                el.value = value;
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
            """,
            code
        )
        actual = self.page.eval_on_selector(self.TWOFA_INPUT, "el => el.value")
        if actual != code:
            raise AssertionError(f"2FA-код не ввёлся: в поле '{actual}' вместо '{code}'")
        self.base.click(self.TWOFA_CONFIRM_BTN)
        # Ждем закрытия попапа или редиректа
        try:
            self.page.wait_for_selector(self.TWOFA_CONTAINER, state="detached", timeout=10000)
        except:
            self.page.wait_for_url("**/dashboard/**", timeout=10000)

    def full_login(self, email: str, password: str) -> None:
        self.go_to_sign_in()
        self.login(email, password)
        self.submit_login()

    def login_with_2fa(self, email: str, password: str, secret: str) -> None:
        """
        1) Открыть /sign-in
        2) Ввести email/password и нажать Log in
        3) Подождать только 2FA-попап
        4) Заполнить в нём код TOTP(secret) и нажать Confirm
        5) Дождаться закрытия попапа и редиректа
        """
        logger.info(f"Starting 2FA login for {email}")
        
        # 1-2. Открываем страницу и заполняем форму
        self.go_to_sign_in()
        self.login(email, password)
        
        # 3. Нажимаем Log in и ждем появления 2FA-попапа
        self.base.click(self.LOGIN_BTN)
        
        logger.info("Waiting for 2FA popup to appear...")
        try:
            self.page.wait_for_selector(self.TWOFA_CONTAINER, timeout=15000, state="visible")
            logger.info("2FA popup appeared successfully")
        except TimeoutError:
            current_url = self.page.url
            logger.info(f"No 2FA popup, current URL: {current_url}")
            if "/dashboard" in current_url or "/stats" in current_url:
                logger.info("Already redirected, 2FA might not be enabled")
                # Ждем загрузки страницы
                self.page.wait_for_load_state("networkidle", timeout=15000)
                return
            raise AssertionError("Попап 2FA не появился за 15 секунд")

        # 4. Генерируем и вводим 2FA код
        code = pyotp.TOTP(secret).now()
        logger.info(f"Generated 2FA code: {code}")
        
        self.page.wait_for_timeout(500)
        
        try:
            self.page.fill(self.TWOFA_INPUT, code)
            logger.info("2FA code filled successfully")
        except Exception as e:
            logger.warning(f"Standard fill failed: {e}, trying JS method")
            self.page.eval_on_selector(self.TWOFA_INPUT, """
                (el, value) => {
                    el.value = value;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }""", code)
            logger.info("2FA code filled via JS method")

        # 5. Нажимаем Confirm и ждем редиректа
        logger.info("Clicking Confirm button...")
        self.base.click(self.TWOFA_CONFIRM_BTN)
        
        # Ждем редиректа на stats/transactions
        try:
            logger.info("Waiting for redirect to stats/transactions...")
            # Ждем конкретный URL
            self.page.wait_for_url("**/stats/transactions", timeout=20000)
            logger.info("Successfully redirected to stats/transactions")
            # Ждем полной загрузки страницы
            self.page.wait_for_load_state("networkidle", timeout=10000)
            logger.info("Page fully loaded")
        except TimeoutError:
            # Если точный URL не сработал, пробуем более общий паттерн
            try:
                self.page.wait_for_url("**/stats/**", timeout=10000)
                logger.info("Redirected to stats page")
                self.page.wait_for_load_state("networkidle", timeout=10000)
            except TimeoutError:
                # Проверяем текущий URL
                current_url = self.page.url
                logger.info(f"Current URL after confirm: {current_url}")
                
                # Ждем немного и проверяем снова
                self.page.wait_for_timeout(3000)
                current_url = self.page.url
                logger.info(f"URL after waiting: {current_url}")
                
                if "/stats/transactions" not in current_url:
                    raise AssertionError(f"Failed to redirect to stats/transactions. Current URL: {current_url}")