import logging


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
options.page_load_strategy = "eager"
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

wait = WebDriverWait(driver, 40)
logging.basicConfig(level=logging.INFO)
RESULTS_LOCATOR = (By.XPATH, '//table[contains(@class,"views-table")]')
PAGELOAD_TIMEOUT = 40

driver.set_page_load_timeout(30)

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


def scrape_page():
    try:
        driver.get(url)
    except TimeoutException:
        # Page may keep loading forever; stop it and continue
        driver.execute_script("window.stop();")

    wait = WebDriverWait(driver, PAGELOAD_TIMEOUT)
    keywords_lc = {kw.lower() for kw in (system_keyword or [])}
    data = []

    try:
        container = wait.until(
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


def au_scrape():
    try:
        return scrape_page()
    finally:
        driver.quit()

