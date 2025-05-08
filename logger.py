import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Создаем директорию для логов если её нет
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)


def setup_logger(name: str = "app") -> logging.Logger:
    """Настройка логгера для приложения"""

    # Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Формат сообщений
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Консольный вывод
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Ротация лог-файлов (10 файлов по 1MB каждый)
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=1024 * 1024,
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # Добавляем обработчики
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Инициализируем основной логгер
logger = setup_logger()