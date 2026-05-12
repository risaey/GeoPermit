"""
email_service.py — Email sending service
Sends REAL emails via Gmail SMTP
"""
from flask_mail import Mail, Message

mail = Mail()


def send_application_submitted_email(user_email, user_name, app_id, project_title, permit_type, submitted_date=None, is_hazard=False, hazard_info=None):
    """Send confirmation email when applicant submits an application"""
    try:
        subject = f"Application Submitted - GeoPermit #{app_id}"
        
        body = f"""
Dear {user_name},

Thank you for submitting your permit application!

Application Details:
- Application ID: {app_id}
- Project Title: {project_title}
- Permit Type: {permit_type}
"""
        
        if submitted_date:
            body += f"- Submitted Date: {submitted_date}\n"
        
        if is_hazard and hazard_info:
            body += f"\n⚠️ HAZARD ZONE WARNING:\n{hazard_info}\n"
        
        body += """
Your application has been received and will be reviewed by our admin team.
You will receive an update once the review is complete.

If you have any questions, please contact our office.

Best regards,
GeoPermit System
"""

        msg = Message(subject=subject, recipients=[user_email], body=body)
        mail.send(msg)
        print(f"✅ Sent application submission email to {user_email}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending application submission email: {e}")
        return False


def send_application_submitted_admin_email(app_id, user_name, user_email, permit_type, project_title, location=None, submitted_date=None, is_hazard=False, hazard_info=None, review_link=None):
    """Send notification email to admin when applicant submits an application"""
    try:
        subject = f"New Application Submitted - #{app_id}"
        
        body = f"""
New permit application submitted!

Applicant: {user_name}
Email: {user_email}
Application ID: {app_id}
Project Title: {project_title}
Permit Type: {permit_type}
"""
        
        if location:
            body += f"Location: {location}\n"
        
        if submitted_date:
            body += f"Submitted Date: {submitted_date}\n"
        
        if is_hazard and hazard_info:
            body += f"\n⚠️ HAZARD ZONE:\n{hazard_info}\n"
        
        if review_link:
            body += f"\nReview Application: {review_link}\n"
        
        body += """
Please review and process this application in the admin dashboard.

GeoPermit System
"""

        msg = Message(subject=subject, recipients=['admin@geopermit.gov'], body=body)
        mail.send(msg)
        print(f"✅ Sent admin notification email for application #{app_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending admin notification email: {e}")
        return False


def send_status_change_email(user_email, user_name, app_id, permit_type, project_title, status, decision_date, remarks=None):
    """Send approval/rejection email to applicant"""
    try:
        subject = f"Your Application #{app_id} has been {status.upper()}"
        
        body = f"""
Dear {user_name},

Your permit application for "{project_title}" has been {status.upper()}.

Application Details:
- Application ID: {app_id}
- Permit Type: {permit_type}
- Status: {status.upper()}
- Decision Date: {decision_date}

"""
        
        if remarks:
            body += f"Admin Remarks:\n{remarks}\n\n"
        
        body += """
If you have any questions, please contact our office.

Best regards,
GeoPermit System
"""

        msg = Message(subject=subject, recipients=[user_email], body=body)
        mail.send(msg)
        print(f"✅ Sent status change email to {user_email}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending status change email: {e}")
        return False