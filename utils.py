import datetime
import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()

sender_email = os.environ.get("EMAIL")
sender_password = os.environ.get("PASSWORD")


def format_results_as_html(records, title):
    html_content = f"<h3>{title} Search Results {datetime.datetime.now().date()}</h3><table border='1' cellpadding='5' cellspacing='0'>"
    html_content += "<tr><th>Tender No</th><th>Description</th><th>Procuring Entity</th><th>Proc. Method</th><th>Proc. Category</th><th>Publish Date</th><th>Close Date</th><th>Page(when you click the link)</th><th>Link</th></tr>"
    for record in records:
        html_content += f"<tr>" \
                        f"<td>{record['Tender. No']}</td>" \
                        f"<td>{record['Description']}</td>" \
                        f"<td>{record['Procuring_Entity']}</td>" \
                        f"<td>{record['Proc. Method']}</td>" \
                        f"<td>{record['Proc. Category']}</td>" \
                        f"<td>{record['Publish Date']}</td>" \
                        f"<td>{record['Close Date']}</td>" \
                        f"<td>{record['page']}</td>" \
                        f"<td><a href='{record['link']}'>View Tender</a></td>" \
                        f"</tr>"
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


system_keyword = ['SIFMIS', 'IFMIS', 'HARDWARE', "I.C.T", "ENTERPRISE", 'GIFMIS', "consultancy", 'GFS', 'HRMIS', 'PFM',
                  'Public Financial Management', 'Quality Assurance', 'Capacity Building Project',
                  'Capacity Injection Project', 'Enterprise Resource Planning', 'ERP', 'Business Intelligence',
                  'Public Sector Reform', 'Budget Management System', 'Audit Management Information System',
                  'Accountable Governance', 'oracle', 'database', 'server', "backup", "datacenter", "datacentre",
                  "data center", "data centre", 'software', 'servers', 'back up', "I.C.T", "website", "system","data"]
