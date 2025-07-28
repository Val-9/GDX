# conftest.py
import os
import pytest
import pyotp
from dotenv import load_dotenv
from typing import Generator
from playwright.sync_api import sync_playwright, Playwright, Browser, BrowserContext, Page
from pages.auth_page import AuthPage
from pages.main_page import MainPage
from pages.profile_page import ProfilePage
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
def main_page(page: Page) -> MainPage:
    return MainPage(page)

@pytest.fixture(scope="function")
def profile_page(page: Page) -> ProfilePage:
    return ProfilePage(page)

@pytest.fixture(scope="function")
def navbar(page: Page) -> Navbar:
    return Navbar(page)

# Улучшенная фикстура для работы с 2FA - теперь с функциональным scope
@pytest.fixture(scope="function")
def setup_2fa(auth_page: AuthPage, profile_page: ProfilePage, creds: tuple[str, str]) -> str:
    """
    Фикстура для настройки 2FA в рамках одного теста.
    Возвращает секрет и автоматически очищает состояние после теста.
    """
    email, pwd = creds
    secret = None

    try:
        # 1. Выполняем вход без 2FA
        auth_page.full_login(email, pwd)

        # 2. Переходим на страницу профиля
        profile_page.navigate_to()

        # 3. Включаем 2FA и получаем секрет
        secret = profile_page.enable_2fa()

        # 4. Сохраняем секрет для отладки и использования другими тестами
        path = os.path.join(os.getcwd(), "last_twofa_secret.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(secret)
        logger.info(f"2FA secret saved to {path}")

        # 5. Подтверждаем включение 2FA
        code = pyotp.TOTP(secret).now()
        profile_page.confirm_enable_2fa(code)

        logger.info("2FA enabled via setup_2fa fixture")

    except Exception as e:
        logger.error(f"Failed to setup 2FA in fixture: {e}")
        pytest.fail(f"2FA setup failed: {e}")

    # --- Передача значения секрета в тест ---
    yield secret
    # --- Конец передачи значения ---

    # --- Автоматическая очистка (отключение 2FA) после теста ---
    try:
        logger.info("Attempting to disable 2FA after test (teardown)")
        # Для отключения 2FA нужен код TOTP и пароль
        if secret: # Убедимся, что секрет был создан
            disable_code = pyotp.TOTP(secret).now()
            profile_page.disable_2fa(pwd, disable_code) # Используем обновлённый метод
            logger.info("2FA disabled after test (teardown successful)")
        else:
            logger.warning("2FA secret was not generated, skipping disable teardown")
    except Exception as e:
        logger.warning(f"Failed to disable 2FA after test (teardown failed): {e}")
        # Не вызываем pytest.fail здесь, чтобы не маскировать ошибку основного теста
    # --- Конец автоматической очистки ---

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
