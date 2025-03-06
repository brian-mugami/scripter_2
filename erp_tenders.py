from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()
service = Service(ChromeDriverManager().install())
options = Options()
Title = "ERP Tenders Africa"
options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)
erp_url = "https://www.globaltenders.com/af/africa-erp-tenders"
timeout = 30
driver.get(erp_url)


def get_page_data(p_title, url, page=1, ):
    data_list = []
    try:
        tender_card = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="card"]//div[@class="card-body p-0"]'))
        )
        tender_rows = tender_card.find_elements(By.XPATH, './/div[@class="tender-wrap"]')

        for row in tender_rows:
            title_div = row.find_element(By.XPATH, './/div[@title="description"]')
            country_div = row.find_element(By.XPATH, './/div[@title="country"]')
            posting_div = row.find_element(By.XPATH, './/div[@title="Posting Date"]')
            deadline_div = row.find_element(By.XPATH, './/div[@title="Deadline"]')
            link_div = row.find_element(By.TAG_NAME, 'a')
            title = title_div.text
            href = link_div.get_attribute("href")
            country = country_div.text
            p_date = posting_div.text
            d_date = deadline_div.text
            row_data = {
                "tender_title": title,
                "country": country,
                "Publish_Date": p_date,
                "Submission_Deadline": d_date,
                "title": p_title,
                "page": page,
                "link": href,
            }

            data_list.append(row_data)
    except Exception as e:
        print("An error occurred in ERP Tender Scarper", e)
    for data in data_list:
        print(data)
    return data_list


def erp_scraper():
    try:
        return get_page_data(Title, erp_url)
    finally:
        driver.quit()
