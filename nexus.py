import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

red_light = "    --> Checkpoint: RED"
green_light = "    --> Checkpoint: GREEN"

class Nexus(object):
    def __init__(self, case_browser, case_hub, case_target, case_identifier):
        self.driver = None
        self.case_browser = None
        self.case_hub = case_hub
        self.case_target = case_target
        hub_fields = case_hub.split("=")
        self.target_hub, self.identify_hub = hub_fields
        self.wait = 0
        self.folder_path="baseline/" + case_identifier +"_" + self.identify_hub + "/"

        capability_dictionary = {
            "FIREFOX": webdriver.DesiredCapabilities.FIREFOX.copy(),
            "INTERNETEXPLORER": webdriver.DesiredCapabilities.INTERNETEXPLORER.copy(),
            "CHROME": webdriver.DesiredCapabilities.CHROME.copy(),
            "SAFARI": webdriver.DesiredCapabilities.SAFARI.copy(),
            "MOBILE": webdriver.DesiredCapabilities.FIREFOX.copy()
        }

        self.browser = capability_dictionary[case_browser]
        self.driver = webdriver.Remote(self.target_hub, self.browser)

        self.log("{0} driver acquired from grid: {1}".format(self.identify_hub, self.target_hub))

    def __del__(self):
        self.log("{0} driver released".format(self.identify_hub))
        self.driver.quit()

    def log(self, *messages):
        print(" **", *messages, end="")
        print(" **\n")

    def execute_test(self, explicit_wait, action_identifier, action_type, action_on, action_by, action_text, action_screenshot, at, count, view_delay, pause_point, pause_delay):
        self.wait = explicit_wait
        output = "    --> {0}: {1}".format(action_type, action_identifier)
        if action_type == "start_url":
            result = self.driver.get(self.case_target + action_text)
        elif action_type == "click_element" or action_type == "standard_keys" or action_type == "special_keys" or action_type == "key_chords":
            result = self.do_action(action_type, action_on, action_by, action_text, at)
        elif action_type == "check_condition" or action_type == "check_content" or action_type == "check_title":
            result = self.do_assert(action_type, action_on, action_by, action_text)
        elif action_type == "check_url":
            result = self.do_assert(action_type, action_on, action_by, self.case_target + action_text)
        elif action_type == "get_url":
            result = self.driver.navigate.to(action_text)
        else:
            raise Exception("Action Type: " + action_type + " not defined in nexus.py file (execute_test method)")

        if result is not None:
            output += "\n" + result

            time.sleep(float(view_delay))

        return output

    def do_assert(self, action_type, action_on, action_by, action_text):
        if action_type == "check_condition":
            check_condition = self.locate_element(action_on, action_by)
            if str(check_condition) == "FAILURE":
                return red_light
            else:
                return green_light
        elif action_type == "check_content":
            check_content = self.locate_element(action_on, action_by).text
            if action_text not in check_content:
                return red_light
            else:
                return green_light
        elif action_type == "check_url":
            check_url = str(self.driver.current_url)
            if action_text != check_url:
                return red_light
            else:
                return green_light
        elif action_type == "check_title":
            check_title = str(self.driver.title)
            if action_text != check_title:
                return red_light
            else:
                return green_light
        else:
            raise Exception("Action Type: " + action_type + " not defined in nexus.py file (do_assert method)")

    def do_action(self, action_type, action_on, action_by, action_text, at):
        urlut = (self.driver.current_url)
        print(urlut)
        if at == "Y":
             print("Accessibility Microservice Stub")
        execute_action = self.locate_element(action_on, action_by)
        if action_type == "click_element":
            execute_action.click()
        elif action_type == "standard_keys":
            execute_action.send_keys(action_text)
        elif action_type == "special_keys":
            special_dictionary = {
                "BACK_SPACE": Keys.BACK_SPACE
            }
            execute_action.send_keys(special_dictionary[action_text])
        elif action_type == "key_chords":
            chord_dictionary = {
                "ALT": Keys.ALT,
                "COMMAND": Keys.COMMAND,
                "SHIFT": Keys.SHIFT,
                "CONTROL": Keys.CONTROL
            }
            key_sequence = ""
            key_chords = action_text.split(",")
            for key_chord in key_chords:
                if key_chord in chord_dictionary.keys():
                                key_sequence += chord_dictionary[key_chord] + ", "
                else:
                    key_sequence += key_chord + ", "
            execute_action.send_keys(key_sequence.rstrip(", "))
        else:
            raise Exception("Action Type: " + action_type + " not defined in nexus.py file (do_action method)")

    def locate_element(self, action_on, action_by):
        action_by_dictionary = {
            "id": By.ID,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT,
            "xpath": By.XPATH,
            "tag_name": By.TAG_NAME,
            "class_name": By.CLASS_NAME,
            "css_selector": By.CSS_SELECTOR,
            "name": By.NAME
        }
        try:
            action = WebDriverWait(self.driver, float(self.wait)).until(EC.presence_of_element_located((action_by_dictionary[action_by], action_on)))
            return action
        except TimeoutException:
            return "FAILURE"
