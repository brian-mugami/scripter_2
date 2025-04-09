import pprint
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
Title = "Rwanda Tenders"
options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)
et_url = "https://www.umucyo.gov.rw/eb/bav/selectListAdvertisingListForGU.do?menuId=EB01020100"
timeout = 30
driver.get(et_url)


def get_table_data(keywords, num=1):
    table = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//table[@class="article_table mb10"]')))

    headings = [heading.text.strip() for heading in table.find_elements(By.XPATH, './/thead//tr//th')]

    rows = table.find_elements(By.XPATH, './/tbody//tr')

    table_data = []
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        row_data = [cell.text.strip() for cell in cells]
        row_dict = dict(zip(headings, row_data))
        row_dict = {k: v for k, v in row_dict.items() if k.strip()}
        row_dict["title"] = Title
        row_dict["link"] = et_url
        row_dict["page"] = num

        tender_name = row_dict.get("Tender Name", "").lower()
        if any(keyword.lower() in tender_name for keyword in keywords):
            table_data.append(row_dict)

    time.sleep(5)

    return table_data


def get_data_list():
    all_filtered_records = []
    initial_data = get_table_data(system_keyword)
    all_filtered_records.extend(initial_data)
    for page_num in range(2, 11):
        time.sleep(5)
        try:
            page_link = driver.find_element(By.XPATH, f'//a[@onclick="fn_pageview({page_num});return false; "]')

            driver.execute_script("arguments[0].click();", page_link)
            print(f"Clicked on page {page_num}")
            new_data = get_table_data(keywords=system_keyword, num=page_num)
            all_filtered_records.extend(new_data)
            time.sleep(5)
        except Exception as e:
            print(f"Could not click page {page_num}: {e}")
    for data in all_filtered_records:
        pprint.pprint(data)
    return all_filtered_records


def scrape_rwanda_data():
    try:
        return get_data_list()
    finally:
        driver.quit()

