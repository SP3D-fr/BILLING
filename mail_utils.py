import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formataddr
import os

def send_mail_with_pdf(smtp_server, smtp_port, smtp_user, smtp_password, sender_name, sender_email, recipient_email, subject, body, pdf_bytes, pdf_filename):
    msg = MIMEMultipart()
    msg['From'] = formataddr((sender_name, sender_email))
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Attach the body text (force utf-8)
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # Attach the PDF
    part = MIMEApplication(pdf_bytes, Name=pdf_filename)
    part['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
    msg.attach(part)

    # Send the email (force utf-8)
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(sender_email, recipient_email, msg.as_string().encode('utf-8'))
