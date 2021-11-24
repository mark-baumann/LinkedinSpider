# Selenium: automation of browser
from selenium import webdriver
#from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver.v2 as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotVisibleException

# some other imports :-)
import os
import platform
import time
import random
import atexit
from pathlib import Path


class Session:

    HOME_URL = "https://www.linkedin.com"

    def __init__(self, store_session=True):

        self.session_data = {
            "duration": 0,
            "connect_requests": 0,
            "page_visits": 0
        }

        self.visited_profiles = []

        start_session = time.time()

        # this function will run when the session ends
        @atexit.register
        def cleanup():
            # End session duration
            seconds = int(time.time() - start_session)
            self.session_data["duration"] = seconds

            # add session data into a list of messages
            lines = []
            for key in self.session_data:
                message = "{}: {}".format(key, self.session_data[key])
                lines.append(message)

            # print out the statistics of the session
            try:
                box = self._get_msg_box(lines=lines, title="Tinderbotz")
                print(box)
            finally:
                print("Started session: {}".format(self.started))
                y = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print("Ended session: {}".format(y))
                print(self.session_data)

        # Go further with the initialisation
        # Setting some options of the browser here below

        options = uc.ChromeOptions()

        # Create empty profile to avoid loggin in every time
        # Create empty profile to avoid annoying Mac Popup
        if store_session:
            if not os.path.isdir(f'./chrome_profile'):
                os.mkdir(f'./chrome_profile')

            Path(f'./chrome_profile/First Run').touch()
            options.add_argument(f'--user-data-dir=./chrome_profile/')

        options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
        options.add_argument("--lang=en-GB")

        # Getting the chromedriver from cache or download it from internet
        print("Getting ChromeDriver ...")
        self.browser = uc.Chrome(options=options)
        self.browser.set_window_size(1250, 750)

        # clear the console based on the operating system you're using
        os.system('cls' if os.name == 'nt' else 'clear')

        # Cool banner
        print("Welcome to Spider Linkedin.")
        time.sleep(1)

        self.started = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("Started session: {}\n\n".format(self.started))

    def _arrange_login(self):
        while True:
            self.browser.get('https://www.linkedin.com/search/results/people/')

            try:
                WebDriverWait(self.browser, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="email-address"]')))

                print("Not yet logged in...")
                print("Log in manually and accept the cookies banner.")
                input("Press ENTER: once you're logged in succesfully.")
            except TimeoutException:
                print("Already logged in.\nLet's continue...")
                break

    def make_contacts(self, amount=20, message=None, sleep=1):

        if amount <= 0:
            return

        self._arrange_login()

        print(f"Starting to connect with {amount} profiles.")

        current_page = 1
        while True:
            xpath_connect_btns = '//button[contains(@aria-label, "connect")]'
            try:
                WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath_connect_btns)))

                connect_buttons = self.browser.find_elements(By.XPATH, xpath_connect_btns)
            except TimeoutException:
                print("No buttons to connect found, let's try the next page...")
                connect_buttons = []

            for connect_btn in connect_buttons:
                connect_btn.click()

                xpath_send = '//button[@aria-label="Send now"]'
                xpath_add_note = '//button[@aria-label="Add a note"]'
                WebDriverWait(self.browser, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath_send)))

                if message:
                    self.browser.find_element(By.XPATH, xpath_add_note).click()

                    xpath_message_field = '//textarea[name="message"]'

                    WebDriverWait(self.browser, 5).until(
                        EC.presence_of_element_located((By.XPATH, xpath_message_field)))

                    self.browser.find_element(By.XPATH, xpath_message_field).send_keys(message)

                self.browser.find_element(By.XPATH, xpath_send).click()
                self.session_data['connect_requests'] += 1
                if self.session_data.get('connect_requests') >= amount:
                    return
                time.sleep(sleep)

            current_page += 1
            self.browser.get(f'https://www.linkedin.com/search/results/people/?page={current_page}')


    def generate_views(self, amount=20, sleep=5):
        if amount <= 0:
            return

        self._arrange_login()

        print(f"Starting to generate {amount} profile views.")

        current_page = 1
        while True:
            xpath_href = '//a[contains(@href, "in/")]'
            try:
                WebDriverWait(self.browser, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath_href)))

                done_profile_els = self.browser.find_elements(By.XPATH, xpath_href)

                for done_profile_el in done_profile_els:
                    href = done_profile_el.get_attribute('href')

                    # Avoid subpages of the same profile and FAQ or documentation
                    if 'detail' in href or 'help' in href or 'answer' in href:
                        continue

                    if not href in self.visited_profiles:
                        self.visited_profiles.append(href)

                        done_profile_el.click()

                        self.session_data['page_visits'] += 1
                        if self.session_data.get('page_visits') >= amount:
                            return

                        time.sleep(sleep)
                        break

            except:
                current_page += 1
                self.browser.get(f'https://www.linkedin.com/search/results/people/?page={current_page}')


    def _get_msg_box(self, lines, indent=1, width=None, title=None):
        """Print message-box with optional title."""
        space = " " * indent
        if not width:
            width = max(map(len, lines))
        box = f'/{"=" * (width + indent * 2)}\\\n'  # upper_border
        if title:
            box += f'|{space}{title:<{width}}{space}|\n'  # title
            box += f'|{space}{"-" * len(title):<{width}}{space}|\n'  # underscore
        box += ''.join([f'|{space}{line:<{width}}{space}|\n' for line in lines])
        box += f'\\{"=" * (width + indent * 2)}/'  # lower_border
        return box
