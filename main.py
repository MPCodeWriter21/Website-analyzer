# Import regex
import json
import os
import shutil
import zipfile
import urllib.parse

from time import sleep
from typing import Union

import log21
import requests

from bs4 import BeautifulSoup
from PIL import (Image, ImageFont, ImageDraw, )
from decouple import config

from selenium import webdriver
from selenium.common import (
    ElementNotInteractableException, NoSuchElementException,
    TimeoutException, JavascriptException,
    InvalidArgumentException,
)
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from whois import whois
from driver_downloader import get_chrome_driver


def is_valid_url(url) -> bool:
    """
    This function checks if the given url is valid or not.
    If it's valid, It will return True & save the url in main_url.
    If it's not valid, It will return False.

    :param url: URL you want to check
    :return: If URL is valid return True, else return False
    """

    parsed_url = urllib.parse.urlsplit(url)

    if parsed_url.scheme not in ('http', 'https'):
        return False
    if not parsed_url.netloc:
        return False

    return True


class Analyzer:
    def __init__(self, url, name: str = "Analyzer", chromedriver_path: Union[str, os.PathLike] = None,
                 verbose: bool = False):
        # Config Important Options for Webdriver
        self._options = webdriver.ChromeOptions()
        self._options.add_argument("--window-size=1280,1024")
        prefs = {"download.default_directory": os.getcwd()}
        self._options.add_experimental_option("prefs", prefs)
        self._options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self._options.add_argument('--headless')
        if not verbose:
            self._options.add_argument('log-level=3')

        self.name = name
        self.url = url
        parsed_url = urllib.parse.urlsplit(url)
        self.scheme = parsed_url.scheme
        self.domain = parsed_url.netloc
        self.url_path = parsed_url.path
        self.file_location = os.path.dirname(__file__)
        self.saved_path = self.set_save_path()
        self.driver = webdriver.Chrome(get_chrome_driver(remove_zip=True, path=chromedriver_path),
                                       options=self._options)

    def set_save_path(self) -> str:
        """
        Sets the save path for the images.

        :return: The save path for the images.
        """

        self.saved_path = os.path.join(self.file_location, self.name)
        if os.path.isdir(self.saved_path) and not os.listdir(self.saved_path):
            return self.saved_path

        self.saved_path = os.path.join(self.file_location, "save", self.name)

        i = 2
        while os.path.exists(self.saved_path):
            self.saved_path = os.path.join(self.file_location, "save", f'{self.name}-{i}')
            i += 1

        os.makedirs(self.saved_path)

        return self.saved_path

    def _check_exists(self, by, el) -> bool:
        """
        Check element exists in page or not.

        :param by: By what basis to find the element?
        :param el: The element you want to find on the page
        :return: If Element exists in page return True, else return False
        """
        try:
            self.driver.find_element(by, el)
        except NoSuchElementException:
            return False
        except ElementNotInteractableException as e:
            e.args = (f"Element is not interactable: {el}",)
            raise e
        return True

    def _wait_until(self, by: str, el: str):
        """
        It checks every one second if Element Exists in page or not
        If Element Exists in page, It checks again else break loop.

        (It's good for when you want check is page reloaded or not)

        :param by: By what basis to find the element?
        :param el: The element you want to find on the page
        """
        driver = self.driver

        while True:
            sleep(1)
            try:
                driver.find_element(by, el)
            except NoSuchElementException:
                break

    def optimize(self):
        """
        Optimize Images for web

        :return: Optimized Images
        """
        driver = self.driver
        saved_path = self.saved_path

        # Get Image compressor URL
        driver.get("https://imagecompressor.com/")

        WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="fileSelector"]')))
        # Get Upload Button
        try:
            upload_btn = driver.find_element(By.XPATH, '//*[@id="fileSelector"]')
        except NoSuchElementException as e:
            e.args += ("Upload Button Not Found!",)
            raise e

        # Upload images
        try:
            upload_btn.send_keys(f"{saved_path}/whois.png")
        except ElementNotInteractableException as e:
            e.args += ("WHOIS image not intractable!",)
            raise e
        except InvalidArgumentException:
            # WHOIS image file not found
            pass

        try:
            upload_btn.send_keys(f"{saved_path}/responsive.png")
        except ElementNotInteractableException as e:
            e.args += ("Responsive image not intractable!",)
            raise e
        except InvalidArgumentException:
            # Responsive image file not found
            pass

        try:
            upload_btn.send_keys(f"{saved_path}/gtmetrix.png")
        except ElementNotInteractableException as e:
            e.args += ("GTMetrix image not intractable!",)
            raise e
        except InvalidArgumentException:
            # GTMetrix image file not found
            pass

        try:
            upload_btn.send_keys(f"{saved_path}/backlinks.png")
        except ElementNotInteractableException as e:
            e.args += ("Backlinks image not intractable!",)
            raise e
        except InvalidArgumentException:
            # Backlinks image file not found
            pass

        try:
            upload_btn.send_keys(f"{saved_path}/AMP.png")
        except ElementNotInteractableException as e:
            e.args += ("AMP image not intractable!",)
            raise e
        except InvalidArgumentException:
            # AMP image file not found
            pass

        try:
            upload_btn.send_keys(f"{saved_path}/ssl.png")
        except ElementNotInteractableException as e:
            e.args += ("SSL image not intractable!",)
            raise e
        except InvalidArgumentException:
            # SSL image file not found
            pass

        # Find and click download button
        WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="app"]/section[1]/div[3]/button')))
        try:
            download_btn = driver.find_element(By.XPATH, '//*[@id="app"]/section[1]/div[3]/button')
        except NoSuchElementException as e:
            e.args += ("Download Button Not Found!",)
            raise e

        try:
            download_btn.click()
        except ElementNotInteractableException as e:
            e.args += ("Download Button not intractable!",)
            raise e

        # Remove All unoptimized files
        for file in os.listdir(saved_path):
            try:
                os.remove(os.path.join(saved_path, file))
            except PermissionError as e:
                e.args += (f"Permission Error: Removing {file}",)
                raise e

        # Move optimized files to saved path directory
        src = os.path.join(os.getcwd(), "imagecompressor.zip")
        dst = os.path.join(saved_path, "imagecompressor.zip")
        try:
            shutil.move(src, dst)
        except FileNotFoundError as e:
            e.args += (f"File Not Found: {src}",)
            raise e

        # Unzip compressed file
        try:
            with zipfile.ZipFile(dst, 'r') as compress:
                compress.extractall(saved_path)
        except FileNotFoundError:
            pass

    def get_whois(self):
        # Get the website's title
        res = requests.get(self.url)
        soup = BeautifulSoup(res.content, 'html.parser')
        title = soup.find('title')
        if title is None:
            title = "No Title"
        else:
            title = title.text

        # Get Response for our website from whois API
        response = whois(self.domain)

        # Get register status
        register_status = "—"

        # Get Nameservers
        try:
            name_servers = "\n".join(nameserver['ldhName'] for nameserver in response['nameservers'])
        except KeyError:
            name_servers = "—"

        # Dates
        try:
            dates = "\n".join(f"{event['eventAction']}: {event['eventDate']}" for event in response['events'])
        except KeyError:
            dates = "—"

        # Ip information
        ip_info: dict = requests.get(f"http://ip-api.com/json/{self.domain}?fields=66846719").json()

        ip_address = ip_info.get('query')
        hosted_website = ip_info.get('reverse')

        # Get IP Location
        ip_city = ' - ' + ip_info.get('city') if ip_info.get('city') else ''

        ip_location = ip_info.get('country') + ip_city

        # Get country code
        country_code = ip_info.get('countryCode')

        # Get country flag
        flag_url = f'https://countryflagsapi.com/png/{country_code}'
        flag = Image.open(requests.get(flag_url, stream=True).raw)
        flag = flag.convert("RGBA")

        # Resize flag
        (width, height) = (flag.width // 20, flag.height // 20)
        flag = flag.resize((width, height))

        # Load raw whois image
        whois_image = Image.open('assets/images/whois.jpg')

        # Make image editable
        editable = ImageDraw.Draw(whois_image)

        # Load fonts
        font = ImageFont.truetype('assets/fonts/Lato-Regular.ttf', 10)
        domain_font = ImageFont.truetype('assets/fonts/Lato-Regular.ttf', 20)
        title_font = ImageFont.truetype('assets/fonts/Vazirmatn-Regular.ttf', 10)

        # Set colors
        color = (90, 90, 90)
        domain_color = (70, 70, 70)

        # Add text to raw image
        editable.text((165, 0), self.domain, domain_color, font=domain_font)  # Domain name
        editable.text((120, 65), register_status, color, font=font)  # Registrar status
        editable.text((120, 90), name_servers, color, font=font)  # Name servers
        editable.text((120, 152), dates, color, font=font)  # Dates
        editable.text((120, 250), ip_address, color, font=font)  # IP address
        editable.text((195, 250), hosted_website, color, font=font)  # Hosted websites
        editable.text((140, 273), ip_location, color, font=font)  # IP location
        editable.text((120, 330), title, color, font=title_font)  # Website title

        # Add flag to raw image
        whois_image.paste(flag, (120, 275), flag)

        # Save whois image
        whois_image.save(f"{self.saved_path}/whois.png")

    def get_responsive(self):
        driver = self.driver

        # Get Responsive website URL
        driver.get("https://amiresponsive.co.uk/")

        # Change window size for image size
        driver.set_window_size(1280, 1024)

        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.XPATH, '//input[@name="site"]')))

        # Find searchbar in page
        try:
            search_bar = driver.find_element(By.XPATH, '//input[@name="site"]')
        except NoSuchElementException as e:
            e.args += ("Search Bar Not Found!",)
            raise e

        # Pass Main URL to responsive website
        try:
            search_bar.send_keys(self.url)
            search_bar.send_keys(Keys.RETURN)
        except ElementNotInteractableException as e:
            e.args += ("Search Bar not intractable!",)
            raise e

        # make page for good picture by removing element
        driver.execute_script('document.querySelector([role="main"]).style.background = "#fff"')
        driver.execute_script('document.querySelector(".devices blockquote").remove()')
        try:
            driver.execute_script('document.querySelector("form").remove()')
        except JavascriptException:
            pass

        # Fixing image for good picture by changing style
        driver.execute_script("window.scrollTo({top:70, left:0, behavior: 'auto'})")

        # Save file
        driver.save_screenshot(f"{self.saved_path}/responsive.png")

        # Crop and save the image
        image = Image.open(f"{self.saved_path}/responsive.png")
        image.crop((140, 90, 1115, 635)).save(f"{self.saved_path}/responsive.png")

    def get_gtmetrix(self):
        driver = self.driver

        # Delete All Cookies
        driver.delete_all_cookies()

        # Get Responsive website URL
        try:
            driver.get("https://gtmetrix.com/")
            driver.set_page_load_timeout(400)
        except TimeoutException as e:
            e.args += ("Could not get responsive website URL",)
            raise e

        # Change window size for image size
        driver.set_window_size(1280, 1024)

        # === Login Section ===
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, 'user-nav-login')))
        # Find login page button
        try:
            login_btn = driver.find_element(By.XPATH, '//*[@id="user-nav-login"]/a')
        except NoSuchElementException as e:
            e.args += ("Login Button Not Found!",)
            raise e
        login_btn.click()

        WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.NAME, 'email')))
        # Find email and password field in page
        try:
            email = driver.find_element(By.XPATH, '//input[@name="email"]')
        except NoSuchElementException as e:
            e.args += ("Email Field Not Found!",)
            raise e

        WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.NAME, 'password')))
        try:
            password = driver.find_element(By.XPATH, '//input[@name="password"]')
        except NoSuchElementException as e:
            e.args += ("Password Field Not Found!",)
            raise e

        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, 'menu-site-nav')))
        try:
            submit_login_btn = driver.find_element(By.XPATH,
                                                   '//*[@id="menu-site-nav"]/div[2]/div[1]/form/div[4]/button'
                                                   )
        except NoSuchElementException as e:
            e.args += ("Submit Login Button Not Found!",)
            raise e

        # Pass Main URL to responsive website
        try:
            email.send_keys(config('EMAIL'))
            password.send_keys(config('PASSWORD'))
            submit_login_btn.click()
        except ElementNotInteractableException as e:
            e.args += ("Email Field not intractable!",)
            raise e

        # Check Email and Password valid for login gtmetrix
        if self._check_exists(By.CLASS_NAME, "tooltip-error"):
            raise Exception("GTMetrix Login Failed!")

        # Find searchbar in page
        WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/main/article/form/div[1]/div[1]/div/input')))
        try:
            search_bar = driver.find_element(By.XPATH,
                                             '/html/body/div[1]/main/article/form/div[1]/div[1]/div/input')
        except NoSuchElementException as e:
            e.args += ("Search Bar Not Found!",)
            raise e

        # Pass Main URL to GTMetrix website
        try:
            search_bar.send_keys(self.url)
        except ElementNotInteractableException as e:
            e.args += ("Search Bar not intractable!",)
            raise e

        # Find and submit Main URL to GTMetrix website
        WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/main/article/form/div[1]/div[2]/button')))
        try:
            submit_url_btn = driver.find_element(By.XPATH,
                                                 '/html/body/div[1]/main/article/form/div[1]/div[2]/button'
                                                 )
        except NoSuchElementException as e:
            e.args += ("Submit URL Button Not Found!",)
            raise e

        submit_url_btn.click()

        # Wait for analyzing complete
        self._wait_until(By.XPATH, "/html/body/div[1]/main/article/h1")

        # Fixing image for good picture by changing style
        driver.execute_script("window.scrollTo({top:80, left:0, behavior: 'auto'})")
        driver.execute_script("document.body.style.zoom='90%'")

        # Delete ADS banner from page
        WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//div[@id="summer"]')))
        try:
            banner = driver.find_element(By.XPATH, '//div[@id="summer"]')
            driver.execute_script("arguments[0].remove()", banner)
        except NoSuchElementException:
            pass

        # Save file
        driver.save_screenshot(f"{self.saved_path}/gtmetrix.png")

        # Crop and save the image
        image = Image.open(f"{self.saved_path}/gtmetrix.png")
        image.crop((15, 5, 1070, 600)).save(f"{self.saved_path}/gtmetrix.png")

    def get_backlinks(self):
        driver = self.driver

        # Delete All Cookies
        driver.delete_all_cookies()

        # Get Responsive website URL
        driver.get("https://lxrmarketplace.com/seo-inbound-link-checker-tool.html")

        # Change window size for image size
        driver.set_window_size(1280, 1024)

        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.XPATH, '//input[@name="url"]')))
        # Find searchbar in page
        try:
            search_bar = driver.find_element(By.XPATH, '//input[@name="url"]')
            search_bar.send_keys(self.url)
            search_bar.send_keys(Keys.RETURN)
        except NoSuchElementException as e:
            e.args += ("Search Bar Not Found!",)
            raise e
        except ElementNotInteractableException as e:
            e.args += ("Search Bar not intractable!",)
            raise e

        # Fixing image for good picture by changing style
        driver.execute_script('document.querySelector("#cookiePopup").remove()')
        driver.execute_script('document.querySelector("#frm-wrap").remove()')

        # Fixing image for good picture by changing style
        driver.execute_script("window.scrollTo({top:30, left:0, behavior: 'auto'})")

        # Save file
        driver.save_screenshot(f"{self.saved_path}/backlinks.png")

        # Crop and save the image
        image = Image.open(f"{self.saved_path}/backlinks.png")
        image.crop((90, 130, 1230, 540)).save(f"{self.saved_path}/backlinks.png")

    def get_amp(self):
        # Get URL
        url = self.url

        # Load the raw image
        raw_amp = Image.open('assets/images/AMP.jpg')

        # Make image editable
        image_editable = ImageDraw.Draw(raw_amp)

        # Load the font
        title_font = ImageFont.truetype('assets/fonts/Roboto-Medium.ttf', 21)

        # Put the URL in image
        image_editable.text((80, 28), url, (255, 255, 255), font=title_font)

        # Save the image
        raw_amp.save(f"{self.saved_path}/AMP.png")

    def get_ssl(self):
        driver = self.driver
        protocol = self.scheme

        # Get URL and SSL
        url = self.url

        # Get website URL
        driver.get(url)

        # Load the raw image
        raw_https = Image.open(f'assets/images/{protocol}.jpg')
        raw_https = raw_https.convert("RGBA")

        # Get Favicon
        favicon_url = f'http://www.google.com/s2/favicons?domain={url}'
        favicon = Image.open(requests.get(favicon_url, stream=True).raw)
        favicon = favicon.convert("RGBA")

        # Paste favicon on https raw image
        raw_https.paste(favicon, (17, 8), favicon)

        # Make https raw image editable
        editable = ImageDraw.Draw(raw_https)

        # Add Font to our text
        font = ImageFont.truetype('assets/fonts/Vazirmatn-Regular.ttf', 14)

        # Set coordination for URL
        url_coordination = (172, 42) if protocol == 'https' else (260, 42)

        # Draw URL text in the raw image
        editable.text(url_coordination, url, (255, 255, 255), font=font)

        # Get Title from website
        title = driver.title
        title = (title[:20] + '...') if len(title) > 20 else title
        # Set coordination for Page Title
        title_coordination = (41, 7)
        # Draw Title text in the raw image
        editable.text(title_coordination, title, (255, 255, 255), font=font, direction="ltr")

        # Save the image
        raw_https.save(f"{self.saved_path}/ssl.png", format='png')

        return print("SSL Done!")

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __del__(self):
        self.close()
