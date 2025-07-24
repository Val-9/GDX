# tests/test_login_negative.py

import pytest
from utils.helpers import take_screenshot, random_sleep
from utils.logger import logger

NEGATIVE_CASES = [
    pytest.param("", "", 
                 "div.gdx-input-error-alert.gdx-alert.type-error", 
                 "Required", id="empty_fields"),
    pytest.param("not-an-email", "ValidPass123!",
                 "div.gdx-gray-card__form-res-alert.gdx-alert.type-error",
                 "Incorrect login or password", id="invalid_email"),
    pytest.param("user@example.com", "wrongPass",
                 "div.gdx-gray-card__form-res-alert.gdx-alert.type-error",
                 "Incorrect login or password", id="wrong_password"),
    pytest.param("user@example.com", "123",
                 "div.gdx-gray-card__form-res-alert.gdx-alert.type-error",
                 "Password must be at least", id="short_password"),
]

@pytest.mark.parametrize(
    "email,password,container_selector,expected_text",
    NEGATIVE_CASES
)
def test_login_negative(
    auth_page, base, page, creds,
    email, password, container_selector, expected_text
):
    logger.info(f"=== CASE {email!r} | {password!r} ===")

    # Сбрасываем форму каждый раз: переходим на /sign-in
    auth_page.go_to_sign_in()
    base.wait_for_element('input[name="email"]')
    random_sleep(0.5, 1.0)

    # Заполняем поля
    base.fill_input('input[name="email"]', email)
    base.fill_input('input[name="password"]', password)

    # Кликаем «Log in» (и ждём /api/login, если отправляется)
    if email or password:
        with page.expect_response(
            lambda r: r.request.method == "POST" and "/api/login" in r.url
        ):
            base.wait_and_click('button:has-text("Log in")')
    else:
        base.wait_and_click('button:has-text("Log in")')

    # Пауза чтобы алерт отрисовался
    random_sleep(1, 1)

    # Проверяем, что появился нужный алерт
    locator = page.locator(f"{container_selector}:has-text(\"{expected_text}\")")
    try:
        locator.wait_for(state="visible", timeout=5_000)
    except Exception:
        take_screenshot(page, f"neg_{email or 'empty'}")
        pytest.fail(
            f"Case [{email!r}|{password!r}]: не дождались ‘{expected_text}’"
        )

    assert locator.is_visible()
    logger.info(f"✅ CASE {email!r} | {password!r} — saw ‘{expected_text}’")
