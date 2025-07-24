import os
import time
import random
from datetime import datetime
from playwright.sync_api import Page

def take_screenshot(page: Page, name: str) -> str:
    """Сделать скриншот при ошибке и вернуть путь."""
    os.makedirs("screenshots", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{name}_{timestamp}.png"
    path = os.path.join("screenshots", filename)
    page.screenshot(path=path, full_page=True)
    return path


def random_sleep(min_sec: float = 0.5, max_sec: float = 1.5) -> None:
    """Случайная пауза для стабилизации тестов."""
    time.sleep(random.uniform(min_sec, max_sec))