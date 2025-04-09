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
Title = "Nigeria Tenders(E Bid Nigeria)"
options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)
et_url = "https://ebid.com.ng/"
timeout = 30
driver.get(et_url)


def get_table_data(keywords, num=1):
    table = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//table')))

    headings = [heading.text.strip() for heading in table.find_elements(By.XPATH, './/thead//tr//th')]

    rows = table.find_elements(By.XPATH, './/tbody//tr')

    table_data = []
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        row_data = [cell.text.strip() for cell in cells]
        row_dict = dict(zip(headings, row_data))
        row_dict = {k: v for k, v in row_dict.items() if k.strip()}
        row_dict["title"] = Title
        row_dict["link"] = cells[0].find_element(by=By.XPATH, value=".//a").get_attribute("href")
        row_dict["page"] = num
        tender_name = row_dict.get("Title", "").lower()
        if any(keyword.lower() in tender_name for keyword in keywords):
            table_data.append(row_dict)
    return table_data


def get_data_list():
    all_filtered_data = []
    initial_data = get_table_data(system_keyword)
    all_filtered_data.extend(initial_data)
    for page_num in range(2, 10):
        retries = 3
        success = False
        while retries > 0 and not success:
            try:
                next_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable(
                        (By.XPATH,
                         '//div[@class="posts-table-below posts-table-controls"]//a[@class="paginate_button next"]')))
                driver.execute_script("arguments[0].scrollIntoView();", next_button)
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(3)
                new_data = get_table_data(keywords=system_keyword, num=page_num)
                all_filtered_data.extend(new_data)
                success = True
            except Exception as e:
                print(f"Could not click page {page_num} (retry {3 - retries + 1}): {e}")
                time.sleep(2)
                retries -= 1
    for data in all_filtered_data:
        pprint.pprint(data)
    return all_filtered_data


def ng_ebid_scrapper():
    try:
        return get_data_list()
    finally:
        driver.quit()
