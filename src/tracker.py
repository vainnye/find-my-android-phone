from dataclasses import dataclass
import math
import random
import time
from typing import Callable
from selenium.webdriver.remote.webelement import WebElement

from selenium.webdriver.remote.webelement import WebElement

from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from db import Phone, LogDict
from alert import Alert
import logging
logger = logging.getLogger(__name__)


LONG_DELAY = 1 *3600
SHORT_DELAY = 5 *60
PERCENT_DELAY_DELTA = 20
MOVES_NUM_FOR_CALC = math.ceil(30/5)

class WaitFinder(WebDriverWait):
    def find_element(self, by: str, selector: str) -> WebElement:
        return self.until(EC.presence_of_element_located((by, selector)))
    
    def find_elements(self, by: str, selector: str) -> list[WebElement]:
        return self.until(EC.presence_of_all_elements_located((by, selector)))

@dataclass
class TrackingMode:
    nb_last_checks: int|None = None
    nb_last_moves: int|None = None
    
    def __init__(self, fast: bool = False):
        self.fast = fast
    
    @property
    def fast(self) -> bool:
        return self.nb_last_moves is not None
    
    @fast.setter
    def fast(self, state: bool):
        if state:
            print("Fast tracking enabled")
            self.nb_last_checks = 0
            self.nb_last_moves = 0
        else:
            print("Fast tracking disabled")
            self.nb_last_checks = None
            self.nb_last_moves = None

class DeviceTracker:
    fmp_name: str
    phone: Phone
    driver: webdriver.Chrome
    last_location: dict[str, str|datetime] = {}
    tracking: TrackingMode = TrackingMode()

    def __init__(self, phone: Phone, cft_bin_path: str, cft_user_data_path: str, profile_folder: str, phone_url: str):
        self.phone = phone
        self.phone_url = phone_url
        
        options = webdriver.ChromeOptions()
        options.binary_location = cft_bin_path
        options.add_argument(fr"--user-data-dir={cft_user_data_path}")
        options.add_argument(fr'--profile-directory={profile_folder}')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
            )
        self.wait_1 = WaitFinder(self.driver, 1)
        self.wait_5 = WaitFinder(self.driver, 5)
        self.wait_10 = WaitFinder(self.driver, 10)
        self.wait_30 = WaitFinder(self.driver, 30)
        self.last_location = {}
    
    def run(self):
        print("DeviceTracker started")
        self.driver.get(self.phone_url)
        
        self.driver.implicitly_wait(5)
        
        btn = self.pin_signin_button()
        if btn:
            btn.click()
            self.do_pin_signin(input("Enter PIN: "))
        
        self.wait_get_position()
        self.reload()
        
        last_data = self.phone.last_log
        if last_data is None:
            last_data = self.get_data()
            self.phone.add_log(last_data)
        print(f"first position log for phone {self.phone.name_id}: {last_data}")
        print(f"first position log for phone {self.phone.name_id}: {last_data}")
        self.loop()

    def pin_signin_button(self):
        try:
            return self.driver.find_element(By.XPATH, "//*[@role='button'][.//*[contains(text(), 'Sign in to view')]]")
        except:
            return None
        
    def do_pin_signin(self, pin: str):
        device_selector = self.driver.find_element(By.XPATH, "//*[@role='button' and @aria-haspopup='true' and @aria-label='Select a device']")
        device_selector.click()

        if device_selector.get_attribute("aria-expanded") == "false":
            print("Phone selector is not expanded after clicking")
            raise RuntimeError("Phone selector did not expand after clicking")

        device_selector.find_element(By.XPATH, f"//following-sibling::div/*[@role='menu' and @aria-label='Device list']/*[@role='menuitem'][.//*[contains(text(), '{self.phone.doc['fmp_name']}')]]").click()

        pin_input_box = self.driver.find_element(By.XPATH, "//input[@type='password' and @aria-label='Enter PIN']")
        pin_input_box.send_keys(input("Enter PIN: "))

        next_button = self.driver.find_element(By.XPATH, "//button[.//*[contains(text(), 'Next')]]")
        next_button.click()

    def reload(self) :
        print("reloading")
        button = self.wait_10.find_element(By.CSS_SELECTOR, 'button:has(#refresh-location-button)')
        icon_class = lambda: self.wait_1.find_element(By.CSS_SELECTOR, '#refresh-location-button').get_attribute('className')
        
        classBefore = icon_class()
        
        button.click()

        # if classBefore == icon_class():
        try:
            # wait until the load icon starts spinning
            self.wait_1.find_element(By.CSS_SELECTOR, f'#refresh-location-button:not([class="{classBefore}"])')
        except: pass
        # wait until the load icon stops spinning
        self.wait_30.find_element(By.CSS_SELECTOR, f'#refresh-location-button[class="{classBefore}"]')

    def wait_get_position(self):
        pos = self.wait_30.find_element(By.CSS_SELECTOR, '[position]').get_attribute('position')
        if not pos or not pos.strip():
            logger.error("Position not found in the page.")
            raise RuntimeError("Position not found in the page.")
        return pos.strip()

    def wait_get_message(self) :
        return self.wait_30.find_element(By.CSS_SELECTOR, "#location-text").text.strip()

    def get_data(self) -> LogDict:
        return {
            "pos": self.wait_get_position(),
            "epoch": datetime.now(),
            "message": self.wait_get_message()
        }
        

    def loop(self) :
        self.reload()
        data = self.get_data()

        hasMoved: bool = self.phone.last_log["pos"] != data["pos"] # type: ignore

        if self.tracking.fast:
            self.tracking.nb_last_checks += 1 #type: ignore
            if self.tracking.nb_last_checks >= MOVES_NUM_FOR_CALC:
                self.tracking.fast = False

        if hasMoved:
            print("new position! "+data["pos"])
            self.phone.add_log(data)

            self.driver.save_screenshot(f'screenshots/{data["epoch"].timestamp()}.png')
            Alert("New position detected\n"+f"New position: {data['pos']}\nMessage: {data['message']}").show()

            if not self.tracking.fast: self.tracking.fast = True
            self.tracking.nb_last_moves += 1 #type: ignore
            
            delay = SHORT_DELAY
        else:
            delay = LONG_DELAY

        print("next reload in "+str(timedelta(seconds=delay)))
        time.sleep(delay * (1+random.randint(-PERCENT_DELAY_DELTA, PERCENT_DELAY_DELTA)/100))
        self.loop()