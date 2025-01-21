import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from utils import system_keyword, get_page

load_dotenv()
driver_path = "chromedriver.exe"
service = Service(executable_path=driver_path)
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)
title = "PPIP(Kenya) Tenders"
ppip_url = "https://tenders.go.ke/tenders"

print("Kenya Running")


def get_filtered_table_data(page, keywords, page_no: int = None, url: str = None):
    headers = []
    headers_text = WebDriverWait(driver, timeout=15).until(
        EC.presence_of_all_elements_located((By.XPATH, '//tr[@class="text-caption font-weight-bold"]//th'))
    )
    for header_text in headers_text:
        headers.append(header_text.text)

    filtered_table_data = []
    rows = WebDriverWait(page, timeout=10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//tbody//tr'))
    )
    for row in rows:
        try:
            elements = WebDriverWait(row, timeout=10).until(
                EC.presence_of_all_elements_located((By.XPATH, ".//td"))
            )
            row_data = {}
            for idx, element in enumerate(elements):
                if idx < len(headers):
                    row_data[headers[idx]] = element.text

            if "Description" in row_data and any(
                    keyword.lower() in row_data["Description"].lower() for keyword in keywords):
                filtered_table_data.append(row_data)
                try:
                    button = elements[-2].find_element(By.TAG_NAME, "button")
                    button.click()
                    tender_info = WebDriverWait(driver, timeout=5).until(
                        EC.element_to_be_clickable((By.XPATH, '//div[@class="v-list-item-title"]'))
                    )
                    tender_info.click()
                    time.sleep(5)
                    link = WebDriverWait(driver, timeout=5).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        '//div[@class="v-card-text d-flex flex-column"]//span[@class="my-2 text-body-1"]//a'))
                    )
                    time.sleep(5)
                    print(link.text)
                    row_data["link"] = link.text
                    row_data["page"] = page_no
                    row_data["title"] = title
                    back_button = WebDriverWait(driver, timeout=5).until(
                        EC.element_to_be_clickable((By.XPATH,
                                                    '//button[@class="v-btn v-btn--elevated v-btn--icon v-theme--lightTheme bg-warning v-btn--density-default v-btn--size-small v-btn--variant-elevated"]'))
                    )
                    back_button.click()
                    time.sleep(5)
                except Exception as e:
                    print(f"Error handling button or modal: {e}")
                    row_data["link"] = url
                    row_data["page"] = page_no
        except StaleElementReferenceException:
            print("Stale element encountered; retrying row processing.")
            continue
        except Exception as e:
            print(f"Error processing row: {e}")

    return filtered_table_data


def scrape_data(url):
    all_filtered_records = []
    page = get_page(url=url, x_path="//table", timeout=40, driver=driver)
    if page:
        filtered_data = get_filtered_table_data(page, system_keyword, page_no=1, url=url)
        all_filtered_records.extend(filtered_data)
        try:
            pagination_list = WebDriverWait(driver, timeout=10).until(
                EC.presence_of_element_located((By.XPATH, '//ul[@class="v-pagination__list"]'))
            )
            for i in range(2, 30):
                next_button = pagination_list.find_element(By.XPATH, f'.//div[text()="{i}"]')
                next_button.click()
                time.sleep(5)
                print(f"Clicked page {i}")
                page_data = get_filtered_table_data(page, system_keyword, page_no=i, url=url)
                all_filtered_records.extend(page_data)
                print(f"Page {i} processed.")
        except Exception as e:
            print(f"Scrapper Error: {e}")
    else:
        print("Failed to load the initial page")

    print("\nFiltered Records Across All Pages:")
    for record in all_filtered_records:
        print(record)

    return all_filtered_records


def ppip_scraper():
    try:
        return scrape_data(ppip_url)
    finally:
        driver.quit()
