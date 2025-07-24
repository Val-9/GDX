import pytest
import pyotp
from pages.auth_page import AuthPage
from pages.twoFaSettings_page import TwoFaSettingsPage
from pages.navbar import Navbar
from utils.logger import logger

@pytest.mark.usefixtures("page")
def test_2fa_full_flow(
    auth_page: AuthPage,
    navbar: Navbar,
    twofa_page: TwoFaSettingsPage,
    creds: tuple[str, str]
):
    email, pwd = creds
    logger.info("=== START test_2fa_full_flow ===")

    # 1–3) Обычный логин
    auth_page.full_login(email, pwd)

    # 4–6) Включаем 2FA
    twofa_page.open()
    secret = twofa_page.enable()
    code = pyotp.TOTP(secret).now()
    twofa_page.confirm_enable(code)
    assert twofa_page.page.locator(TwoFaSettingsPage.DISABLE_BTN).is_visible()

    # 7) Логаут
    navbar.logout()

    # 8–11) Логин с 2FA
    auth_page.full_login(email, pwd)
    auth_page.confirm_2fa(pyotp.TOTP(secret).now())

    # 12–16) Отключаем 2FA
    twofa_page.open()
    twofa_page.disable(pwd, pyotp.TOTP(secret).now())
    assert twofa_page.page.locator(TwoFaSettingsPage.ENABLE_BTN).is_visible()

    logger.info("=== END test_2fa_full_flow ===")
