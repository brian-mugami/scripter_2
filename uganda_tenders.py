from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from utils import get_page, system_keyword

load_dotenv()
service = Service(ChromeDriverManager().install())
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)
Title = "Uganda Public Procurement Tenders"
ug_url = "https://gpp.ppda.go.ug/public/bid-invitations"
ug_xpath = '//div[@class="ng-star-inserted"]'
ug_timeout = 40


def get_filtered_data(keywords, page, url: str = None):
    data_list = []
    if keywords:
        keywords = [kw.lower() for kw in keywords]
    try:
        page_elements = WebDriverWait(page, timeout=10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="px-6 py-4"]')))
        for element in page_elements:
            title = WebDriverWait(element, timeout=10).until(
                EC.presence_of_element_located((By.XPATH,
                                                './/div[@class="mb-2 text-xl font-bold break-all sm:break-words md:break-all lg:truncate xl:break-all"]')))
            if keywords and not any(keyword in title.text.lower() for keyword in keywords):
                continue
            org = WebDriverWait(element, timeout=10).until(
                EC.presence_of_element_located((By.XPATH,
                                                './/div[@class="text-gray-600"]')))
            deadline = WebDriverWait(element, timeout=10).until(
                EC.presence_of_element_located((By.XPATH,
                                                './/span[@class="text-gray-600 ng-star-inserted"]')))
            data_list.append({
                "link": url,
                "organization": org.text,
                "description": title.text,
                "deadline": deadline.text,
                "title": Title
            })
    except Exception as e:
        print("Error extracting data for an element:", str(e))
    for record in data_list:
        print(record)
    return data_list


def ug_scraper():
    try:
        page = get_page(url=ug_url, x_path=ug_xpath, timeout=ug_timeout, driver=driver)
        return get_filtered_data(keywords=system_keyword, page=page, url=ug_url)
    finally:
        driver.quit()
