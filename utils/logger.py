import os
import logging
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler

# Директория для логов
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Корневой логгер
logger = logging.getLogger("ui_test_logger")
logger.setLevel(logging.DEBUG)  # в файл пишем всё, в консоль – от INFO

# Формат сообщений: [Время] Уровень — Сообщение
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 1) Красивый консольный вывод
console_handler = RichHandler(
    rich_tracebacks=True,  # человекочитаемые tracebacks
    markup=True            # поддержка цветов/маркировки
)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# 2) Файловый хендлер с ротацией: 5 МБ, до 5 бэкапов
file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "test.log"),
    mode="a",
    maxBytes=5 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8"
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Подключаем оба хендлера
logger.addHandler(console_handler)
logger.addHandler(file_handler)
