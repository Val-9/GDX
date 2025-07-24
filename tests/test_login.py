import os
import pytest
from utils.helpers import take_screenshot
from utils.logger import logger


def test_login_success(auth_page, base, page, creds):
    email, password = creds
    logger.info("=== Начало теста: test_login_success ===")
    try:
        auth_page.go_to_sign_in()
        auth_page.login(email, password)
        base.click('button:has-text("Log in")')
        # TODO: добавить проверку успешного входа
    except Exception as e:
        take_screenshot(page, "login_failure")
        logger.error(f"Ошибка во время теста: {e}")
        raise
    finally:
        logger.info("=== Конец теста: test_login_success ===")