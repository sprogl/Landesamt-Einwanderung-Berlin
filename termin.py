#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select, WebDriverWait
import selenium.common.exceptions
# from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
# from fake_useragent import UserAgent
import time
import sys
import chime
import json
import configs.config

with open("config.json", "r") as config_file:
    configs_json = config_file.read()
    form = json.loads(configs_json)
    request = configs.config.parse_form(form)

session_timeout = 30*60
delay_short = 0.5
delay_medium = 4
delay_long = 30
delay_very_long = 1800
url = "https://otv.verwalt-berlin.de/ams/TerminBuchen/wizardng"
if sys.platform == "linux":
    path_to_driver = "~/.wdm/drivers/chromedriver/linux64/108.0.5359/chromedriver"
elif sys.platform == "win32":
    path_to_driver = ".\\chromedriver.exe"


def wait_find(browser, wait_for_element, attribute=By.ID, timeout=None):
    # ignored_exceptions=(selenium.common.exceptions.NoSuchElementException, selenium.common.exceptions.StaleElementReferenceException)
    # WebDriverWait(browser, session_timeout, ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((attribute, wait_for_element)))
    searchTxt = ""
    if timeout:
        initial = time.time()
        final = initial + timeout
        while (not searchTxt) and (time.time() < final):
            try:
                searchTxt = browser.find_element(attribute, wait_for_element)
            except selenium.common.exceptions.NoSuchElementException:
                continue
        if time.time() > final:
            raise TimeoutError
    else:
        while not searchTxt:
            try:
                searchTxt = browser.find_element(attribute, wait_for_element)
            except selenium.common.exceptions.NoSuchElementException:
                continue
    return searchTxt


def wait_loading(browser, timeout=None):
    initial = time.time()
    wait_find(browser, "loading", By.CLASS_NAME, timeout=timeout)
    time.sleep(delay_medium)
    check = True
    if timeout:
        final = initial + timeout
        while check and time.time() < final:
            time.sleep(delay_short)
            element_loading = wait_find(
                browser, "loading", By.CLASS_NAME, timeout=timeout)
            block = element_loading.get_attribute("style")[8:14]
            check = (block == " block" or block == "block;")
        if time.time() > final:
            raise TimeoutError
    else:
        while check:
            time.sleep(delay_short)
            element_loading = wait_find(browser, "loading", By.CLASS_NAME)
            block = element_loading.get_attribute("style")[8:14]
            check = (block == " block" or block == "block;")


def catch_termin_page(browser):
    try:
        wait_find(
            browser, f'//label[@for="{request["service"]}"]', attribute=By.XPATH, timeout=5)
    except TimeoutError:
        for i in range(3):
            chime.info(sync=True)
        time.sleep(delay_very_long)
    else:
        return


options = Options()
# userAgent = UserAgent().random
# print(userAgent)
# options.add_argument(f'user-agent={userAgent}')
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--incognito")
options.add_experimental_option(
    "prefs", {"profile.block_third_party_cookies": True})
# options.xperimental_option('detach', True)
s = Service(path_to_driver)

with webdriver.Chrome(service=s, options=options) as driver:
    # with webdriver.Chrome(service=s) as driver:
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)

    driver.get(url)

    wait_loading(driver)

    check_box = wait_find(driver, "xi-cb-1", timeout=delay_long)
    time_session_end = time.time() + session_timeout
    # time.sleep(delay_short)
    check_box.click()

    time.sleep(delay_short)
    button_continue = driver.find_element(
        By.ID, "applicationForm:managedForm:proceed")
    # time.sleep(delay_short)
    button_continue.click()

    wait_loading(driver)

    select_citizenship = wait_find(driver, "xi-sel-400", timeout=delay_long)
    time.sleep(delay_medium)
    Select(select_citizenship).select_by_value(request["code_citizenship"])

    time.sleep(delay_short)
    select_number = driver.find_element(By.ID, "xi-sel-422")
    time.sleep(delay_short)
    Select(select_number).select_by_value(request["count_applicants"])

    time.sleep(delay_short)
    select_live_in_berlin = driver.find_element(By.ID, "xi-sel-427")
    time.sleep(delay_short)
    Select(select_live_in_berlin).select_by_value(request["live_together"])

    if request["live_together"] == "1":
        time.sleep(delay_short)
        select_partner = driver.find_element(By.ID, "xi-sel-428")
        time.sleep(delay_short)
        Select(select_partner).select_by_value(
            request["code_citizenship_partner"])

    time.sleep(delay_short)
    radio_extend = driver.find_element(
        By.XPATH, f'//label[@for="{request["service_category"]}"]')
    # time.sleep(delay_short)
    radio_extend.click()

    time.sleep(delay_short)
    radio_purpose_studies = driver.find_element(
        By.XPATH, f'//label[@for="{request["service"]}"]')
    # time.sleep(delay_short)
    radio_purpose_studies.click()

    time.sleep(delay_short)
    radio_purpose_study = driver.find_element(
        By.ID, request["type_residence_permit"])
    # time.sleep(delay_short)
    radio_purpose_study.click()

    while time.time() < time_session_end:
        try:
            time.sleep(delay_short)
            wait_loading(driver)
        except selenium.common.exceptions.UnexpectedAlertPresentException:
            alert = driver.switch_to.alert
            print(alert.text)
            alert.accept()
            wait_loading(driver)
        time.sleep(delay_short)
        catch_termin_page(driver)
        button_continue = wait_find(
            driver, "applicationForm:managedForm:proceed", timeout=delay_long)
        # time.sleep(delay_short)
        button_continue.click()

driver.quit()
