import random
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional, Union, Literal, Any, cast
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, Locator
from utils.logger import logger
from utils.helpers import take_screenshot, random_sleep


class BaseTest:
    """Утилиты для взаимодействия со страницей и повышения стабильности тестов."""
    
    def __init__(self, page: Page):
        self.page = page
        self.context = page.context

    def wait_for_element(self, selector: str, timeout: int = 5000) -> None:
        """Ожидает появления элемента на странице."""
        logger.info(f"Ожидание элемента: {selector}, таймаут={timeout}ms")
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
        except PlaywrightTimeoutError as e:
            logger.error(f"Элемент не найден: {selector}")
            take_screenshot(self.page, f"wait_failed_{selector}")
            raise AssertionError(f"Не найден элемент: {selector}") from e

    def click(self, selector: str, timeout: int = 5000, force: bool = False) -> None:
        """Кликает по элементу с предварительным ожиданием."""
        self.wait_for_element(selector, timeout)
        logger.info(f"Клик по элементу: {selector}")
        locator = self.page.locator(selector)
        locator.scroll_into_view_if_needed()
        locator.click(force=force)

    def fill_input(self, selector: str, value: str, timeout: int = 5000) -> None:
        """Заполняет текстовое поле значением."""
        self.wait_for_element(selector, timeout)
        logger.info(f"Заполнение поля {selector} значением '{value}'")
        self.page.fill(selector, value)

    def open_url(
        self,
        url: str,
        wait_until: Literal['commit', 'domcontentloaded', 'load'] = 'load',
        timeout: int = 30000
    ) -> None:
        """
        Открывает страницу с ретраями и улучшенной обработкой загрузки.
        """
        # Нормализация URL
        if not url.startswith(('http://', 'https://', 'chrome-extension')):
            url = f'https://{url}'

        if self.page.url != url:
            logger.info(f"Открытие URL: {url}")
            try:
                # Пробуем открыть страницу с базовым ожиданием
                self.page.goto(url, wait_until="domcontentloaded", timeout=timeout)
                logger.info(f"Страница загружена (DOM ready): {self.page.url}")
                
                # Дополнительно ждем полной загрузки ресурсов, но с обработкой таймаута
                try:
                    self.page.wait_for_load_state("load", timeout=10000)
                    logger.info("Страница полностью загружена (load event)")
                except TimeoutError:
                    logger.warning("Таймаут ожидания полной загрузки, но DOM готов")
                    
                # Ждем появления body страницы как дополнительную проверку
                try:
                    self.page.wait_for_selector("body", timeout=5000)
                    logger.info("Body страницы найден")
                except TimeoutError:
                    logger.warning("Таймаут ожидания body, но страница загружена")
                    
            except Exception as e:
                logger.error(f"Не удалось открыть страницу {url}: {e}")
                take_screenshot(self.page, "open_url_failed")
                raise

    def is_element_visible(self, selector: str, timeout: int = 3000) -> bool:
        """Проверяет, виден ли элемент на странице."""
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            return self.page.is_visible(selector)
        except PlaywrightTimeoutError:
            return False

    def get_text(self, selector: str, timeout: int = 5000) -> str:
        """Получает текст элемента."""
        self.wait_for_element(selector, timeout)
        return self.page.locator(selector).text_content() or ""

    def get_attribute(self, selector: str, attribute: str, timeout: int = 5000) -> str:
        """Получает значение атрибута элемента."""
        self.wait_for_element(selector, timeout)
        return self.page.locator(selector).get_attribute(attribute) or ""

    def wait_for_url(self, url_pattern: str, timeout: int = 10000) -> None:
        """Ждет, пока URL не будет соответствовать паттерну."""
        logger.info(f"Ожидание URL по паттерну: {url_pattern}")
        try:
            self.page.wait_for_url(url_pattern, timeout=timeout)
            logger.info(f"URL соответствует паттерну: {self.page.url}")
        except PlaywrightTimeoutError as e:
            logger.error(f"URL не соответствует паттерну {url_pattern}")
            raise AssertionError(f"URL не изменился на ожидаемый: {url_pattern}") from e

    def click_if_visible(self, selector: str, timeout: int = 3000) -> bool:
        """Кликает по элементу, если он виден."""
        if self.is_element_visible(selector, timeout):
            self.click(selector)
            return True
        return False

    def wait_for_element_to_disappear(self, selector: str, timeout: int = 5000) -> None:
        """Ждет, пока элемент исчезнет со страницы."""
        logger.info(f"Ожидание исчезновения элемента: {selector}")
        try:
            self.page.wait_for_selector(selector, state="detached", timeout=timeout)
            logger.info(f"Элемент исчез: {selector}")
        except PlaywrightTimeoutError as e:
            logger.warning(f"Элемент не исчез за отведенное время: {selector}")
            raise AssertionError(f"Элемент не исчез: {selector}") from e

    def clear_input(self, selector: str, timeout: int = 5000) -> None:
        """Очищает текстовое поле."""
        self.wait_for_element(selector, timeout)
        self.page.locator(selector).clear()

    def double_click(self, selector: str, timeout: int = 5000) -> None:
        """Двойной клик по элементу."""
        self.wait_for_element(selector, timeout)
        logger.info(f"Двойной клик по элементу: {selector}")
        self.page.locator(selector).dblclick()

    def hover(self, selector: str, timeout: int = 5000) -> None:
        """Наведение курсора на элемент."""
        self.wait_for_element(selector, timeout)
        self.page.locator(selector).hover()