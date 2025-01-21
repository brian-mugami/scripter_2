from ppip import ppip_scraper
from uganda_tenders import ug_scraper
from utils import format_results_as_html, send_email


def main():
    errors = []
    email_content = ""
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
    if errors:
        error_message = "<br>".join(errors)
        send_email(
            subject="Tender Scraper Errors",
            body=f"<h3>The following errors occurred during scraping:</h3><p>{error_message}</p>",
            recipients=["brianmugz1@gmail.com", "themugamis@gmail.com"]
        )

    if email_content:
        try:
            send_email(
                subject="Combined Tenders Results",
                body=email_content,
                recipients=["brianmugz1@gmail.com", "themugamis@gmail.com"]
            )
        except Exception as e:
            send_email(
                subject="Error Sending Tenders Results",
                body=f"<h3>An error occurred while sending the results email:</h3><p>{str(e)}</p>",
                recipients=["brianmugz1@gmail.com", "themugamis@gmail.com"]
            )
    else:
        send_email(
            subject="No Tenders Found",
            body="No tenders matching your search were found for today.",
            recipients=["brianmugz1@gmail.com", "themugamis@gmail.com"]
        )


if __name__ == "__main__":
    main()
