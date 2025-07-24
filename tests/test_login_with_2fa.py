import pytest
import pyotp
from pages.auth_page import AuthPage
from utils.logger import logger

@pytest.mark.usefixtures("page")
def test_login_with_2fa(
    auth_page: AuthPage,
    creds: tuple[str, str],
    saved_twofa_secret: str
):
    """
    Проверяем, что с включённой 2FA можно войти
    """
    email, pwd = creds
    secret = saved_twofa_secret

    logger.info("=== START test_login_with_2fa ===")
    logger.info(f"Using email: {email}")
    logger.info(f"Using secret: {secret}")
    
    try:
        totp = pyotp.TOTP(secret)
        test_code = totp.now()
        logger.info(f"Test TOTP code: {test_code}")
    except Exception as e:
        pytest.fail(f"Invalid 2FA secret: {e}")
    
    auth_page.login_with_2fa(email, pwd, secret)

    current_url = auth_page.page.url
    logger.info(f"Final URL: {current_url}")
    
    # Проверяем конкретный URL
    if "/stats/transactions" not in current_url:
        # Даем еще немного времени
        auth_page.page.wait_for_timeout(2000)
        current_url = auth_page.page.url
        logger.info(f"URL after additional wait: {current_url}")
        
        if "/stats/transactions" not in current_url:
            logger.error(f"Expected /stats/transactions, got: {current_url}")
            pytest.fail("Не перешли на /stats/transactions после 2FA")
    
    logger.info("=== END test_login_with_2fa ===")