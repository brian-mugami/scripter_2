import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv

from erp_tenders import erp_scraper
from ethiopia_egp import egp_scraper
from nigeria_ebid import ng_ebid_scrapper
from nigeria_etenders import ng_etenders_scrapper
from nigeria_tenders import ng_procurement_scrapper
from ppip import ppip_scraper
from rwanda_ucwa import scrape_rwanda_data
from tz_pprea import tz_scrapper
from uganda_tenders import ug_scraper
from utils import format_results_as_html, send_email
from world_bank import wb_scrape
from afdb_tenders import afdb_scrape
load_dotenv()

error_email_1 = os.environ.get("ERROR_EMAIL_1")
email_1 = os.environ.get("RECEIPT_EMAIL_1")
email_2 = os.environ.get("RECEIPT_EMAIL_2")
email_3 = os.environ.get("RECEIPT_EMAIL_3")
email_4 = os.environ.get("RECEIPT_EMAIL_4")
email_5 = os.environ.get("RECEIPT_EMAIL_5")
email_6 = os.environ.get("RECEIPT_EMAIL_6")

all = [email_1,email_6,email_5,email_2,email_3,email_4,email_5]
logging.basicConfig(
    filename="scraper_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    errors = []
    email_content = ""
    scrapers = {
        "ERP Tenders Africa": erp_scraper,
        "Ethiopia Tenders": egp_scraper,
        "TZ Tenders": tz_scrapper,
        "PPIP Tenders": ppip_scraper,
        "World Bank Tenders": wb_scrape,
        "Rwanda Tenders": scrape_rwanda_data,
        "Nigeria e-Bid": ng_ebid_scrapper,
        "Nigeria e-Tenders": ng_etenders_scrapper,
        "Nigeria Procurement": ng_procurement_scrapper,
        "Uganda Tenders": ug_scraper,
        "AFDB Tenders":afdb_scrape
    }
    results = {}
    with ThreadPoolExecutor() as executor:
        future_to_name = {executor.submit(scraper): name for name, scraper in scrapers.items()}
        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                result = future.result()
                if result:
                    results[name] = result
            except Exception as e:
                error_msg = f"{name} scraper failed: {str(e)}"
                logging.error(error_msg)
                errors.append(error_msg)

    for name, result in results.items():
        email_content += f"<h2>{name}</h2>{format_results_as_html(result)}<br>"

    if errors:
        send_email(
            subject="Tender Scraper Errors",
            body=f"<h3>The following errors occurred during scraping:</h3><p>{'<br>'.join(errors)}</p>",
            recipients=[error_email_1]
        )

    if email_content:
        send_email(
            subject="Combined Tenders Results(E.Africa, Nigeria, World Bank)",
            body=email_content,
            recipients=all
        )
    else:
        send_email(
            subject="No Tenders Found",
            body="No tenders matching your search were found for today.",
            recipients=all
        )


if __name__ == "__main__":
    main()
