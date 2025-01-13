from ppip import ppip_scraper
from utils import format_results_as_html, send_email

if __name__ == "__main__":
    content = ppip_scraper("https://tenders.go.ke/tenders")
    if content:
        try:
            html_content = format_results_as_html(content, title="PPIP")
            send_email(subject="PPIP Tenders", body=html_content,
                       recipients=["brianmugz1@gmail.com", "themugamis@gmail.com",])
        except Exception as e:
            print("Exception caused failure:", str(e))
    else:
        send_email(subject="PPIP Tenders", body="No tenders matching your search for today",
                   recipients=["brianmugz1@gmail.com", "themugamis@gmail.com"])
