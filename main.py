import os
import time
import logging
import pyotp
import traceback
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
    global TIMEOUT, LOGIN_TIMEOUT, EMAIL, PASSWORD, LOGLEVEL, SLEEPTIME, TOTP, DEBUG

    # dev environment
    DEBUG = os.getenv('DEBUG') is not None

    value = os.getenv('TIMEOUT') or 5
    TIMEOUT = int(value)
    value = os.getenv('LOGIN_TIMEOUT') or 10
    LOGIN_TIMEOUT = int(value)

    EMAIL = os.getenv('EMAIL') or ''
    PASSWORD = os.getenv('PASSWORD') or ''
    LOGLEVEL = str.upper(os.getenv('LOGLEVEL') or '')
    SLEEPTIME = int(os.getenv('SLEEPTIME') or -1)
    value = os.getenv('TOTP') or None
    TOTP = None if value is None else pyotp.TOTP(value)


def execute():
    chrome_options = Options()
    # bypass OS security model
    chrome_options.add_argument('--no-sandbox')
    # overcome limited resource problems
    chrome_options.add_argument('--disable-dev-shm-usage')
    # path when run inside of docker container
    chrome_driver_path = '/usr/bin/chromedriver'

    if DEBUG:
        chrome_driver_path = './chromedriver'
        # window size when run in headless mode.
        # this is necessary as some styles are dynamic
        chrome_options.add_argument('--window-size=800,600')
    else:
        chrome_options.add_argument('--headless')

    browser = webdriver.Chrome(chrome_driver_path, options=chrome_options)
    browser.get('https://www.epicgames.com/store/en-US/free-games/')

    try:
        # need to wait for element to be clickable
        logger.debug('find and click on login button')
        el = WebDriverWait(browser, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/login']"))
        )
        el.click()

        # need to wait for element to be clickable
        logger.debug('wait for email field on login page')
        el = WebDriverWait(browser, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "usernameOrEmail"))
        )

        el.send_keys(EMAIL)
        browser.find_element_by_id('password').send_keys(PASSWORD)
        WebDriverWait(browser, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, 'login'))
        ).click()

        if TOTP is not None:
            logger.debug('wait for 2fa field on login page')
            el = WebDriverWait(browser, TIMEOUT).until(
                EC.element_to_be_clickable((By.ID, "code"))
            )
            el.send_keys(TOTP.now())
            logger.debug('logging in with 2fa')
            browser.find_element_by_id('continue').click()

        try:
            # confirm login
            logger.debug('search for wrong credentials message')
            WebDriverWait(browser, LOGIN_TIMEOUT).until(EC.visibility_of_element_located((
                By.XPATH, "//h6[contains(text(),'credentials') and contains(text(),'invalid')]"
            )))
            logger.critical('failed to login into account, credentials invalid')
            return
        except TimeoutException:
            logger.debug('login succeeded')
            pass

        try:
            # get free games available
            logger.debug('wait for and get all free games available')
            games_found = WebDriverWait(browser, TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.XPATH, "//a[descendant::span[text()='Free Now']]"))
            )
        except TimeoutException:
            logger.critical('no free games found')
            return

        # close cookie policy span as that interferes with clicking on the purchase button
        try:
            logger.debug('close the cookies banner')
            browser.find_element_by_xpath("//button[@id='euCookieAccept']").click()
        except NoSuchElementException:
            logger.debug('no cookies banner to close')

        for i in range(len(games_found)):
            # need to wait for element to be clickable
            logger.debug('wait for and get all free games available')
            games_found = WebDriverWait(browser, TIMEOUT).until(
                EC.visibility_of_all_elements_located((By.XPATH, "//a[descendant::span[text()='Free Now']]"))
            )

            # click game
            games_found[i].click()

            # mature content block
            logger.debug('bypass mature content block')
            try:
                WebDriverWait(browser, TIMEOUT).until(
                    EC.visibility_of_element_located((By.XPATH, "//p[contains(text(),'mature content')]")))
                WebDriverWait(browser, TIMEOUT).until(
                    EC.visibility_of_element_located((By.XPATH, "//span[contains(text(),'Continue')]"))).click()
            except TimeoutException:
                logger.debug('no mature content block to bypass')

            # need to wait for element to be visible (it's not clickable if already owned)
            logger.debug('find the purchase button')
            purchase_button = WebDriverWait(browser, TIMEOUT).until(
                EC.visibility_of_element_located((By.XPATH, "//button[contains(@class,'Purchase')]"))
            )

            # name of the game (responsive UI element)
            # will only find it when width < 1024 (default window size is 800x600 when run in headless mode)
            logger.debug('find the game title')
            name = browser.find_element_by_xpath("//h1[contains(@class,'NavigationVertical')]").text

            # price formatted as '£11.99'
            logger.debug('find the game price')
            price = browser.find_element_by_xpath("//s").text

            # date formatted as 'Sale ends 11/29/2019 at 3:59 PM'
            logger.debug('extract aditional info from the purchase button')
            expires = browser.find_element_by_xpath("//span[contains(text(),'Sale ends')]").text

            if purchase_button.text == "OWNED":
                logger.info('game \"%s\" already owned. Price was %s and %s', name, price, expires)
            elif purchase_button.text == 'GET':
                logger.info('obtaining game \"%s\"', name)

                # scroll to button
                logger.debug('scroll to purchase button and click it')
                ActionChains(browser).move_to_element(purchase_button).perform()
                purchase_button.click()

                # wait until its visible and then click the purchase button
                logger.debug('find and click on the last purchase button')
                WebDriverWait(browser, TIMEOUT).until(
                    EC.visibility_of_element_located((By.XPATH, "//button[contains(@class,'btn-primary')]"))
                ).click()

                # wait until its visible and then click the 'I Agree" popup
                # 'Refund and Right of Withdrawal Information' popup
                try:
                    logger.debug('accept the conditions of refund popup')
                    WebDriverWait(browser, TIMEOUT).until(
                        EC.visibility_of_all_elements_located((By.XPATH, "//button[contains(@class,'btn-primary')]"))
                    )[1].click()
                except (NoSuchElementException, LookupError) as ex:
                    logger.debug('no refund conditions popup to accept')

                # Purchase should be complete. Checking for confirmation
                logger.debug('Wait for confirmation that checkout is complete')
                WebDriverWait(browser, TIMEOUT).until(EC.visibility_of_element_located((
                    By.XPATH, "//h1/span[contains(text(),'Install')]|//span[contains(text(),'Thank you for buying')]"
                )))
                logger.info('obtained game %s. Price was %s and %s', name, price, expires)
            elif purchase_button.text == 'SEE EDITIONS':
                logger.warning('game \"%s\" has different editions available, this is not yet supported', name)
            else:
                logger.warning('purchase button text not recognized: %s', purchase_button.text)

            # navigate back to free games page
            browser.get('https://www.epicgames.com/store/en-US/free-games/')
        logger.info('all games processed')
    except (TimeoutException, NoSuchElementException, WebDriverException) as ex:
        logger.critical(traceback.format_exc())
    browser.get('https://www.epicgames.com/logout')
    browser.close()


def main():
    global logger
    logger = logging.getLogger('egs-weekly-freegames')
    read_env_variables()
    logging.basicConfig(level=logging.ERROR)
    logger.setLevel(getattr(logging, LOGLEVEL, "INFO"))
    if EMAIL == "" or PASSWORD == "":
        print('credentials missing')
        return
    logger.debug(
        'started with TIMEOUT: %i, LOGIN_TIMEOUT: %i, EMAIL: %s, password: %s',
        TIMEOUT, LOGIN_TIMEOUT, EMAIL, len(PASSWORD) * "*",
    )
    execute()
    while SLEEPTIME >= 0:
        logger.info('sleeping for %i seconds', SLEEPTIME)
        time.sleep(SLEEPTIME)
        execute()


if __name__ == '__main__':
    main()
