from flask import Flask, render_template, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from datetime import datetime

app = Flask(__name__)

# Country-State-City Data
COUNTRIES_DATA = {
    "India": {
        "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Tirupati"],
        "Karnataka": ["Bangalore", "Mysore", "Hubli", "Mangalore", "Belgaum"],
        "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"],
        "Delhi": ["New Delhi", "North Delhi", "South Delhi", "East Delhi", "West Delhi"],
        "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar"],
        "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer"],
        "Uttar Pradesh": ["Lucknow", "Kanpur", "Ghaziabad", "Agra", "Varanasi"],
        "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri"],
    },
    "United States": {
        "California": ["Los Angeles", "San Francisco", "San Diego", "Sacramento"],
        "New York": ["New York City", "Buffalo", "Rochester", "Albany"],
        "Texas": ["Houston", "Dallas", "Austin", "San Antonio"]
    },
    "United Kingdom": {
        "England": ["London", "Manchester", "Birmingham", "Liverpool"],
        "Scotland": ["Edinburgh", "Glasgow", "Aberdeen", "Dundee"],
    },
    "Canada": {
        "Ontario": ["Toronto", "Ottawa", "Mississauga", "Hamilton"],
        "Quebec": ["Montreal", "Quebec City", "Laval", "Gatineau"],
    }
}

# Email Configuration
EMAIL_CONFIG = {
    'sender_email': 'amanpandit4756@gmail.com',  # Replace with your email
    'sender_password': 'agyb kiry rorx wroq',   # Replace with your app password
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 465
}

def validate_mobile(mobile):
    """Validate 10-digit mobile number"""
    return bool(re.match(r'^\d{10}$', mobile))

def validate_email(email):
    """Validate email format"""
    if not email:
        return True
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

def send_confirmation_email(name, email, amount, donation_for, donation_type):
    """Send confirmation email to donor"""
    if not email:
        return True, "No email provided"
    
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = "Thank You for Your Donation"
        message["From"] = EMAIL_CONFIG['sender_email']
        message["To"] = email
        
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #4CAF50; border-bottom: 3px solid #4CAF50; padding-bottom: 10px;">
                        Thank You for Your Generous Donation!
                    </h2>
                    <p style="font-size: 16px; color: #333;">Dear <strong>{name}</strong>,</p>
                    
                    <p style="font-size: 16px; color: #333; line-height: 1.6;">
                        We sincerely thank you for your generous donation. Your contribution will make 
                        a significant difference in the lives of those we serve.
                    </p>
                    
                    <div style="background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #333; margin-top: 0;">Donation Details:</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; color: #666;"><strong>Amount:</strong></td>
                                <td style="padding: 8px 0; color: #333;">₹{amount}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #666;"><strong>Donation For:</strong></td>
                                <td style="padding: 8px 0; color: #333;">{donation_for}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #666;"><strong>Payment Method:</strong></td>
                                <td style="padding: 8px 0; color: #333;">{donation_type}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #666;"><strong>Date:</strong></td>
                                <td style="padding: 8px 0; color: #333;">{datetime.now().strftime('%B %d, %Y')}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <p style="font-size: 16px; color: #333; line-height: 1.6;">
                        Your support helps us continue our mission and make a positive impact in the community.
                    </p>
                    
                    <p style="font-size: 16px; color: #333; line-height: 1.6;">
                        If you have any questions or need a receipt for tax purposes, please don't hesitate to contact us.
                    </p>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                        <p style="color: #666; margin-bottom: 5px;">Warm regards,</p>
                        <p style="color: #333; font-weight: bold; margin-top: 5px;">The Donation Team</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        part = MIMEText(html, "html")
        message.attach(part)
        
        with smtplib.SMTP_SSL(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            server.sendmail(EMAIL_CONFIG['sender_email'], email, message.as_string())
        
        return True, "Email sent successfully"
    except Exception as e:
        return False, f"Email sending failed: {str(e)}"

@app.route('/')
def index():
    """Render donation form"""
    return render_template('index.html', countries=list(COUNTRIES_DATA.keys()))

@app.route('/api/states/<country>')
def get_states(country):
    """API endpoint to get states for a country"""
    if country in COUNTRIES_DATA:
        return jsonify(list(COUNTRIES_DATA[country].keys()))
    return jsonify([])

@app.route('/api/cities/<country>/<state>')
def get_cities(country, state):
    """API endpoint to get cities for a state"""
    if country in COUNTRIES_DATA and state in COUNTRIES_DATA[country]:
        return jsonify(COUNTRIES_DATA[country][state])
    return jsonify([])

@app.route('/submit', methods=['POST'])
def submit_donation():
    """Process donation form submission"""
    try:
        # Get form data
        data = request.form
        
        name = data.get('name', '').strip()
        mobile = data.get('mobile', '').strip()
        email = data.get('email', '').strip()
        address = data.get('address', '').strip()
        country = data.get('country', '').strip()
        state = data.get('state', '').strip()
        city = data.get('city', '').strip()
        donation_for = data.get('donation_for', '').strip()
        amount = data.get('amount', '').strip()
        donation_type = data.get('donation_type', '').strip()
        
        # Validation
        errors = []
        
        if not name:
            errors.append("Name is required")
        
        if not mobile:
            errors.append("Mobile number is required")
        elif not validate_mobile(mobile):
            errors.append("Mobile number must be 10 digits")
        
        if email and not validate_email(email):
            errors.append("Invalid email format")
        
        if not country:
            errors.append("Country is required")
        
        if not state:
            errors.append("State is required")
        
        if not city:
            errors.append("City is required")
        
        if not donation_for:
            errors.append("Donation purpose is required")
        
        if not amount:
            errors.append("Donation amount is required")
        else:
            try:
                amount_float = float(amount)
                if amount_float <= 0:
                    errors.append("Donation amount must be greater than 0")
            except ValueError:
                errors.append("Donation amount must be a valid number")
        
        if not donation_type:
            errors.append("Donation type is required")
        
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400
        
        # Send confirmation email
        email_sent, email_message = send_confirmation_email(
            name, email, amount, donation_for, donation_type
        )
        
        # Here you can add code to save to database
        # save_to_database(data)
        
        return jsonify({
            'success': True,
            'message': f'Thank you {name}! Your donation of ₹{amount} has been registered successfully.',
            'email_sent': email_sent,
            'email_message': email_message
        })
        
    except Exception as e:
        return jsonify({'success': False, 'errors': [str(e)]}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)