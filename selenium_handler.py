import json
import urllib

import requests
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException, NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import random
import time
import pickle
import os

from human_behavior import HumanBehavior


class SeleniumHandler:
    def __init__(self, username, password, proxy=None, cookie_file='cookies.pkl'):
        options = webdriver.ChromeOptions()

        # Uncomment this section if you want to use a proxy
        # if proxy:
        #     options.add_argument(f'--proxy-server={proxy}')

        options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=options)
        self.username = username
        self.password = password
        self.cookie_file = cookie_file

    def login(self):
        self.driver.get("https://www.instagram.com/accounts/login/")

        HumanBehavior.sleep()

        self.accept_cookies()

        HumanBehavior.sleep()

        # Check if cookies file exists, if so load the cookies
        if os.path.exists(self.cookie_file):
            self.load_cookies()
            print("Loaded cookies from file.")

            HumanBehavior.sleep()

            self.driver.get("https://www.instagram.com/")

            print(f"is logged in{self.is_logged_in()}")


            # Check if truly logged in now
            if self.is_logged_in():
                print("Logged in using saved cookies.")
                return
            else:
                print("Cookies expired or invalid. Logging in manually.")

        # If cookies file doesn't exist or are invalid, log in manually
        self.driver.get("https://www.instagram.com/accounts/login/")
        HumanBehavior.sleep()

        login_attempts = 0
        while not self.is_logged_in() and login_attempts <= 3:
            username_input = self.driver.find_element(By.NAME, "username")
            password_input = self.driver.find_element(By.NAME, "password")

            username_input.send_keys(self.username)
            password_input.send_keys(self.password)
            password_input.send_keys(Keys.RETURN)

            login_attempts += 1
            HumanBehavior.sleep(4, 5)

        if login_attempts == 4 and not self.is_logged_in():
            raise PermissionError

        print("Logged in manually.")

        self.handle_save_login_info_prompt()

        self.save_cookies()  # Save cookies after successful login

    def load_cookies(self):
        with open(self.cookie_file, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                self.driver.add_cookie(cookie)

    def save_cookies(self):
        with open(self.cookie_file, 'wb') as file:
            pickle.dump(self.driver.get_cookies(), file)
        print("Cookies saved to file.")

    def is_logged_in(self):
        try:
            # Check for the presence of the login form fields
            self.driver.find_element(By.NAME, "username")
            self.driver.find_element(By.NAME, "password")
            return False  # If these elements are found, we're not logged in
        except (NoSuchElementException, NoSuchWindowException):
            return True  # If elements aren't found, assume we're logged in

    def accept_cookies(self):
        """Check for the cookie consent text and click 'Allow all cookies' if the popup appears."""
        try:
            # Look for the cookie consent text
            consent_text = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Allow the use of cookies from Instagram on this browser?')]")

            if consent_text:
                print("Cookie consent popup detected.")
                # If the text is found, look for the "Allow all cookies" button
                allow_button = self.driver.find_element(By.XPATH, "//button[text()='Allow all cookies']")
                allow_button.click()
                print("Clicked 'Allow all cookies' on the cookie consent popup.")

        except NoSuchElementException:
            # If either the text or button is not found, print a message and move on
            print("Cookie consent popup not found or already handled.")

    def handle_save_login_info_prompt(self):
        try:
            # Check for the "Save your login info?" prompt
            prompt = self.driver.find_element(By.XPATH, "//div[text()='Save your login info?']")
            if prompt:
                # Click the "Save info" button
                save_button = self.driver.find_element(By.XPATH, "//button[text()='Save info']")
                save_button.click()
                print("Clicked 'Save' on the 'Save your login info?' prompt.")
        except NoSuchElementException:
            # If the prompt or button is not found, do nothing
            print("No 'Save your login info?' prompt found.")

    def navigate_to_post(self, post_url):
        # Navigate to the specific post URL
        self.driver.get(post_url)
        time.sleep(random.uniform(2, 4))

    def is_logged_in(self):
        # Check if the profile icon is present, which indicates login status
        self.driver.get("https://www.instagram.com/")
        time.sleep(2)
        try:
            self.driver.find_element(By.XPATH, "//a[contains(@href, '/accounts/activity/')]")
            return True
        except:
            return False

    def navigate_to_post(self, post_url):
        # Navigate to the specific post URL
        self.driver.get(post_url)
        time.sleep(random.uniform(2, 4))

    def get_likes1(self):
        # Open likes list
        self.driver.find_element(By.XPATH, "//a[contains(@href, '/liked_by/')]").click()
        time.sleep(2)

        # Scroll to load all likes
        likes = set()
        for _ in range(5):  # Adjust the range based on the number of likes
            time.sleep(random.uniform(2, 3))
            like_elements = self.driver.find_elements(By.XPATH, "//a[contains(@class, 'FPmhX')]")
            likes.update([el.text for el in like_elements])
            self.driver.execute_script("arguments[0].scrollIntoView();", like_elements[-1])

        print("Likes:", likes)
        return list(likes)

    def get_likes(self, post_shortcode):
        # Extract session ID from cookies
        session_id = self.driver.get_cookie("sessionid")["value"]

        print("Session ID:", session_id)

        # Decode the session ID
        decoded_session_id = urllib.parse.unquote(session_id)
        print("Decoded Session ID:", decoded_session_id)

        # Extract all cookies from Selenium and format them for requests
        cookies = {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
        cookie_header = "; ".join([f"{name}={value}" for name, value in cookies.items()])

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Cookie": cookie_header
        }

        url = "https://www.instagram.com/graphql/query/"
        query_hash = "d5d763b1e2acf209d62d22d184488e57"  # Query hash for likes endpoint

        variables = {
            "shortcode": post_shortcode,
            "include_reel": True,
            "first": 50
        }

        all_likes = []
        has_next_page = True

        while has_next_page:
            response = requests.get(url, headers=headers, params={
                "query_hash": query_hash,
                "variables": json.dumps(variables)
            })

            # Check for any HTTP errors
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                print("Response content:", response.text)  # Inspect response content for more details
                break

            # Try to parse the JSON response, handling any JSON decoding errors
            try:
                data = response.json()
            except json.JSONDecodeError:
                print("Failed to decode JSON. Response content was not JSON.")
                print("Response content:", response.text)
                break

            # Extract likers from the response if JSON decoding is successful
            edges = data.get("data", {}).get("shortcode_media", {}).get("edge_liked_by", {}).get("edges", [])
            new_likers = [edge["node"]["username"] for edge in edges]

            all_likes.extend(new_likers)
            print(f"Collected {len(all_likes)} likes so far...")

            # Get page info to check if there's another page of results
            page_info = data.get("data", {}).get("shortcode_media", {}).get("edge_liked_by", {}).get("page_info", {})
            has_next_page = page_info.get("has_next_page", False)
            variables["after"] = page_info.get("end_cursor")

            # Use a longer delay to avoid rate limiting
            time.sleep(5)

        return all_likes

    def get_comments(self):
        print("Getting comments")
        # Scroll and load comments
        comments = set()
        for _ in range(5):  # Adjust the range based on the number of comments
            time.sleep(random.uniform(2, 3))
            comment_elements = self.driver.find_elements(By.XPATH, "//span[@class='_6lAjh']")
            comments.update([el.text for el in comment_elements])
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        print("Comments:", comments)
        return list(comments)

    def close(self):
        self.driver.quit()