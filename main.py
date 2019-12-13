import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains


def read_env_variables():
    global TIMEOUT, LOGIN_TIMEOUT, EMAIL, PASSWORD

    value = os.getenv('TIMEOUT') or 5
    TIMEOUT = int(value)
    value = os.getenv('LOGIN_TIMEOUT') or 10
    LOGIN_TIMEOUT = int(value)

    EMAIL = os.getenv('EMAIL') or ""
    PASSWORD = os.getenv('PASSWORD') or ""


def execute():
    global CURRENT_STEP

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    browser = webdriver.Chrome('/usr/bin/chromedriver', options=chrome_options)
    browser.get('https://www.epicgames.com/store/en-US/collection/free-games-collection/')

    try:
        # need to wait for element to be clickable
        CURRENT_STEP = 'find and click on login button'
        el = WebDriverWait(browser, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/login']"))
        )
        el.click()

        # need to wait for element to be clickable
        CURRENT_STEP = 'wait for email field on login page'
        el = WebDriverWait(browser, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "email"))
        )

        el.send_keys(EMAIL)
        browser.find_element_by_id('password').send_keys(PASSWORD)
        browser.find_element_by_id('login').click()

        try:
            # login succeeded
            # need to wait for element to be clickable
            CURRENT_STEP = 'wait for and get all free games available'
            games_found = WebDriverWait(browser, LOGIN_TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.XPATH, "//a[contains(@class,'Card-root') and contains(@href,'/store/en-US/product/')]"))
            )
        except TimeoutException:
            # check if login failed
            CURRENT_STEP = 'search for wrong credentials message'
            browser.find_element_by_xpath("//h6[contains(text(),'credentials') and contains(text(),'invalid')]")
            print('failed to login into account, credentials invalid')
            return

        if len(games_found) < 1:
            print('no free games found')
            return
        for i in range(len(games_found)):
            # need to wait for element to be clickable
            CURRENT_STEP = 'wait for and get all free games available'
            games_found = WebDriverWait(browser, TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.XPATH, "//a[contains(@class,'Card-root') and contains(@href,'/store/en-US/product/')]"))
            )

            # select game
            games_found[i].click()

            # mature content block
            CURRENT_STEP = 'bypass mature content block'
            try:
                WebDriverWait(browser, TIMEOUT).until(EC.visibility_of_element_located((By.XPATH, "//p[contains(text(),'mature content')]")))
                WebDriverWait(browser, TIMEOUT).until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(),'Continue')]"))).click()
            except TimeoutException:
                pass

            # need to wait for element to be visible (it's not clickable if already owned)
            CURRENT_STEP = 'find the purchase button'
            purchase_button = WebDriverWait(browser, TIMEOUT).until(
                EC.visibility_of_element_located((By.XPATH, "//button[contains(@class,'Purchase')]"))
            )

            # name of the game (responsive UI element)
            # will only find it when width < 1024 (default window size is 800x600 when run in headless mode)
            CURRENT_STEP = 'find the game title'
            name = browser.find_element_by_xpath("//h1[contains(@class,'NavigationVertical')]").text

            # price formated as '£11.99'
            CURRENT_STEP = 'find the game price'
            price = browser.find_element_by_xpath("//s").text

            # date formated as 'Sale ends 11/29/2019 at 3:59 PM'
            CURRENT_STEP = 'extract aditional info from the purchase button'
            expires = browser.find_element_by_xpath("//span[contains(text(),'Sale ends')]").text

            if purchase_button.text == "OWNED":
                print('game \"{}\" already owned. Price was {} and {}'.format(name, price, expires))
            elif purchase_button.text == 'GET':
                print('obtaining game ' + name)

                # close cookie policy span as that interferes with button click
                CURRENT_STEP = 'close the cookies banner'
                browser.find_element_by_xpath("//button[@id='euCookieAccept']").click()
                # scroll to button
                CURRENT_STEP = 'scrol to purchase button and click it'
                ActionChains(browser).move_to_element(purchase_button).perform()
                purchase_button.click()

                # wait until its visible and then click the purchase button
                CURRENT_STEP = 'find and click on the last purchase button'
                WebDriverWait(browser, TIMEOUT).until(
                    EC.visibility_of_element_located((By.XPATH, "//button[contains(@class,'btn-primary')]"))
                ).click()

                # wait until its visible and then click the 'I Agree" popup
                # 'Refund and Right of Withdrawal Information' popup
                CURRENT_STEP = 'accept the conditions of refund popup'
                WebDriverWait(browser, TIMEOUT).until(
                    EC.visibility_of_all_elements_located((By.XPATH, "//button[contains(@class,'btn-primary')]"))
                )[1].click()

                # need to wait for the "thank you" message before proceding
                CURRENT_STEP = 'wait for page thanking for the purchase'
                WebDriverWait(browser, TIMEOUT).until(
                    EC.visibility_of_element_located((By.XPATH, "//span[contains(text(),'Thank you for buying')]"))
                )
                print('obtained game {}. Price was {} and {}'.format(name, price, expires))
            else:
                print('purchase button text not recognized: ' + purchase_button.text)

            # navigate back to free games page
            browser.get('https://www.epicgames.com/store/en-US/collection/free-games-collection/')
        print('all games processed')
    except (TimeoutException, NoSuchElementException, WebDriverException) as ex:
        print('failed on step \"' + CURRENT_STEP + '\". DOM may have been updated. Exception message: ' + str(ex))
        browser.close()


def main():
    read_env_variables()
    if EMAIL == "" or PASSWORD == "":
        print('credentials missing')
        return
    print('started with TIMEOUT: {}, LOGIN_TIMEOUT: {}, EMAIL: {}, password: {}'.format(TIMEOUT, LOGIN_TIMEOUT, EMAIL, len(PASSWORD)*"*"))
    execute()


if __name__ == '__main__':
    main()
