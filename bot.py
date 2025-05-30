import time
import cv2
import mss
import numpy as np
import pyautogui
import pytesseract

# Указываем путь к исполняемому файлу Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

from fuzzywuzzy import fuzz

from utils import queryMousePosition


def golden_fishing_getMask(hsv):
	'''
	HSV это цветовая модель,
	используется для представления цвета в виде трех компонентов:
	Hue, Saturation, Value
	:param hsv: изображение в HSV
	:return: маска для золотой удочки
	'''
	yellow_lower = np.array([20, 100, 100])
	yellow_upper = np.array([30, 255, 255])
	mask = cv2.inRange(hsv, yellow_lower, yellow_upper)

	return mask




class FishingBot:
	'''
	Основной класс для автоматической рыбалки в Terraria
	'''
	title = "Terraria Auto-Fishing Bot"
	rod = "Golden Fishing Rod"
	ocr = {
		"enabled": False,   # флаг OCR
		"exclude": False,   # флаг исключения определенных объектов
		"list": []          # список исключений
	}

	active = False        # флаг активации бота
	last_catch_time = 0   # интервал между забросами (до нового заброса)
	last_sonar_time = 0   # время чтения сонара (до его исчезновения)

	def __init__(self, config):
		'''
		Инициализация бота
		:param config: конфигурация
		'''
		self.config = config  # присваиваем конфигурацию
		self.sct = mss.mss() # создаем объект для создания скриншотов

	def click(self):
		'''
		Нажимаем на мышь
		'''
		pyautogui.mouseDown() # нажимаем на мышь
		time.sleep(0.01)
		pyautogui.mouseUp() # отпускаем мышь

	def start(self):
		'''
		Запуск бота
		'''
		print("Запуск бота через", self.config["start_after"], "секунд.")
		print("Выбранная удочка:", self.rod)
		print("Пожалуйста, отрегулируйте вашу удочку!")

		# если OCR не включен
		if not self.ocr["enabled"]:
			time.sleep(self.config["start_after"])
			self.click()
			print("Удочка сброшена ...")
			self.last_catch_time = time.time()
		# если OCR включен
		else:
			time.sleep(self.config["start_after"] / 2)

		self.active = True
		self.wait()

	def stop(self):
		'''
		Остановка бота
		'''
		self.active = False

	def wait(self):
		'''
		Ожидание появления метки сонара
		'''
		# если OCR включен
		if self.ocr["enabled"]:
			while self.active:
				# минимальный интервал между забросами
				if time.time() - self.last_catch_time < self.config["last_catch_interval"]:
					continue

				# создаем скриншот метки сонара
				cur = queryMousePosition()
				mon = {
					"left": cur['x'] - 200,
					"top": cur['y'] - 75,
					"width": 400,
					"height": 50
				}
				img = np.asarray(self.sct.grab(mon))

				# создаем RGB для Tesseract
				rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

				# читаем psm 6 & 7
				pcm6 = pytesseract.image_to_string(rgb, lang='rus', config='--psm 6')
				pcm7 = pytesseract.image_to_string(rgb, lang='rus', config='--psm 7')

				# Показываем что видит система (OCR область)
				self.show("OCR - Область сонара", img)

				# Выводим распознанный текст в консоль
				if pcm6.strip():
					print(f"PSM6: '{pcm6.strip()}'")
				if pcm7.strip():
					print(f"PSM7: '{pcm7.strip()}'")

				if(((fuzz.ratio(pcm6.lower(), 'ящик')) > 50 or (fuzz.ratio(pcm7.lower(), 'ящик')) > 50)
				or ('ящик' in pcm6.lower() or 'ящик' in pcm7.lower() or 'яшик' in pcm6.lower() or 'яшик' in pcm7.lower())):
					print("Это Ящик!")
					self.catch(True) # catch ASAP
				else:
					print("Неть ...")

		# если OCR не включен
		else:
			while self.active:

				# минимальный интервал между забросами
				if time.time() - self.last_catch_time < self.config["last_catch_interval"]:
					continue

				cur = queryMousePosition() # функция, возвращает координаты мыши
				mon = {
					"left": cur['x'] - int((self.config["box_height"]/2)),
					"top": cur['y'] - int((self.config["box_width"]/2)),
					"width": self.config["box_width"],
					"height": self.config["box_height"]
				}
				# grab - функция, которая делает скриншот
				img = np.asarray(self.sct.grab(mon))

				# создаем HSV цветовую модель
				hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

				# получаем маску по удочке
				mask = golden_fishing_getMask(hsv)

				# проверяем наличие рыбы
				# np.sum(mask) - функция, которая суммирует все значения в маске
				hasFish = np.sum(mask)

				# Показываем что видит система (область удочки)
				self.show("Анализ цвета - Область удочки", img)

				# Показываем маску (что именно ищет система)
				# self.show("Маска удочки (желтый цвет)", mask)

				# Выводим информацию о маске в консоль
				# >0 - удочка видна, =0 - рыба клюет
				print(f"Сумма маски: {hasFish}")

				# если удочка видна
				if hasFish > 0:
					pass
				# если рыба клюет
				else:
					self.catch()

	def catch(self, asap = False):
		'''
		Захватываем рыбу
		'''
		print("Ловим! ...")

		# если не нужно ловить сразу
		if not asap:
			time.sleep(0.3)

		self.click()

		time.sleep(1) # ждем 1 секунду
		print("Новая удочка заброшена ...")
		self.click()

		# сброс времени последнего заброса
		self.last_catch_time = time.time()

	def show(self, title, img):
		'''
		Отображает изображение в окне
		'''
		cv2.imshow(title, img)
		if cv2.waitKey(25) & 0xFF == ord("q"):
			cv2.destroyAllWindows()
			quit()
