import os
import requests
import pyotp

def disable_2fa_for_user(password: str, secret: str) -> None:
    """
    Снимает 2FA у пользователя через API.
    Ожидает в .env:
      USER_API_TOKEN — JWT или Bearer-токен пользователя
    """
    token = os.getenv("USER_API_TOKEN")
    if not token:
        raise RuntimeError("Не задан USER_API_TOKEN в окружении")

    # Генерируем текущий одноразовый код из секрета
    totp_code = pyotp.TOTP(secret).now()

    resp = requests.post(
        "https://api.godex.io/api/v2/account/disable2fa",
        headers={"Authorization": f"{token}"},
        json={
            "password": password,
            "time_password": totp_code
        }
    )
    resp.raise_for_status()
