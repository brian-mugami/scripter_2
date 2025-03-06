import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from language_utils import translate_to_english, detect_language
from utils import system_keyword

load_dotenv()
service = Service(ChromeDriverManager().install())
options = Options()
Title = "Ethiopia Tenders"
options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)
et_url = "https://production.egp.gov.et/egp/bids/all"
timeout = 30
driver.get(et_url)


def get_table_data(title, page, keywords):
    data_list = []
    if keywords:
        keywords = {kw.lower() for kw in keywords}
    try:
        table = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, '//tbody'))
        )
        rows = table.find_elements(By.XPATH, ".//tr")

        for row in rows:
            try:
                row_elements = row.find_elements(By.XPATH, ".//td")
                original_text = row_elements[2].text
                language = detect_language(original_text)

                trans_text = (
                    translate_to_english(original_text)
                    if language != "en" and len(original_text) > 3
                    else original_text
                )
                if keywords and not any(keyword in trans_text.lower() for keyword in keywords):
                    continue
                row_data = {
                    "ref_no": row_elements[0].text,
                    "lot_no": row_elements[1].text,
                    "procuring_title": row_elements[2].text,
                    "procuring_title_translated": trans_text,
                    "procuring_entity": row_elements[3].text,
                    "Procurement_category": row_elements[4].text,
                    "Market_approach": row_elements[5].text,
                    "Source": row_elements[6].text,
                    "title": title,
                    "page": page,
                    "link": driver.current_url,
                    "Submission_Deadline": row_elements[7].text,
                }
                data_list.append(row_data)
            except StaleElementReferenceException:
                print("Stale element encountered in ERP Tender Scrapper; skipping row.")
            except IndexError:
                print("Skipping row due to missing columns ERP Tender Scrapper.")
            except Exception as e:
                print(f"Error processing row ERP Tender Scrapper: {e}")

    except Exception as e:
        print(f"Error retrieving table data on page {page}: {e}")

    return data_list


def scrape_data(title, keywords):
    filtered_data = []
    try:
        for i in range(20):  # Scrape 5 pages
            print(f"Scraping page {i + 1}...")
            data_extracted = get_table_data(title=title, page=i + 1, keywords=keywords)
            filtered_data.extend(data_extracted)
            next_button_xpath = '//div[@class="flex items-center justify-end py-3 bg-gray-100"]//li[@class="ant-pagination-next ng-star-inserted"]'
            next_bt = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, next_button_xpath))
            )
            next_bt.click()
            time.sleep(5)

    except Exception as e:
        print("EGP Error:", str(e))
    return filtered_data


def egp_scraper():
    try:
        return scrape_data(Title, system_keyword)
    finally:
        driver.quit()
