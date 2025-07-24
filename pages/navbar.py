from playwright.sync_api import Page
from utils.base_test import BaseTest

class Navbar:
    ACCOUNT_DROPDOWN = 'div.gdx-account-select'
    LOGOUT_OPTION    = 'ul[role="listbox"] >> text=Log out'

    def __init__(self, page: Page):
        self.page = page
        self.base = BaseTest(page)

    def logout(self) -> None:
        self.base.click(self.ACCOUNT_DROPDOWN)
        self.base.click(self.LOGOUT_OPTION)
        self.page.wait_for_url("**/sign-in", timeout=10000)
