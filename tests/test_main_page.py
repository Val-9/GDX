import pytest

def test_main_page_dashboard_button_is_visible(main_page):
    main_page.navigate_to_main()
    assert main_page.base.is_element_visible(main_page.DASHBOARD_LINK)

def test_main_page_navigation_works(main_page):
    main_page.navigate_to_main()
    auth_page = main_page.click_dashboard()
    assert "/sign-in" in auth_page.page.url

def test_exchange_flow(main_page):
    main_page.navigate_to_main()
    main_page.select_send_currency("BTC")
    main_page.set_send_amount("1")
    
    main_page.select_receive_currency("USDT")
    main_page.set_receive_amount("3500")
    
    main_page.click_exchange_button()