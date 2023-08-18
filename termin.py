#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select, WebDriverWait
import selenium.common.exceptions

# from selenium.webdriver.support import expected_conditions
# from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium_stealth import stealth

# from fake_useragent import UserAgent
import time

# import sys
import chime
import json
import configs.config

# Read the config.json file and parse it
with open("config.json", "r") as config_file:
    configs_json = config_file.read()
    form = json.loads(configs_json)
    request = configs.config.parse_form(form)

# Define timeout and delays lengths
session_timeout = 30 * 60
delay_short = 0.5
delay_medium = 4
delay_long = 30
delay_very_long = 1800

# The appointment booking page's URL
url = "https://otv.verwalt-berlin.de/ams/TerminBuchen/wizardng"

# if sys.platform == "linux":
#     path_to_driver = "~/.wdm/drivers/chromedriver/linux64/108.0.5359/chromedriver"
# elif sys.platform == "win32":
#     path_to_driver = ".\\chromedriver.exe"


def wait_find(
    browser: webdriver.Chrome,
    value: str,
    attribute: str = By.ID,
    timeout: float | int = None,
) -> str:
    """This function finds an element with the attribute field of \"attribute\" and the attribute value of \"value\" continuesly.
    If the optional argument of \"timeout\" is set it tries until the timeout reaches.
    This function is specifically usefull when not sure if the page is loaded yet.
    It returns the text field of the tag as the output.
    """
    # ignored_exceptions=(selenium.common.exceptions.NoSuchElementException, selenium.common.exceptions.StaleElementReferenceException)
    # WebDriverWait(browser, session_timeout, ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((attribute, wait_for_element)))
    searchTxt = ""
    # Check if the timeout is present
    if timeout:
        # Set the timespan
        initial = time.time()
        final = initial + timeout
        # Try finding the element until the timeout reaches
        while (not searchTxt) and (time.time() < final):
            try:
                searchTxt = browser.find_element(attribute, value)
            except selenium.common.exceptions.NoSuchElementException:
                continue
        if time.time() > final:
            raise TimeoutError
    else:
        # Try finding the element until eternity :)
        while not searchTxt:
            try:
                searchTxt = browser.find_element(attribute, value)
            except selenium.common.exceptions.NoSuchElementException:
                continue
    return searchTxt


def wait_loading(browser: webdriver.Chrome, timeout: float | int = None):
    initial = time.time()
    # Wait until page loads
    wait_find(browser, "loading", By.CLASS_NAME, timeout=timeout)
    time.sleep(delay_medium)
    check = True
    # Check if the timeout is present
    if timeout:
        # Set the timespan
        final = initial + timeout
        # Keep iterating until page gets out of blocking mode or time is out
        while check and time.time() < final:
            # Let the page initializes
            time.sleep(delay_short)
            # Catch the loading element (which blocks the page)
            element_loading = wait_find(
                browser, "loading", By.CLASS_NAME, timeout=timeout
            )
            # Extract its class attribute
            block = element_loading.get_attribute("style")[8:14]
            # Check if it is blocking the page or not (check = True if in blocking mode)
            check = block == " block" or block == "block;"
        # Raise error if time is out
        if time.time() > final:
            raise TimeoutError
    else:
        # Keep iterating until page gets out of blocking mode
        while check:
            # Let the page initializes
            time.sleep(delay_short)
            # Catch the loading element (which blocks the page)
            element_loading = wait_find(browser, "loading", By.CLASS_NAME)
            # Extract its class attribute
            block = element_loading.get_attribute("style")[8:14]
            # Check if it is blocking the page or not (check = True if in blocking mode)
            check = block == " block" or block == "block;"


def catch_termin_page(browser: webdriver.Chrome):
    """This prevents the browser from closing or iterating in the case the appointment page appears."""
    try:
        # Spend only 5 seconds finding a specific element
        # that does not appear in appointment booking page
        wait_find(
            browser,
            f'//label[@for="{request["service"]}"]',
            attribute=By.XPATH,
            timeout=5,
        )
    # Investigate the if the timeout occured or the element actually founded
    except TimeoutError:
        # In case of timeout, beep thrice
        for i in range(3):
            chime.info(sync=True)
        time.sleep(delay_very_long)
    else:
        return


# Set some options for the browser
options = Options()
# userAgent = UserAgent().random
# print(userAgent)
# options.add_argument(f'user-agent={userAgent}')
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--incognito")
options.add_experimental_option("prefs", {"profile.block_third_party_cookies": True})
# options.xperimental_option('detach', True)
# s = Service(path_to_driver)
s = Service()

# Open the test browser
with webdriver.Chrome(service=s, options=options) as driver:
    # with webdriver.Chrome(service=s) as driver:
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    # request the page and wait until it loads
    driver.get(url)
    wait_loading(driver)

    # Set the timeout (the time by which the session expires)
    time_session_end = time.time() + session_timeout

    # Tick the consent check box
    check_box = wait_find(driver, "xi-cb-1", timeout=delay_long)
    check_box.click()

    # Click continue button
    time.sleep(delay_short)
    button_continue = driver.find_element(By.ID, "applicationForm:managedForm:proceed")
    button_continue.click()

    # Wait the new page loading
    wait_loading(driver)

    # Select citizenship
    select_citizenship = wait_find(driver, "xi-sel-400", timeout=delay_long)
    time.sleep(delay_medium)
    Select(select_citizenship).select_by_value(request["code_citizenship"])

    # Select applicant(s) count
    time.sleep(delay_short)
    select_number = driver.find_element(By.ID, "xi-sel-422")
    time.sleep(delay_short)
    Select(select_number).select_by_value(request["count_applicants"])

    # Select the whether the applicant have spouse
    time.sleep(delay_short)
    select_live_in_berlin = driver.find_element(By.ID, "xi-sel-427")
    time.sleep(delay_short)
    Select(select_live_in_berlin).select_by_value(request["live_together"])

    # Select spouse's (if any) citizenship
    if request["live_together"] == "1":
        time.sleep(delay_short)
        select_partner = driver.find_element(By.ID, "xi-sel-428")
        time.sleep(delay_short)
        Select(select_partner).select_by_value(request["code_citizenship_partner"])

    # Select service category requested
    time.sleep(delay_short)
    radio_extend = driver.find_element(
        By.XPATH, f'//label[@for="{request["service_category"]}"]'
    )
    radio_extend.click()

    # Select the general perpose of permit (if required)
    if configs.config.general_perpose_required(request["service_category"]):
        time.sleep(delay_short)
        radio_purpose_of_permit_general = driver.find_element(
            By.XPATH, f'//label[@for="{request["service"]}"]'
        )
        radio_purpose_of_permit_general.click()

    # Select specific perpose of permit requested
    time.sleep(delay_short)
    radio_purpose_of_permit_specific = driver.find_element(
        By.ID, request["type_residence_permit"]
    )
    radio_purpose_of_permit_specific.click()

    # Continuesly click the continue button until it goes to the next page
    # or the session terminates
    while time.time() < time_session_end:
        # Wait until the page loads
        try:
            time.sleep(delay_short)
            wait_loading(driver)
        except selenium.common.exceptions.UnexpectedAlertPresentException:
            alert = driver.switch_to.alert
            print(alert.text)
            alert.accept()
            wait_loading(driver)

        # Catch appointment booking page as it appears
        time.sleep(delay_short)
        catch_termin_page(driver)

        # Click on the continue button, otherwise
        button_continue = wait_find(
            driver, "applicationForm:managedForm:proceed", timeout=delay_long
        )
        button_continue.click()

driver.quit()
