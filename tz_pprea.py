from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from utils import get_page

load_dotenv()
driver_path = "chromedriver.exe"
service = Service(executable_path=driver_path)
options = Options()
# options.add_argument('--headless')
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
            href = WebDriverWait(element, timeout=10).until(
                EC.presence_of_element_located((By.XPATH, './/a')))
            link = href.get_attribute("href")
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
                "link": link if link else url,
                "title": title.text,
                "organization": org.text,
                "publish_date": date.text,
                "deadline_date": deadline_date.text,
            })
    except Exception as e:
        print("Error extracting data for an element:", str(e))
    return data_list


def scrape_data(url, xpath, timeout):
    try:
        page = get_page(url=url,
                        x_path=xpath,
                        timeout=timeout, driver=driver)
        if page:
            next_button = WebDriverWait(driver, timeout=10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'button')))
            next_button[-1].click()
        else:
            print("Did not click")
    except Exception as e:
        print("No page")
        print(str(e))


scrape_data(tz_url, tz_xpath, tz_timeout)
