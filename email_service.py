import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
GMAIL_USER = os.getenv('GMAIL_USER', 'dattusrinu1122@gmail.com')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'dattusrinu1122@gmail.com')

def send_email_with_attachment(to_email, to_name, subject, html_body, pdf_attachment=None, pdf_filename='certificate.pdf'):
    """Send email using SendGrid API"""
    
    try:
        print(f"Sending email to {to_email} via SendGrid...")
        
        # Create email message
        message = Mail(
            from_email=GMAIL_USER,
            to_emails=to_email,
            subject=subject,
            html_content=html_body
        )
        
        # Add PDF attachment if provided
        if pdf_attachment:
            try:
                pdf_data = pdf_attachment.read()
                encoded_file = base64.b64encode(pdf_data).decode()
                
                attached_file = Attachment(
                    FileContent(encoded_file),
                    FileName(pdf_filename),
                    FileType('application/pdf'),
                    Disposition('attachment')
                )
                message.attachment = attached_file
                print("PDF attachment added")
            except Exception as pdf_err:
                print(f"PDF attachment error: {pdf_err}")
        
        # Send email
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        print(f"✓ Email sent! Status code: {response.status_code}")
        return True
        
    except Exception as e:
        print(f"✗ SendGrid error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def get_certificate_email_template(name, batch_year, amount, donation_id):
    """Get HTML template for donation certificate email"""
    from datetime import datetime
    
    certificate_number = f'DON-{donation_id:06d}'
    date = datetime.now().strftime('%B %d, %Y')
    year = datetime.now().year
    
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
            .details {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
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
                <p>Your generosity makes a difference</p>
            </div>
            <div class="content">
                <p>Dear <strong>{name}</strong>,</p>
                
                <p>On behalf of the entire Alumni Network, we extend our heartfelt gratitude for your generous donation.</p>
                
                <div class="amount">₹ {amount:,.2f}</div>
                
                <div class="details">
                    <p><strong>📋 Donation Details:</strong></p>
                    <ul style="list-style: none; padding: 0;">
                        <li>📅 Date: {date}</li>
                        <li>🎓 Batch Year: {batch_year}</li>
                        <li>🔖 Certificate No: {certificate_number}</li>
                    </ul>
                </div>
                
                <p>Your <strong>Certificate of Appreciation</strong> is attached to this email. Please keep it for your records.</p>
                
                <p>Your contribution supports our alumni network and helps strengthen the bonds of our community.</p>
                
                <p style="margin-top: 30px;">With gratitude,<br><strong>The Alumni Network Team</strong></p>
            </div>
            <div class="footer">
                <p>© {year} Alumni Network. All rights reserved.</p>
                <p>Contact: {ADMIN_EMAIL}</p>
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
                    {message.replace(chr(10), '<br>')}
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
