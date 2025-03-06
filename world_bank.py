import time

from dotenv import load_dotenv
from langdetect import detect
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from language_utils import translate_to_english
from utils import african_countries, system_keyword

load_dotenv()
service = Service(ChromeDriverManager().install())
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)
Title = "World Bank Tenders"
wb_url = "https://projects.worldbank.org/en/projects-operations/procurement?srce=both"


def get_filtered_table_data(pages, keywords, page_no: int = None, url: str = None):
    data_list = []

    if keywords:
        keywords = {kw.lower() for kw in keywords}

    try:
        new_contents = pages.find_element(by=By.TAG_NAME, value="tbody")
        rows = new_contents.find_elements(by=By.TAG_NAME, value="tr")

        for row in rows:
            try:
                each_column = row.find_elements(by=By.TAG_NAME, value="td")
                original_text = each_column[0].text
                language = detect(original_text) if original_text else "en"

                trans_text = translate_to_english(original_text) if language != "en" else original_text

                if (
                        each_column[1].text in african_countries
                        and any(keyword in trans_text.lower() for keyword in keywords)
                        and "Contract Award" not in each_column[3].text
                ):
                    url_link_element = each_column[2].find_element(By.TAG_NAME,
                                                                   "a")  # Look for <a> inside the first column
                    url_link = url_link_element.get_attribute("href") if url_link_element else None
                    data_list.append({
                        "description": original_text,
                        "translated_description": trans_text,
                        "country": each_column[1].text,
                        "page_no": page_no,
                        "title": Title,
                        "link": url_link if url_link else url,
                        "tender_title": each_column[2].text,
                        "notice_type": each_column[3].text,
                        "language": each_column[4].text,
                        "publish_date": each_column[5].text
                    })

            except StaleElementReferenceException:
                print("Stale element encountered; skipping row.")
            except IndexError:
                print("Skipping row due to missing columns.")
            except Exception as e:
                print(f"Error processing row: {e}")

    except NoSuchElementException:
        print("Table body not found.")
    except Exception as e:
        print(f"Error retrieving table: {e}")
    return data_list


def scrape_data(url):
    filtered_data = []
    driver.get(url)
    btn = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//ul[@class="pagination ng-star-inserted"]'))
    )
    table = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//table'))
    )
    data = get_filtered_table_data(table, system_keyword, page_no=1, url=wb_url)
    filtered_data.extend(data)
    buttons = btn.find_elements(By.XPATH, "./li/a")[2:-2]
    page = 2
    for button in buttons:
        time.sleep(10)
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        try:
            button.click()
            time.sleep(5)
            table = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//table'))
            )
            new_data = get_filtered_table_data(pages=table, keywords=system_keyword, page_no=page, url=wb_url)
            filtered_data.extend(new_data)
        except Exception as e:
            print(f"Exception occurred while clicking the button: {e}")
    return filtered_data


def wb_scrape():
    try:
        return scrape_data(wb_url)
    finally:
        driver.quit()
