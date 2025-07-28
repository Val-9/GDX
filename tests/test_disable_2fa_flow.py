# tests/test_disable_2fa_flow.py
import pytest
import pyotp
from pages.auth_page import AuthPage
from pages.profile_page import ProfilePage
from utils.logger import logger
from utils.helpers import take_screenshot

@pytest.mark.usefixtures("page")
def test_disable_2fa_flow(
    auth_page: AuthPage,
    profile_page: ProfilePage,
    saved_twofa_secret: str,
    creds: tuple[str, str],
    base
):
    email, pwd = creds
    secret = saved_twofa_secret
    
    logger.info("=== START test_disable_2fa_flow ===")
    
    # 1. Логин с 2FA
    auth_page.login_with_2fa(email, pwd, secret)
    
    # 2. Переход в профиль
    logger.info("Переход на страницу профиля")
    profile_page.navigate_to()
    take_screenshot(base.page, "before_disable_2fa")
    
    # 3. Проверка начального состояния (2FA включена)
    logger.info("Проверка начального состояния - 2FA должен быть включен")
    assert profile_page.base.is_element_visible(ProfilePage.DISABLE_BTN), "Кнопка Disable должна быть видна при включенном 2FA"
    assert profile_page.base.is_element_visible(ProfilePage.TWOFA_ENABLED_BLOCK), "Блок с включенным 2FA должен быть отображен"
    logger.info("2FA действительно включен - кнопка Disable видна и блок с включенным 2FA отображен")
    
    # 4. Отключение 2FA
    code = pyotp.TOTP(secret).now()
    logger.info(f"Отключение 2FA с кодом: {code}")
    profile_page.disable_2fa(pwd, code)
    take_screenshot(base.page, "after_disable_2fa")
    
    # 5. Проверка, что 2FA отключена (кнопка Enable видна и блок с выключенным 2FA отображен)
    logger.info("Проверка, что 2FA отключена")
    assert profile_page.base.is_element_visible(ProfilePage.ENABLE_BTN), "Кнопка Enable должна быть видна после отключения 2FA"
    assert profile_page.base.is_element_visible(ProfilePage.TWOFA_DISABLED_BLOCK), "Блок с выключенным 2FA должен быть отображен"
    logger.info("2FA успешно отключена - кнопка Enable видна и блок с выключенным 2FA отображен")
    
    logger.info("=== END test_disable_2fa_flow ===")