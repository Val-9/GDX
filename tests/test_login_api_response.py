# tests/test_login_api_response.py

import pytest
from utils.logger import logger
from utils.helpers import take_screenshot

def test_login_api_response(auth_page, base, page, creds):
    """
    Проверяем HTTP-статус и тело JSON-ответа на POST https://godex.io/api/login,
    и убеждаемся, что после логина открывается личный кабинет.
    """
    email, password = creds
    logger.info("=== Начало теста: test_login_api_response ===")

    # 1. Переходим на страницу логина и вводим учётные данные
    auth_page.go_to_sign_in()
    auth_page.login(email, password)

    # 2. Ловим запрос и ответ на /api/login
    with page.expect_request(lambda req: req.method == "POST" and "/api/login" in req.url) as req_info, \
         page.expect_response(lambda resp: resp.request.method == "POST" and "/api/login" in resp.url) as resp_info:
        base.click('button:has-text("Log in")')

    response = resp_info.value
    status = response.status
    logger.info(f"RESPONSE ← HTTP {status} на {response.url}")
    assert status == 200, f"Ожидали HTTP 200, получили {status}"

    # 3. Разбираем JSON-ответ и проверяем токен
    try:
        body = response.json()
    except Exception:
        take_screenshot(page, "login_api_parse_fail")
        pytest.fail("Не удалось распарсить JSON-ответ от /api/login")

    assert isinstance(body, dict), "Ожидали JSON-объект в теле ответа"
    assert "token" in body, "В ответе отсутствует ключ 'token'"
    token = body["token"]
    assert isinstance(token, str) and token.strip(), "Токен должен быть непустой строкой"
    parts = token.split(".")
    assert len(parts) == 3, f"Неверный формат JWT‑токена: {token}"

    # 4. UI-assertion: проверяем, что открылась страница личного кабинета
    profile_locator = page.locator('h2.gdx-h2.account__title')
    profile_locator.wait_for(state='visible', timeout=10_000)
    title_text = profile_locator.text_content().strip()
    assert title_text == 'Personal profile', \
        f"Ожидали заголовок 'Personal profile', получили '{title_text}'"

    logger.info("=== Конец теста: test_login_api_response ===")
