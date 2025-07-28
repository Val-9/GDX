# pages/main_page.py
from playwright.sync_api import Page
from utils.base_test import BaseTest
from utils.logger import logger
from pages.auth_page import AuthPage

class MainPage:  
    URL = "https://godex.io/"  # Исправлено: убраны лишние пробелы
    
    # Локаторы
    DASHBOARD_LINK = 'header a.gdx-header__sign-in.size-2'
    # Локаторы для формы обмена
    EXCHANGE_FORM = 'div.gdx-exchange-form' # Основной контейнер формы
    SEND_INPUT = 'div.exchange-input:first-child input' # Поле ввода "You Send"
    RECEIVE_INPUT = 'div.exchange-input:last-child input' # Поле ввода "You Get"
    EXCHANGE_BUTTON = 'a.exchange-button' # Кнопка Exchange
    
    def __init__(self, page: Page):
        self.page = page
        self.base = BaseTest(page)
        
    def navigate_to_main(self) -> 'MainPage': # Добавлен возврат self для цепочки вызовов
        """
        Переход на главную страницу
        """
        logger.info("Открытие главной страницы")
        self.base.open_url(self.URL.strip(), wait_until="networkidle", timeout=30000) # .strip() убирает пробелы
        return self # Возвращаем self для возможности цепочки вызовов
        
    def click_dashboard(self) -> AuthPage:
        """
        Клик по кнопке Dashboard и переход на страницу логина
        
        Returns:
            AuthPage: Страница аутентификации
        """
        logger.info("Клик по кнопке Dashboard")
        
        # Ожидаем появления кнопки
        self.base.wait_for_element(self.DASHBOARD_LINK, timeout=10000)
        
        # Клик по кнопке
        self.base.click(self.DASHBOARD_LINK)
        
        # Ожидаем перехода на страницу логина
        try:
            self.page.wait_for_url("**/sign-in", timeout=10000)
            logger.info("Успешный переход на страницу логина")
        except Exception as e:
            current_url = self.page.url
            logger.error(f"Не удалось перейти на страницу логина. Текущий URL: {current_url}")
            raise AssertionError(f"Ожидался переход на /sign-in, но URL стал: {current_url}")
        
        # Возвращаем следующую страницу
        return AuthPage(self.page)
    
    def is_dashboard_visible(self) -> bool:
        """
        Проверяет, видна ли кнопка Dashboard
        
        Returns:
            bool: True если кнопка видна, False если нет
        """
        try:
            return self.page.locator(self.DASHBOARD_LINK).is_visible(timeout=5000)
        except:
            return False

    # --- Методы для работы с формой обмена ---
    # Все методы ниже теперь находятся внутри класса MainPage

    def select_send_currency(self, currency: str) -> None:
        """Выбор монеты для You Send"""
        logger.info(f"Выбор монеты 'You Send': {currency}")
        # Клик по полю ввода "You Send" для активации выбора
        self.page.click(self.SEND_INPUT)
        # Заполняем поле названием монеты
        self.page.fill(self.SEND_INPUT, currency)
        # Нажимаем Enter для подтверждения выбора (если это требуется UI)
        self.page.press(self.SEND_INPUT, 'Enter')
        
    def select_receive_currency(self, currency: str) -> None:
        """Выбор монеты для You Get"""
        logger.info(f"Выбор монеты 'You Get': {currency}")
        # Клик по полю ввода "You Get" для активации выбора
        self.page.click(self.RECEIVE_INPUT)
        # Заполняем поле названием монеты
        self.page.fill(self.RECEIVE_INPUT, currency)
        # Нажимаем Enter для подтверждения выбора (если это требуется UI)
        self.page.press(self.RECEIVE_INPUT, 'Enter')
        
    def set_send_amount(self, amount: str) -> None:
        """Установка суммы для You Send"""
        logger.info(f"Установка суммы 'You Send': {amount}")
        self.page.fill(self.SEND_INPUT, amount)
        
    def set_receive_amount(self, amount: str) -> None:
        """Установка суммы для You Get"""
        logger.info(f"Установка суммы 'You Get': {amount}")
        self.page.fill(self.RECEIVE_INPUT, amount)
        
    def click_exchange_button(self) -> None:
        """Нажатие кнопки Exchange"""
        logger.info("Нажатие кнопки Exchange")
        # Дождаться, пока кнопка станет кликабельной (не disabled)
        self.page.wait_for_selector(f"{self.EXCHANGE_BUTTON}:not([disabled])", timeout=10000)
        self.page.click(self.EXCHANGE_BUTTON)

    