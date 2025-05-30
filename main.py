import logging
from config import load_config
from bot import FishingBot

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Запуск бота
if __name__ == "__main__":
	config = load_config("config.ini")
	bot = FishingBot(config)
	bot.start()
