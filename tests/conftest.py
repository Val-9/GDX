import os
import pytest
import pyotp
from dotenv import load_dotenv
from typing import Generator
from playwright.sync_api import sync_playwright, Playwright, Browser, BrowserContext, Page
from pages.auth_page import AuthPage
from pages.twoFaSettings_page import TwoFaSettingsPage
from pages.navbar import Navbar
from utils.base_test import BaseTest
from utils.helpers import take_screenshot
from pytest_html import extras
from utils.logger import logger

load_dotenv(override=True)

@pytest.fixture(scope="session")
def creds() -> tuple[str, str]:
    email = os.getenv("EMAIL", "")
    pwd   = os.getenv("PASSWORD", "")
    if not email or not pwd:
        pytest.skip("UI-тесты пропущены: EMAIL/PASSWORD не заданы в .env")
    return email, pwd

@pytest.fixture(scope="session")
def pw() -> Generator[Playwright, None, None]:
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(pw: Playwright) -> Generator[Browser, None, None]:
    browser = pw.chromium.launch(headless=False, slow_mo=50)
    yield browser
    browser.close()

@pytest.fixture(scope="function")
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    ctx = browser.new_context()
    yield ctx
    ctx.close()

@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    pg = context.new_page()
    yield pg
    pg.close()

@pytest.fixture(scope="function")
def base(page: Page) -> BaseTest:
    return BaseTest(page)

@pytest.fixture(scope="function")
def auth_page(page: Page) -> AuthPage:
    return AuthPage(page)

@pytest.fixture(scope="function")
def twofa_page(page: Page) -> TwoFaSettingsPage:
    return TwoFaSettingsPage(page)

@pytest.fixture(scope="function")
def navbar(page: Page) -> Navbar:
    return Navbar(page)

# Улучшенная фикстура для работы с 2FA - теперь с функциональным scope
@pytest.fixture(scope="function")
def setup_2fa(auth_page: AuthPage, twofa_page: TwoFaSettingsPage, creds: tuple[str, str]) -> str:
    """
    Фикстура для настройки 2FA в рамках одного теста.
    Возвращает секрет и автоматически очищает состояние после теста.
    """
    email, pwd = creds
    secret = None
    
    # Выполняем настройку 2FA
    auth_page.full_login(email, pwd)
    twofa_page.go_to_profile_enable()
    secret = twofa_page.enable()
    
    # Сохраняем секрет для отладки
    path = os.path.join(os.getcwd(), "last_twofa_secret.txt")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(secret)
        logger.info(f"2FA secret saved to {path}")
    except Exception as e:
        logger.warning(f"Failed to save 2FA secret: {e}")
    
    # Подтверждаем включение
    code = pyotp.TOTP(secret).now()
    twofa_page.confirm_enable(code)
    
    yield secret
    
    # Автоматическая очистка после теста
    try:
        # Отключаем 2FA после теста
        twofa_page.go_to_profile_disable()
        disable_code = pyotp.TOTP(secret).now()
        twofa_page.disable(pwd, disable_code)
        logger.info("2FA disabled after test")
    except Exception as e:
        logger.warning(f"Failed to disable 2FA after test: {e}")

# Безопасная фикстура для чтения сохраненного секрета
@pytest.fixture(scope="session")
def saved_twofa_secret() -> str:
    path = os.path.join(os.getcwd(), "last_twofa_secret.txt")
    if not os.path.exists(path):
        pytest.skip("Файл last_twofa_secret.txt не найден — сначала запустите тест с настройкой 2FA")
    try:
        with open(path, "r", encoding="utf-8") as f:
            secret = f.read().strip()
        if not secret:
            pytest.skip("Секрет 2FA пуст — проверьте содержимое last_twofa_secret.txt")
        return secret
    except Exception as e:
        pytest.skip(f"Ошибка при чтении секрета 2FA: {e}")

# Улучшенная обработка скриншотов
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    page = item.funcargs.get("page")
    if not page or rep.when != "call":
        return
    
    try:
        if rep.failed:
            take_screenshot(page, f"{item.name}_failure")
            logger.error(f"Test {item.name} failed, screenshot taken")
        elif rep.passed:
            take_screenshot(page, f"{item.name}_success")
            logger.info(f"Test {item.name} passed, screenshot taken")
    except Exception as e:
        logger.warning(f"Failed to take screenshot: {e}")

@pytest.hookimpl(optionalhook=True)
def pytest_html_report_title(report):
    report.title = "Godex UI-Tests Report"

@pytest.hookimpl(optionalhook=True)
def pytest_html_results_summary(prefix, summary, postfix):
    prefix.extend([extras.html("<h2>Стоит проверить:</h2>")])