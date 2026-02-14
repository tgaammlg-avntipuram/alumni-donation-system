from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import razorpay
import os
from datetime import datetime
from database import *
from email_service import *
from certificate import generate_certificate_pdf

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Razorpay configuration
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', 'rzp_test_SFzwVpWGa62eE9')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '7TRTxl12pzlXqq1KvwgHBsvj')

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Initialize database on startup
init_db()

@app.route('/')
def index():
    """Public donation page"""
    stats = get_donation_stats()
    return render_template('index.html', 
                         razorpay_key=RAZORPAY_KEY_ID,
                         stats=stats)

@app.route('/api/create-order', methods=['POST'])
def create_order():
    """Create Razorpay order"""
    try:
        data = request.json
        amount = int(float(data['amount']) * 100)  # Convert to paise
        
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f"receipt_{datetime.now().timestamp()}",
            'notes': {
                'name': data['name'],
                'email': data['email'],
                'batch_year': data['batch_year']
            }
        }
        
        order = razorpay_client.order.create(data=order_data)
        
        return jsonify({
            'success': True,
            'order_id': order['id'],
            'amount': amount
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/verify-payment', methods=['POST'])
def verify_payment():
    """Verify payment and send certificate"""
    try:
        data = request.json
        
        print("=== Payment Verification Started ===")
        print(f"Order ID: {data.get('razorpay_order_id')}")
        print(f"Payment ID: {data.get('razorpay_payment_id')}")
        
        # Verify signature
        params_dict = {
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        }
        
        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
            print("✓ Signature verified successfully")
        except Exception as sig_error:
            print(f"✗ Signature verification failed: {str(sig_error)}")
            raise Exception(f'Invalid payment signature: {str(sig_error)}')
        
        # Save donation to database
        try:
            donation_id = add_donation(
                name=data['name'],
                email=data['email'],
                batch_year=int(data['batch_year']),
                amount=float(data['amount']),
                payment_id=data['razorpay_payment_id'],
                order_id=data['razorpay_order_id'],
                message=data.get('message', '')
            )
            print(f"✓ Donation saved with ID: {donation_id}")
        except Exception as db_error:
            print(f"✗ Database error: {str(db_error)}")
            raise Exception(f'Database error: {str(db_error)}')
        
        # Generate certificate PDF
        try:
            pdf_buffer = generate_certificate_pdf(
                name=data['name'],
                batch_year=int(data['batch_year']),
                amount=float(data['amount']),
                donation_id=donation_id
            )
            print("✓ Certificate PDF generated")
        except Exception as pdf_error:
            print(f"⚠ Certificate generation error: {str(pdf_error)}")
            # Continue even if PDF fails
            pdf_buffer = None
        
        # Send email with certificate
        email_sent = False
        try:
            email_template = get_certificate_email_template(
                name=data['name'],
                batch_year=int(data['batch_year']),
                amount=float(data['amount']),
                donation_id=donation_id
            )
            
            email_sent = send_email_with_attachment(
                to_email=data['email'],
                to_name=data['name'],
                subject='Thank You for Your Donation - Certificate Attached',
                html_body=email_template,
                pdf_attachment=pdf_buffer,
                pdf_filename=f'donation_certificate_{donation_id}.pdf'
            )
            
            if email_sent:
                mark_certificate_sent(donation_id)
                add_email_log(data['email'], 'Donation Certificate', 'sent')
                print("✓ Email sent successfully")
            else:
                print("⚠ Email sending failed")
        except Exception as email_error:
            print(f"⚠ Email error: {str(email_error)}")
            # Continue even if email fails
        
        # Send notification to admin
        try:
            send_email_with_attachment(
                to_email=ADMIN_EMAIL,
                to_name='Admin',
                subject=f'New Donation Received - ₹{data["amount"]}',
                html_body=f"""
                <h3>New Donation Received</h3>
                <p><strong>Donor:</strong> {data['name']}</p>
                <p><strong>Batch:</strong> {data['batch_year']}</p>
                <p><strong>Amount:</strong> ₹{data['amount']}</p>
                <p><strong>Payment ID:</strong> {data['razorpay_payment_id']}</p>
                """
            )
            print("✓ Admin notification sent")
        except Exception as admin_error:
            print(f"⚠ Admin notification error: {str(admin_error)}")
        
        print("=== Payment Verification Completed Successfully ===")
        
        return jsonify({
            'success': True,
            'donation_id': donation_id,
            'email_sent': email_sent
        })
        
    except Exception as e:
        print(f"✗✗✗ VERIFICATION ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'message': str(e)
        }), 400

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = verify_admin(username, password)
        
        if admin:
            session['admin_id'] = admin['id']
            session['admin_username'] = admin['username']
            session['admin_name'] = admin['full_name']
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    stats = get_donation_stats()
    donations = get_all_donations()
    
    return render_template('admin_dashboard.html',
                         admin_name=session.get('admin_name'),
                         stats=stats,
                         donations=donations)

@app.route('/admin/send-email', methods=['POST'])
def admin_send_email():
    """Send bulk emails"""
    if 'admin_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        email_type = data['type']  # 'batch', 'all', 'custom'
        subject = data['subject']
        message = data['message']
        
        recipients = []
        
        if email_type == 'batch':
            batch_year = int(data['batch_year'])
            alumni = get_alumni_by_batch(batch_year)
            recipients = [{'email': a['email'], 'name': a['name']} for a in alumni]
            
        elif email_type == 'all':
            alumni = get_alumni_by_batch()
            recipients = [{'email': a['email'], 'name': a['name']} for a in alumni]
            
        elif email_type == 'custom':
            emails = data['emails']  # List of emails
            recipients = [{'email': e, 'name': 'Alumni'} for e in emails]
        
        result = send_bulk_email(recipients, subject, message)
        
        return jsonify({
            'success': True,
            'sent': result['success'],
            'failed': result['failed']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
