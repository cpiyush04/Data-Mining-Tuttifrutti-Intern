import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import csv


class GamesCrawler:
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

        return webdriver

    def games_url_extractor(self, link, output_file):
        with open(output_file, "a", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(["Game Name", "URL"])

            page = 1

            try:
                while True:
                    self.driver.get(f"{link}{page}")
                    page += 1
                    print(f"Scraping page {page}")

                    wait = WebDriverWait(self.driver, 10)
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                    time.sleep(2)
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                    self.driver.execute_script("window.scrollTo(0, 0);")

                    game_cards = wait.until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, "div.discovery-project-card")
                        )
                    )

                    print(f"Found {len(game_cards)} games")

                    if not game_cards:
                        print("No more games found. Stopping.")
                        break  # Stop if no more content is available

                    for game in game_cards:
                        try:
                            element = game.find_element(By.CSS_SELECTOR, "a.project-card__title")
                            game_name = element.text.strip()
                            game_url = element.get_attribute("href").strip()
                            if game_url:
                                writer.writerow([game_name, game_url])

                        except Exception as e:
                            print(f"Error extracting game: {e}")
                            continue

            except Exception as e:
                print(f"Error loading page {page}: {e}")

            finally:
                self.driver.quit()
                print("Driver closed.")


if __name__ == "__main__":
    scraper = GamesCrawler()
    base_links = ["https://www.kickstarter.com/discover/advanced?state=successful&category_id=35&raised=2&sort=magic"
                  "&seed=2896013&page=", "https://www.kickstarter.com/discover/advanced?state=successful&category_id"
                                         "=35&raised=1&sort=magic&seed=2896013&page=",
                  "https://www.kickstarter.com/discover/advanced?category_id=35&raised=0&sort=magic&seed=2896013&page="]

    for link in base_links:
        scraper.games_url_extractor(link, output_file="Kickstarter-Games_and_URLs.csv")
