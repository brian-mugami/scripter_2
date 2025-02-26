import os

from dotenv import load_dotenv

from ethiopia_egp import egp_scraper
from ppip import ppip_scraper
from tz_pprea import tz_scrapper
from uganda_tenders import ug_scraper
from utils import format_results_as_html, send_email
from world_bank import wb_scrape

load_dotenv()

error_email_1 = os.environ.get("ERROR_EMAIL_1")
email_1 = os.environ.get("RECEIPT_EMAIL_1")
email_2 = os.environ.get("RECEIPT_EMAIL_2")
email_3 = os.environ.get("RECEIPT_EMAIL_3")
email_4 = os.environ.get("RECEIPT_EMAIL_4")
email_5 = os.environ.get("RECEIPT_EMAIL_5")

all = [email_5, email_4, email_2, email_3, email_1]


def main():
    errors = []
    email_content = ""
    try:
        eg_results = egp_scraper()
        if eg_results:
            eg_html = format_results_as_html(eg_results)
            email_content += f"<h2>Ethiopia Tenders</h2>{eg_html}<br>"
    except Exception as e:
        errors.append(f"Ethiopia scraper failed: {str(e)}")
    try:
        tz_results = tz_scrapper()
        if tz_results:
            tz_html = format_results_as_html(tz_results)
            email_content += f"<h2>TZ Tenders</h2>{tz_html}<br>"
    except Exception as e:
        errors.append(f"Tz scraper failed: {str(e)}")
    try:
        ppip_results = ppip_scraper()
        if ppip_results:
            ppip_html = format_results_as_html(ppip_results)
            email_content += f"<h2>PPIP Tenders</h2>{ppip_html}<br>"
    except Exception as e:
        errors.append(f"PPIP scraper failed: {str(e)}")
    try:
        ug_results = ug_scraper()
        if ug_results:
            ug_html = format_results_as_html(ug_results)
            email_content += f"<h2>Uganda Tenders</h2>{ug_html}<br>"
    except Exception as e:
        errors.append(f"Uganda scraper failed: {str(e)}")
    try:
        wb_results = wb_scrape()
        if wb_results:
            wb_html = format_results_as_html(wb_results)
            email_content += f"<h2>World Bank Tenders</h2>{wb_html}<br>"
    except Exception as e:
        errors.append(f"World Bank scraper failed: {str(e)}")
    if errors:
        error_message = "<br>".join(errors)
        send_email(
            subject="Tender Scraper Errors",
            body=f"<h3>The following errors occurred during scraping:</h3><p>{error_message}</p>",
            recipients=[error_email_1]
        )

    if email_content:
        try:
            send_email(
                subject="Combined Tenders Results",
                body=email_content,
                recipients=all
            )
        except Exception as e:
            send_email(
                subject="Error Sending Tenders Results",
                body=f"<h3>An error occurred while sending the results email:</h3><p>{str(e)}</p>",
                recipients=[error_email_1]
            )
    else:
        send_email(
            subject="No Tenders Found",
            body="No tenders matching your search were found for today1.",
            recipients=all
        )


if __name__ == "__main__":
    main()
