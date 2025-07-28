# tests/test_enable_2fa_flow.py
import pytest
import pyotp
from pages.auth_page import AuthPage
from pages.profile_page import ProfilePage
from utils.logger import logger
from utils.helpers import take_screenshot

@pytest.mark.usefixtures("page")
def test_enable_2fa_flow(
    auth_page: AuthPage,
    profile_page: ProfilePage,
    creds: tuple[str, str],
    base
):
    email, pwd = creds
    logger.info("=== START test_enable_2fa_flow ===")
    
    # 1. Логин без 2FA
    auth_page.login_without_2fa(email, pwd)
    
    # 2. Переход в профиль (со страницы транзакций через клик по кнопке Profile)
    logger.info("Переход на страницу профиля через клик по кнопке Profile")
    profile_page.go_to_profile_from_transactions()
    take_screenshot(base.page, "before_enable_2fa")
    
    # 3. Проверка начального состояния (2FA выключена)
    logger.info("Проверка начального состояния - 2FA должен быть выключен")
    assert profile_page.base.is_element_visible(ProfilePage.ENABLE_BTN), "Кнопка Enable должна быть видна при выключенном 2FA"
    logger.info("2FA действительно выключен - кнопка Enable видна")
    
    # 4. Включение 2FA
    logger.info("Включение 2FA")
    secret = profile_page.enable_2fa()
    take_screenshot(base.page, "after_enable_click")
    
    if not secret:
        pytest.fail("Секрет 2FA не был сгенерирован")
    
    logger.info(f"Сгенерирован секрет 2FA: {secret}")
    
    # 5. Подтверждение включения 2FA
    code = pyotp.TOTP(secret).now()
    logger.info(f"Подтверждение 2FA кодом: {code}")
    profile_page.confirm_enable_2fa(code)
    take_screenshot(base.page, "after_confirm_enable")
    
    # 6. Проверка, что 2FA включена (кнопка Disable видна и блок с включенным 2FA отображен)
    logger.info("Проверка, что 2FA включена")
    assert profile_page.base.is_element_visible(ProfilePage.DISABLE_BTN), "Кнопка Disable должна быть видна после включения 2FA"
    assert profile_page.base.is_element_visible(ProfilePage.TWOFA_ENABLED_BLOCK), "Блок с включенным 2FA должен быть отображен"
    logger.info("2FA успешно включена - кнопка Disable видна и блок с включенным 2FA отображен")
    
    # 7. Сохраняем секрет для последующих тестов
    import os
    path = os.path.join(os.getcwd(), "last_twofa_secret.txt")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(secret)
        logger.info(f"Секрет 2FA сохранен в {path}")
    except Exception as e:
        logger.warning(f"Не удалось сохранить секрет 2FA: {e}")
    
    logger.info("=== END test_enable_2fa_flow ===")