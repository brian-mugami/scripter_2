import os
import smtplib
from datetime import datetime
from email.message import EmailMessage

from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

load_dotenv()

sender_email = os.environ.get("EMAIL")
sender_password = os.environ.get("PASSWORD")


def get_page(url: str, timeout: int, x_path: str, driver):
    driver.get(url)
    try:
        first_page = WebDriverWait(driver, timeout=timeout).until(EC.presence_of_element_located(
            (By.XPATH, x_path)
        ))
        return first_page
    except Exception as e:
        print(str(e))
        return None


def format_results_as_html(records):
    if not records:
        return f"<h3>No Search Results Found</h3><p>No results available.</p>"
    title = records[0].get('title', 'Search Results')
    headers = [key for key in records[0].keys() if key != 'title']
    html_content = f"<h3>{title} Search Results {datetime.now().date()}</h3>"
    html_content += "<table border='1' cellpadding='5' cellspacing='0'>"
    html_content += "<tr>"
    for header in headers:
        html_content += f"<th>{header}</th>"
    html_content += "</tr>"
    for record in records:
        html_content += "<tr>"
        for key in headers:
            value = record[key]
            if key.lower() == 'link':
                html_content += f"<td><a href='{value}'>View Tender</a></td>"
            else:
                html_content += f"<td>{value}</td>"
        html_content += "</tr>"

    html_content += "</table>"
    return html_content


def send_email(subject, body, recipients):
    msg = EmailMessage()
    msg["From"] = sender_email
    msg["Subject"] = subject
    msg["To"] = ", ".join(recipients)
    msg.set_content("This email contains HTML content. Please enable HTML view.")
    msg.add_alternative(body, subtype="html")
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(sender_email, sender_password)
            smtp.sendmail(sender_email, recipients, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


system_keyword = ['SIFMIS', 'IFMIS', "I.C.T", "ENTERPRISE", 'GIFMIS', 'GFS', 'HRMIS', 'PFM', "HRMS",
                  "information system", "management system", "human resource", 'Public Financial Management',
                  'Quality Assurance', 'Capacity Building Project', 'Capacity Injection Project',
                  'Enterprise Resource Planning', 'ERP', 'Business Intelligence', 'Public Sector Reform',
                  'Budget Management System', 'Audit Management Information System', 'Accountable Governance', 'oracle',
                  'database', 'server', "backup", "datacenter", "datacentre", "data center", "data centre", 'software',
                  'servers', 'back up', "I.C.T", "website", "data"]

african_countries = [
    "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cabo Verde", "Cameroon",
    "Central African Republic", "Chad", "Comoros", "Congo", "Cote d'Ivoire", "Djibouti", "Egypt",
    "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia", "Gabon", "Gambia", "Ghana", "Guinea",
    "Guinea-Bissau", "Kenya", "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi", "Mali", "Mauritania",
    "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger", "Nigeria", "Rwanda", "Sao Tome and Principe",
    "Senegal", "Seychelles", "Sierra Leone", "Somalia", "South Africa", "South Sudan", "Sudan", "Tanzania",
    "Togo", "Tunisia", "Uganda", "Zambia", "Zimbabwe"
]
