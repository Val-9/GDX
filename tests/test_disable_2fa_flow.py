import pytest
import pyotp
from pages.auth_page import AuthPage
from pages.navbar import Navbar
from pages.twoFaSettings_page import TwoFaSettingsPage
from utils.logger import logger
from utils.helpers import take_screenshot  # Импортируем правильно

@pytest.mark.usefixtures("page")
def test_2fa_disable_flow(
    auth_page: AuthPage,
    navbar: Navbar,
    twofa_page: TwoFaSettingsPage,
    saved_twofa_secret: str,
    creds: tuple[str, str],
    base
):
    email, pwd = creds
    secret = saved_twofa_secret
    
    logger.info("=== START test_2fa_disable_flow ===")
    
    # 1. Логин с 2FA
    auth_page.login_with_2fa(email, pwd, secret)
    
    # 2. Переход в профиль для отключения
    logger.info("Navigating to profile to disable 2FA")
    twofa_page.go_to_profile_disable()
    take_screenshot(base.page, "before_disable_2fa")  # Используем правильно
    
    # 3. Отключение 2FA
    code = pyotp.TOTP(secret).now()
    logger.info(f"Disabling 2FA with code: {code}")
    twofa_page.disable(pwd, code)
    take_screenshot(base.page, "after_disable_2fa")  # Используем правильно
    
    # 4. Проверка, что 2FA отключена
    logger.info("Verifying 2FA is disabled")
    try:
        # Ждем появления кнопки Enable
        twofa_page.page.wait_for_selector(TwoFaSettingsPage.ENABLE_BTN, state="visible", timeout=15000)
        logger.info("Enable button is visible - 2FA disabled successfully")
    except Exception as e:
        logger.error(f"Enable button not found: {e}")
        raise AssertionError("Enable button should be visible after disabling 2FA")