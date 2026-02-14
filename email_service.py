import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
GMAIL_USER = os.getenv('GMAIL_USER', 'dattusrinu1122@gmail.com')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', 'rmnguxwerqmdzzrm')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'dattusrinu1122@gmail.com')

def send_email_with_attachment(to_email, to_name, subject, html_body, pdf_attachment=None, pdf_filename='certificate.pdf'):
    """Send email with optional PDF attachment"""
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"Alumni Network <{GMAIL_USER}>"
        msg['To'] = f"{to_name} <{to_email}>"
        msg['Subject'] = subject
        
        # Attach HTML body
        msg.attach(MIMEText(html_body, 'html'))
        
        # Attach PDF if provided
        if pdf_attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(pdf_attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {pdf_filename}')
            msg.attach(part)
        
        # Connect and send
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Email error: {str(e)}")
        return False

def get_certificate_email_template(name, batch_year, amount, donation_id):
    """Get HTML template for donation certificate email"""
    from datetime import datetime
    
    certificate_number = f'DON-{donation_id:06d}'
    date = datetime.now().strftime('%B %d, %Y')
    payment_id = f'Payment #{donation_id}'
    year = datetime.now().year
    admin_email = ADMIN_EMAIL
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Georgia', serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .email-wrapper {{
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .amount {{
                font-size: 36px;
                color: #28a745;
                font-weight: bold;
                text-align: center;
                margin: 20px 0;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 30px;
                text-align: center;
                color: #666;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="email-wrapper">
            <div class="header">
                <h1>🎓 Thank You for Your Donation!</h1>
            </div>
            <div class="content">
                <p>Dear <strong>{name}</strong>,</p>
                <p>Thank you for your generous donation to the Alumni Network!</p>
                
                <div class="amount">₹ {amount}</div>
                
                <p><strong>Donation Details:</strong></p>
                <ul>
                    <li>Certificate No: {certificate_number}</li>
                    <li>Batch Year: {batch_year}</li>
                    <li>Date: {date}</li>
                </ul>
                
                <p>Your certificate of appreciation is attached to this email.</p>
                
                <p>With gratitude,<br><strong>The Alumni Network Team</strong></p>
            </div>
            <div class="footer">
                <p>© {year} Alumni Network. All rights reserved.</p>
                <p>Contact: {admin_email}</p>
            </div>
        </div>
    </body>
    </html>
    """
 

def send_bulk_email(recipients, subject, message):
    """Send bulk email to multiple recipients"""
    
    success_count = 0
    failed = []
    
    for recipient in recipients:
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto;">
                <h2 style="color: #667eea;">Alumni Network Update</h2>
                <div style="background: #f9f9f9; padding: 20px; border-radius: 10px;">
                    {message}
                </div>
                <p style="color: #666; font-size: 14px; margin-top: 20px;">
                    Best regards,<br>Alumni Network Team
                </p>
            </div>
        </body>
        </html>
        """
        
        if send_email_with_attachment(recipient['email'], recipient['name'], subject, html_body):
            success_count += 1
        else:
            failed.append(recipient['email'])
    
    return {
        'success': success_count,
        'failed': len(failed),
        'failed_emails': failed
    }
