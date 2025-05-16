import smtplib
from email.message import EmailMessage

# CONFIG — replace with your actual email and app password
EMAIL_SENDER = "21f3002571@ds.study.iitm.ac.in"
EMAIL_PASSWORD = "maum pygk krgy bxxv"

def send_feedback_email(to_email: str, chat_transcript: str):
    msg = EmailMessage()
    msg['Subject'] = "Your Chat Summary & Feedback Request"
    msg['From'] = EMAIL_SENDER
    msg['To'] = to_email

    msg.set_content(f"""
Hi there,

Thank you for chatting with our support bot!

Here’s a summary of your conversation:
----------------------------
{chat_transcript}
----------------------------

We'd love to hear your thoughts. Please reply to this email with your feedback.

Best,
The Support Team
    """)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("✅ Email sent successfully")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
