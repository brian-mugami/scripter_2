import time
from urllib.parse import urljoin

from dotenv import load_dotenv
from langdetect import detect
from selenium import webdriver
from selenium.common import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from language_utils import translate_to_english
from utils import system_keyword

load_dotenv()
service = Service(ChromeDriverManager().install())
options = Options()
Title = "AFDB Tenders"
options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)
url = "https://www.afdb.org/en/projects-and-operations/procurement"
timeout = 30
driver.get(url)
wait = WebDriverWait(driver, 15)

initial = WebDriverWait(driver, timeout).until(
    EC.presence_of_element_located((By.XPATH, '//div[@class="views-bootstrap-grid-plugin-style"]'))
)

RESULTS_LOCATOR = (By.XPATH, '//div[@class="views-bootstrap-grid-plugin-style"]')
PAGELOAD_TIMEOUT = 15


def wait_ready():
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")


def get_filtered_table_data(container, keywords_lc, page_no: int, url: str):
    data_list = []
    try:
        cards = container.find_elements(
            By.XPATH,
            './/div[contains(@class,"row")]//div[contains(@class,"col-md-4")]'
        )
        for card in cards:
            try:
                date_div = card.find_element(By.XPATH, './/span[contains(@class,"date-display-single")]')
                link = card.find_element(By.XPATH, ".//a")
                href = (link.get_attribute('href') or "").strip()
                text = (link.get_attribute("textContent") or link.text or "").strip()
                date = date_div.text.strip()

                # robust language detect
                try:
                    language = detect(text) if text else "en"
                except Exception:
                    language = "en"

                trans_text = translate_to_english(text) if (language and language != "en") else text

                if any(kw in trans_text.lower() for kw in keywords_lc):
                    data_list.append({
                        "page": page_no,
                        "description": text,
                        "translated_description": trans_text,
                        "page_no": page_no,
                        "title": Title,
                        "publish_date": date,
                        "link": href,
                        "url": url,
                    })
            except StaleElementReferenceException:
                continue
            except NoSuchElementException:
                continue
            except Exception as e:
                print(f"Row error: {e}")
    except NoSuchElementException:
        print("Results container not found.")
    return data_list


def scrape_data(pages=8, delay_sec=2):
    filtered_data, visited, seen_links = [], set(), set()
    keywords_lc = {kw.lower() for kw in (system_keyword or [])}
    done = 0

    while done < pages:
        wait_ready()
        container = WebDriverWait(driver, PAGELOAD_TIMEOUT).until(
            EC.presence_of_element_located(RESULTS_LOCATOR)
        )
        if delay_sec:
            time.sleep(delay_sec)

        cur_url = driver.current_url
        if cur_url in visited:
            break
        visited.add(cur_url)

        # scrape this page
        page_items = get_filtered_table_data(container, keywords_lc, page_no=done + 1, url=cur_url)
        # de-dupe by link (optional)
        for item in page_items:
            if item["link"] not in seen_links:
                filtered_data.append(item)
                seen_links.add(item["link"])

        done += 1
        if done >= pages:
            break

        # get next URL
        try:
            next_a = WebDriverWait(driver, PAGELOAD_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, '//li[contains(@class,"next")]/a[@title="Go to next page"]'))
            )
        except Exception:
            break

        href = (next_a.get_attribute("href") or "").strip()
        if not href or href.endswith("#"):
            break
        next_url = urljoin(cur_url, href)
        if next_url in visited or next_url == cur_url:
            break

        # force real page change
        old_container = container
        driver.get(next_url)
        WebDriverWait(driver, PAGELOAD_TIMEOUT).until(EC.staleness_of(old_container))

    return filtered_data


def afdb_scrape():
    try:
        return scrape_data()
    finally:
        driver.quit()
