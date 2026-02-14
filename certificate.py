from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from datetime import datetime
import io

def generate_certificate_pdf(name, batch_year, amount, donation_id):
    """Generate a professional certificate PDF"""
    
    buffer = io.BytesIO()
    
    # Create PDF in landscape mode
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # Draw border
    c.setStrokeColor(colors.HexColor('#667eea'))
    c.setLineWidth(15)
    c.rect(30, 30, width-60, height-60)
    
    c.setLineWidth(3)
    c.setStrokeColor(colors.HexColor('#764ba2'))
    c.rect(40, 40, width-80, height-80)
    
    # Title
    c.setFont("Helvetica-Bold", 48)
    c.setFillColor(colors.HexColor('#667eea'))
    c.drawCentredString(width/2, height-120, "CERTIFICATE OF APPRECIATION")
    
    # Subtitle
    c.setFont("Helvetica", 24)
    c.setFillColor(colors.HexColor('#764ba2'))
    c.drawCentredString(width/2, height-160, "Alumni Donation")
    
    # Decorative line
    c.setStrokeColor(colors.HexColor('#667eea'))
    c.setLineWidth(2)
    c.line(width/2-200, height-180, width/2+200, height-180)
    
    # Body text
    c.setFont("Helvetica", 18)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2, height-230, "This certificate is proudly presented to")
    
    # Recipient name
    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(colors.HexColor('#667eea'))
    c.drawCentredString(width/2, height-280, name)
    
    # Draw underline for name
    name_width = c.stringWidth(name, "Helvetica-Bold", 36)
    c.setStrokeColor(colors.HexColor('#764ba2'))
    c.setLineWidth(2)
    c.line(width/2 - name_width/2, height-290, width/2 + name_width/2, height-290)
    
    # Batch year
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor('#764ba2'))
    c.drawCentredString(width/2, height-320, f"Batch of {batch_year}")
    
    # Recognition text
    c.setFont("Helvetica", 16)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2, height-370, "In grateful recognition of your generous donation of")
    
    # Amount
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(colors.HexColor('#28a745'))
    c.drawCentredString(width/2, height-410, f"₹ {amount:,.2f}")
    
    # Thank you message
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    text1 = "Your contribution supports our alumni network and helps strengthen"
    text2 = "the bonds of our community. Your generosity makes a lasting impact"
    text3 = "and is deeply appreciated."
    
    c.drawCentredString(width/2, height-460, text1)
    c.drawCentredString(width/2, height-480, text2)
    c.drawCentredString(width/2, height-500, text3)
    
    # Signatures
    date_str = datetime.now().strftime("%B %d, %Y")
    
    # Left signature
    c.setLineWidth(1)
    c.setStrokeColor(colors.black)
    c.line(150, 100, 300, 100)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(225, 85, "Alumni President")
    c.setFont("Helvetica", 10)
    c.drawCentredString(225, 70, date_str)
    
    # Right signature
    c.line(width-300, 100, width-150, 100)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width-225, 85, "Secretary")
    c.setFont("Helvetica", 10)
    c.drawCentredString(width-225, 70, date_str)
    
    # Certificate number
    cert_number = f"DON-{donation_id:06d}"
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.grey)
    c.drawCentredString(width/2, 50, f"Certificate No: {cert_number} | Date: {date_str}")
    
    c.save()
    
    buffer.seek(0)
    return buffer