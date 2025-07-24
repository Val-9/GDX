# tests/test_enable_2fa_flow.py

import pytest
import pyotp
from pages.auth_page import AuthPage
from pages.twoFaSettings_page import TwoFaSettingsPage
from utils.logger import logger
from utils.helpers import take_screenshot

@pytest.mark.usefixtures("page")
def test_enable_2fa_flow(
    auth_page: AuthPage,
    twofa_page: TwoFaSettingsPage,
    creds: tuple[str, str],
    base
):
    email, pwd = creds
    logger.info("=== START test_enable_2fa_flow ===")
    
    # 1. Логин без 2FA
    auth_page.full_login(email, pwd)
    
    # 2. Переход в профиль для включения 2FA
    logger.info("Navigating to profile to enable 2FA")
    twofa_page.go_to_profile_enable()
    take_screenshot(base.page, "before_enable_2fa")
    
    # 3. Включение 2FA
    logger.info("Enabling 2FA")
    secret = twofa_page.enable()
    take_screenshot(base.page, "after_enable_click")
    
    if not secret:
        pytest.fail("2FA secret was not generated")
    
    logger.info(f"Generated 2FA secret: {secret}")
    
    # 4. Подтверждение включения 2FA
    code = pyotp.TOTP(secret).now()
    logger.info(f"Confirming 2FA with code: {code}")
    twofa_page.confirm_enable(code)
    take_screenshot(base.page, "after_confirm_enable")
    
    # 5. Проверка, что 2FA включена (кнопка Disable видна)
    logger.info("Verifying 2FA is enabled")
    try:
        twofa_page.page.wait_for_selector(TwoFaSettingsPage.DISABLE_BTN, state="visible", timeout=15000)
        logger.info("2FA successfully enabled - Disable button is visible")
    except Exception as e:
        logger.error(f"Failed to verify 2FA enable: {e}")
        raise AssertionError("Disable button should be visible after enabling 2FA")
    
    # 6. Сохраняем секрет для последующих тестов
    import os
    path = os.path.join(os.getcwd(), "last_twofa_secret.txt")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(secret)
        logger.info(f"2FA secret saved to {path}")
    except Exception as e:
        logger.warning(f"Failed to save 2FA secret: {e}")
    
    logger.info("=== END test_enable_2fa_flow ===")