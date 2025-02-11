from selenium import webdriver as wd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import pandas as pd
import csv


class KickstarterScraper:
    def __init__(self):
        """
            Initializes a scraper class and creates a Web Driver session
        """
        self.driver = self.setup_webdriver()

    @staticmethod
    def setup_webdriver():
        """
            Configures the undetected Chrome WebDriver with several custom options
            to optimize performance, avoid detection mechanisms and bypass securities.
        """

        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--process-per-site")
        options.add_argument("--log-level=3")
        options.add_argument("--remote-debugging-port=0")
        options.add_argument("--single-process")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-webgl")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-flash-plugin")
        options.add_argument("--dns-prefetch-disable")
        options.add_argument("--enable-quic")
        options.add_argument("--disable-webrtc")
        options.add_argument("--window-size=1280x800")

        # Block Images to avoid excessive loads
        options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.images": 2,
        })

        # Set WebDriver capabilities to optimize page loading
        options.page_load_strategy = 'eager'

        # Initializing browser session
        webdriver = uc.Chrome(options=options)

        # Blocking unnecessary network requests (images, fonts, videos, etc.) to speed up loading
        webdriver.execute_cdp_cmd("Network.enable", {})
        webdriver.execute_cdp_cmd("Network.setBlockedURLs", {
            "urls": ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.woff", "*.woff2", "*.ttf", "*.ico",  # Fonts
                     "*.mp4", "*.webm", "*.avi", "*.mov", "*.mkv",
                     "*.json", "*.xml"]})

        return webdriver

    @staticmethod
    def read_from_file(filepath, start_row, end_row, url_col):
        """
            Reads Games URLS from the file provided.

            Parameters:
            filepath (str): Path to the Excel file.
            min_row (int): The starting row number to read from.
            max_row (int): The ending row number to read until.
            url_col (int): The column index where URLs are stored.

            Returns:
            list: List of URLs read from the file.
        """
        if filepath.endswith(".xlsx"):
            try:
                df = pd.read_excel(filepath)
                links = df.iloc[start_row - 2:end_row - 1, url_col-1]
                return links
            except Exception as e:
                print(f"Error reading while file: {e}")
                return []
                
        elif filepath.endswith(".csv"):
            try:
                df = pd.read_csv(filepath)
                links = df.iloc[start_row - 2:end_row - 1, url_col-1]
                return links
            except Exception as e:
                print(f"Error reading while file: {e}")
                return []

    def scrape_commentator_name_picture(self, url):
        """
            Extracts commentator names and profile images from the individual games.

            Parameters:
            url (str): The Kickstarter project URL.

            Returns:
            tuple: (game_name (str), list of commentator names, list of profile image links)
        """

        collected_names = set()  # Using Data Struct set to avoid repetitive names from being scrapped
        collected_data = []  # list for storing names and linked profile images as pair

        # Loads the project page
        self.driver.get(url)
        game_name = self.driver.title.strip()
        print(f"Scraping: {game_name}")
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Try to locate and click the comments section
        try:
            comments_section = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.tabbed-nav__link.project-nav__link--comments")))
            comments_section.click()
        except Exception as e:
            print(f"Error locating comments on page: {e}")
            return game_name, []

        # Setup for iterating over comments and loading new content
        page_bottom = self.driver.execute_script("return document.body.scrollHeight")
        max_loading_attempt = 0

        # Scroll down and load more comments until no new content appears
        while True:
            try:
                Load_Button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ksr-button.bttn.bttn-medium.bttn-secondary"
                                                                 ".flex.w100p.fill-bttn-icon.hover-fill-bttn-icon"
                                                                 ".keyboard-focusable")))
                self.driver.execute_script("arguments[0].scrollIntoView(true);", Load_Button)
                self.driver.execute_script("arguments[0].click();", Load_Button)
                time.sleep(2)
                max_loading_attempt = 0
            except Exception:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                max_loading_attempt += 1

            updated_bottom = self.driver.execute_script("return document.body.scrollHeight")
            if updated_bottom == page_bottom and max_loading_attempt >= 1:
                print("No more new content")
                break
            page_bottom = updated_bottom

        # Locate all comment containers and extract names and images
        comments_containers = WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.flex.mb3.justify-between"))
        )

        for container in comments_containers:
            try:
                name = container.find_element(By.CSS_SELECTOR, "span.do-not-visually-track").text.strip()
                if name and name not in collected_names:
                    collected_names.add(name)
                    image_source = container.find_element(By.CSS_SELECTOR, "img.avatar").get_attribute("src")
                    collected_data.append((name, image_source))
            except Exception:
                continue

        return game_name, collected_data

    @staticmethod
    def save_results(file_path, game_name, commentator_data):
        """
            Creates file to save output if it does not exist. Appends data for a single game to an existing file.
            Ensures the game name appears only once for the associated commentators.
        """
        try:
            file_exists = os.path.exists(file_path)
            with open(file_path, mode='a', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)

                if not file_exists:
                    writer.writerow(["Game", "Commentator_Name", "Profile_Image_Link"])
                
                first_row = True
                for name, img in commentator_data:
                    writer.writerow([game_name if first_row else "", name, img])
                    first_row = False

                if not commentator_data:
                    writer.writerow([game_name, "No Commentators Found", "No Image Found"])
        
        except Exception as e:
            print(f"Error saving data: {e}")

        print(f"Data for '{game_name}' saved")

    def links_parser(self, links, output_filepath):
        """
            Executes the scraping process for multiple URLs.

            Parameters:
            links: list of games links taken from read file func.
            output_filepath: path to storage file
        """
        for link in links:
            game_name, commentator_data = self.scrape_commentator_name_picture(link)
            if commentator_data:
                self.save_results(output_filepath, game_name, commentator_data)
            else:
                print(f"No commentators found for: {game_name}")
                break

    def close(self):
        self.driver.quit()
        print("Driver session ended.")


if __name__ == "__main__":
    scraper = KickstarterScraper()
    output_file = "scraped_data1.csv"
    input_file = "new.xlsx"

    try:
        game_links = scraper.read_from_file(input_file, 652, 653, 2)
        scraper.links_parser(game_links, output_file)
    finally:
        scraper.close()
