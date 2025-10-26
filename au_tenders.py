import logging
import time
from urllib.parse import urljoin

from dotenv import load_dotenv
from langdetect import detect
from selenium import webdriver
from selenium.common import StaleElementReferenceException, NoSuchElementException, TimeoutException
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
Title = "A.U Tenders"
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--lang=en-US")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
driver = webdriver.Chrome(service=service, options=options)
url = "https://au.int/en/bids"
timeout = 40
driver.get(url)
wait = WebDriverWait(driver, 40)
logging.basicConfig(level=logging.INFO)
RESULTS_LOCATOR = (By.XPATH, '//table[contains(@class,"views-table")]')
PAGELOAD_TIMEOUT = 40

def norm_text(el) -> str:
    txt = (el.get_attribute("textContent") or el.text or "").strip()
    return " ".join(txt.split())

def safe_detect_lang(text: str) -> str:
    if not text or text.isascii():
        return "en"
    try:
        return detect(text)
    except Exception:
        return "en"

def wait_ready():
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

# def scrape_page():
#     data_list = []
#     wait_ready()
#     keywords_lc = {kw.lower() for kw in (system_keyword or [])}
#     try:
#         container = WebDriverWait(driver, PAGELOAD_TIMEOUT).until(
#                     EC.presence_of_element_located(RESULTS_LOCATOR)
#                 )
#         elements = container.find_elements(by=By.XPATH, value='.//tbody//tr')
#         try:
#             for element in elements:
#                 deadline = element.find_element(By.XPATH, value='.//td[@class="views-field views-field-field-date active views-align-left"]')
#                 print(deadline.text)
#                 link_and_desc = element.find_element(By.XPATH, value='.//td[@class="views-field views-field-title views-align-left"]//a')
#                 href = link_and_desc.get_attribute('href')
#                 desc = link_and_desc.text
#                 print(href, desc)
#                 try:
#                     language = detect(desc) if desc else "en"
#                 except Exception:
#                     language = "en"
#                 trans_text = translate_to_english(desc) if (language and language != "en") else desc
#                 if any(kw in trans_text.lower() for kw in keywords_lc):
#                     data_list.append({
#                         "description": desc,
#                         "translated_description": trans_text,
#                         "title": Title,
#                         "deadline_date": deadline.text,
#                         "link": href,
#                         "url": url,
#                     })
#         except StaleElementReferenceException:
#             print("Stale element encountered; skipping row.")
#         except NoSuchElementException:
#             print("Skipping row due to missing columns.")
#         except Exception as e:
#             print(f"Row error: {e}")
#
#     except NoSuchElementException:
#         print("Results container not found.")
#
#     for list in data_list:
#         print(list)
#     return data_list

def scrape_page():
    wait_ready()
    keywords_lc = {kw.lower() for kw in (system_keyword or [])}
    data = []

    try:
        container = WebDriverWait(driver, PAGELOAD_TIMEOUT).until(
            EC.presence_of_element_located(RESULTS_LOCATOR)
        )
        rows = container.find_elements(By.CSS_SELECTOR, "tbody > tr")
        for r in rows:
            for attempt in range(2):  # tiny retry for staleness
                try:
                    deadline_el = r.find_element(By.CSS_SELECTOR, 'td.views-field-field-date')
                    link_el = r.find_element(By.CSS_SELECTOR, 'td.views-field-title a')
                    deadline = norm_text(deadline_el)
                    desc = norm_text(link_el)
                    href = (link_el.get_attribute("href") or "").strip()

                    # quick keyword check first (before langdetect/translate)
                    if not any(kw in desc.lower() for kw in keywords_lc):
                        # try English translation only if not matched
                        lang = safe_detect_lang(desc)
                        trans = translate_to_english(desc) if lang != "en" else desc
                        if not any(kw in trans.lower() for kw in keywords_lc):
                            break
                    else:
                        trans = desc
                    data.append({
                        "description": desc,
                        "translated_description": trans,
                        "title": Title,
                        "deadline_date": deadline,
                        "link": href,
                        "url": url,
                    })
                    break
                except StaleElementReferenceException:
                    if attempt == 1:
                        logging.warning("Stale row twice; skipping.")
                except NoSuchElementException:
                    break
                except Exception as e:
                    logging.exception(f"Row error: {e}")
                    break
    except TimeoutException:
        logging.error("Results table not found within timeout.")

    return data

scrape_page()

def au_scrape():
    try:
        return scrape_page()
    finally:
        driver.quit()

