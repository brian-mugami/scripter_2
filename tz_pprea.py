import re
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from utils import system_keyword

load_dotenv()
service = Service(ChromeDriverManager().install())
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)
Title = "Nest (Tanzania) Tenders"
tz_url = "https://nest.go.tz/tenders/published-tenders"
tz_xpath = '//div[@class="bg-white rounded-b-xl overflow-hidden ng-tns-c3250602556-7 ng-trigger ng-trigger-fadeIn ng-star-inserted"]'
tz_timeout = 40


def get_filtered_table_data(keywords, page_no: int = None, url: str = None):
    data_list = []
    if keywords:
        keywords = [kw.lower() for kw in keywords]
    try:
        page_elements = WebDriverWait(driver, timeout=10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="p-3"]')))
        for element in page_elements:
            try:
                title = WebDriverWait(element, timeout=10).until(
                    EC.presence_of_element_located((By.XPATH, './/h2')))
                if keywords and not any(keyword in title.text.lower() for keyword in keywords):
                    continue
                org = WebDriverWait(element, timeout=10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, './/div[@class="!text-primary !text-sm !mb-0 cursor-pointer"]')))
                date = WebDriverWait(element, timeout=10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, './/div[@class="whitespace-nowrap"]')))
                deadline_date = WebDriverWait(element, timeout=10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, './/div[@class="!text-accent whitespace-nowrap"]')))
                data_list.append({
                    "page_no": page_no,
                    "link": url,
                    "title": Title,
                    "description": title.text,
                    "organization": org.text,
                    "publish_date": date.text,
                    "deadline_date": deadline_date.text,
                })
            except Exception as e:
                print(f"Skipping element due to error: {e}")
    except Exception as e:
        print("Error extracting data for an element:", str(e))
    return data_list


def scrape_data(url, timeout):
    filtered_data = []
    driver.get(url)
    time.sleep(5)
    max_number = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, '//select//option')))
    match = re.search(r'(\d+)$', max_number.text)
    last_number = int(match.group(1)) if match else 1
    last_number = last_number // 2
    print(f"Total Pages: {last_number}")
    current = 1
    while current < last_number:
        try:
            data = get_filtered_table_data(keywords=system_keyword, page_no=current, url=url)
            time.sleep(10)
            next_button = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(@class, "rounded-r") and contains(@class, "border-gray-300")]')
            ))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(2)
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(5)
            current += 1
            filtered_data.extend(data)
            print(f"Clicked Next Button, now on Page {current}")
        except Exception as e:
            print("No page")
            print(str(e))
            continue
    print(f"Scraped {len(filtered_data)} records.")
    return filtered_data


def tz_scrapper():
    try:
        return scrape_data(tz_url, tz_timeout)
    finally:
        driver.quit()
