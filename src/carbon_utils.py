import os
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


# Load emission factors from CSV
def load_emission_factors():
    data = pd.read_csv("Carbon_Emission_Factors_195_Countries.csv")
    emission_factors = {
        row['Country']: {
            "Transportation": row['Transportation (kg CO2 per km)'],
            "Electricity": row['Electricity (kg CO2 per kWh)'],
            "Diet": row['Diet (kg CO2 per meal)'],
            "Waste": row['Waste (kg CO2 per kg)']
        }
        for _, row in data.iterrows()
    }
    return emission_factors, data

# Categorize emissions
def categorize_emissions(total_emissions, country, avg_emissions):
    if total_emissions < avg_emissions:
        return "Good", "Your carbon emissions are lower than the average for your country."
    elif total_emissions == avg_emissions:
        return "Moderate", "Your carbon emissions are on par with the average for your country."
    else:
        return "Bad", "Your carbon emissions are higher than the average for your country."


def send_email_smtp(user_email, subject, body, image_path):
    sender_email = os.getenv("SENDER_EMAIL")  # Use environment variables
    sender_password = os.getenv("SENDER_PASSWORD")  # Use App Password
    smtp_server = "smtp.gmail.com"
    smtp_port = 465

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = user_email
    msg["Subject"] = subject

    # Ensure non-ASCII characters do not cause encoding issues
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="background-color: #f4f4f9; padding: 20px; border-radius: 8px;">
            <img src="cid:image1" alt="Carbon Footprint Banner" style="width: 100%; max-width: 600px; display: block; margin: 0 auto;"/>
            <h2 style="color: #4CAF50; text-align: center;">Carbon Footprint Report</h2>
            <p style="font-size: 16px; text-align: center;">Dear User,</p>
            <p style="font-size: 16px; line-height: 1.5; text-align: center;">
                Here is your carbon footprint report for <strong>{subject}</strong>:
            </p>
            <ul style="font-size: 16px; line-height: 1.8;">
                <li><strong>Transportation:</strong> {body['transportation_emissions']} tons</li>
                <li><strong>Electricity:</strong> {body['electricity_emissions']} tons</li>
                <li><strong>Diet:</strong> {body['diet_emissions']} tons</li>
                <li><strong>Waste:</strong> {body['waste_emissions']} tons</li>
                <li><strong>Total Emissions:</strong> {body['total_emissions']} tons</li>
                <li><strong>Emission Category:</strong> {body['category']}</li>
                <li><strong>Country's Total Emissions:</strong> {body['country_emissions']} tons</li>
            </ul>
            <p style="font-size: 16px; text-align: center;">{body['message']}</p>
            <p style="font-size: 16px; text-align: center;">Best regards,</p>
            <p style="font-size: 16px; text-align: center;">Carbon Footprint Calculator Team</p>
        </div>
    </body>
    </html>
    """.replace("\xa0", " ")  # Fix ASCII encoding issue

    msg.attach(MIMEText(html_body, "html", "utf-8"))  # Use UTF-8 encoding

    # Attach Image
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            img_data = img_file.read()
            image = MIMEImage(img_data, name="carbon_report.jpg")
            image.add_header("Content-ID", "<image1>")  # Attach image to email
            msg.attach(image)

    try:
        # Send Email
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user_email, msg.as_string())

        print("✅ Email sent successfully!")
        return True

    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

