"""
email_service.py — Email notification functions
Sends emails for permit submissions and status updates
"""
from flask import render_template_string, current_app
from flask_mail import Mail, Message
import threading

mail = Mail()

# Email templates
SUBMIT_EMAIL_USER = """
<html>
  <head>
    <style>
      body { font-family: Arial, sans-serif; }
      .container { max-width: 600px; margin: 0 auto; padding: 20px; }
      .header { background: linear-gradient(135deg, #0d5e3a, #1565a0); color: white; padding: 20px; border-radius: 8px; }
      .content { margin: 20px 0; }
      .footer { color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 10px; }
      .highlight { background: #e8f5ee; padding: 10px; border-left: 4px solid #0d5e3a; margin: 10px 0; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h2>🎉 Permit Application Submitted</h2>
      </div>
      <div class="content">
        <p>Dear <strong>{{ user_name }}</strong>,</p>
        <p>Your permit application has been successfully submitted!</p>
        
        <div class="highlight">
          <strong>Application Details:</strong><br>
          <strong>Application ID:</strong> #{{ app_id }}<br>
          <strong>Permit Type:</strong> {{ permit_type }}<br>
          <strong>Project Title:</strong> {{ project_title }}<br>
          <strong>Submitted Date:</strong> {{ submitted_date }}<br>
          <strong>Status:</strong> <span style="color: #f59e0b;">⏳ Pending Review</span>
        </div>

        {% if is_hazard %}
        <div style="background: #fff8f0; border: 2px solid #ff9800; padding: 15px; border-radius: 8px; margin: 15px 0;">
          <strong style="color: #e65100;">⚠️  Hazard Zone Alert</strong><br>
          <p style="margin: 10px 0 0 0; font-size: 14px;">
            Your project location is in a hazard-prone area. The admin may request additional documentation.
          </p>
        </div>
        {% endif %}

        <p>You can check your application status anytime by logging into your GeoPermit account.</p>
        
        <p style="color: #666; margin-top: 20px;">
          If you have any questions, please contact the admin at <strong>admin@geopermit.gov</strong>
        </p>
      </div>
      
      <div class="footer">
        <p>This is an automated email from GeoPermit System. Please do not reply to this email.</p>
        <p>&copy; 2024 GeoPermit System. All rights reserved.</p>
      </div>
    </div>
  </body>
</html>
"""

SUBMIT_EMAIL_ADMIN = """
<html>
  <head>
    <style>
      body { font-family: Arial, sans-serif; }
      .container { max-width: 600px; margin: 0 auto; padding: 20px; }
      .header { background: #d32f2f; color: white; padding: 20px; border-radius: 8px; }
      .content { margin: 20px 0; }
      .footer { color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 10px; }
      .highlight { background: #fff3e0; padding: 10px; border-left: 4px solid #f57c00; margin: 10px 0; }
      .btn { background: #0d5e3a; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; display: inline-block; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h2>📋 New Application to Review</h2>
      </div>
      <div class="content">
        <p>A new permit application has been submitted and requires your review.</p>
        
        <div class="highlight">
          <strong>Application Details:</strong><br>
          <strong>Application ID:</strong> #{{ app_id }}<br>
          <strong>Applicant:</strong> {{ user_name }} ({{ user_email }})<br>
          <strong>Permit Type:</strong> {{ permit_type }}<br>
          <strong>Project Title:</strong> {{ project_title }}<br>
          <strong>Location:</strong> {{ location }}<br>
          <strong>Submitted:</strong> {{ submitted_date }}
        </div>

        {% if is_hazard %}
        <div style="background: #ffebee; border: 2px solid #d32f2f; padding: 15px; border-radius: 8px; margin: 15px 0;">
          <strong style="color: #991b1b;">🚨 HAZARD ZONE APPLICATION</strong><br>
          <p style="margin: 10px 0 0 0; font-size: 14px;">
            {{ hazard_info }}
          </p>
        </div>
        {% endif %}

        <p style="margin-top: 20px;">
          <a href="{{ review_link }}" class="btn">Review Application</a>
        </p>
      </div>
      
      <div class="footer">
        <p>This is an automated notification from GeoPermit System.</p>
      </div>
    </div>
  </body>
</html>
"""

STATUS_CHANGE_EMAIL = """
<html>
  <head>
    <style>
      body { font-family: Arial, sans-serif; }
      .container { max-width: 600px; margin: 0 auto; padding: 20px; }
      .header { padding: 20px; border-radius: 8px; color: white; }
      .header.approved { background: linear-gradient(135deg, #4caf50, #388e3c); }
      .header.rejected { background: linear-gradient(135deg, #f44336, #d32f2f); }
      .content { margin: 20px 0; }
      .footer { color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 10px; }
      .highlight { padding: 10px; border-radius: 4px; margin: 10px 0; }
      .highlight.approved { background: #e8f5e9; border-left: 4px solid #4caf50; }
      .highlight.rejected { background: #ffebee; border-left: 4px solid #f44336; }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header {{ status }}">
        <h2>
          {% if status == 'approved' %}
            ✅ Your Application Has Been Approved!
          {% else %}
            ❌ Your Application Has Been Rejected
          {% endif %}
        </h2>
      </div>
      <div class="content">
        <p>Dear <strong>{{ user_name }}</strong>,</p>
        
        <p>
          {% if status == 'approved' %}
            Great news! Your permit application has been <strong style="color: #4caf50;">APPROVED</strong>.
          {% else %}
            Unfortunately, your permit application has been <strong style="color: #f44336;">REJECTED</strong>.
          {% endif %}
        </p>
        
        <div class="highlight {{ status }}">
          <strong>Application Details:</strong><br>
          <strong>Application ID:</strong> #{{ app_id }}<br>
          <strong>Permit Type:</strong> {{ permit_type }}<br>
          <strong>Project Title:</strong> {{ project_title }}<br>
          <strong>Decision Date:</strong> {{ decision_date }}
        </div>

        {% if remarks %}
        <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 15px 0;">
          <strong>Admin Remarks:</strong><br>
          <p style="margin: 10px 0 0 0; font-size: 14px;">{{ remarks }}</p>
        </div>
        {% endif %}

        <p style="margin-top: 20px; color: #666;">
          You can view the full details of your application in your GeoPermit account.
        </p>
      </div>
      
      <div class="footer">
        <p>This is an automated notification from GeoPermit System.</p>
        <p>&copy; 2024 GeoPermit System. All rights reserved.</p>
      </div>
    </div>
  </body>
</html>
"""


def send_async_email(app, msg):
    """Send email asynchronously so it doesn't block the request"""
    with app.app_context():
        try:
            mail.send(msg)
            print(f"✅ Email sent to {msg.recipients}")
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")


def send_application_submitted_email(user_email, user_name, app_id, permit_type, 
                                     project_title, submitted_date, is_hazard, hazard_info):
    """Send email to user when they submit an application"""
    try:
        # Email to the applicant
        html_body = render_template_string(
            SUBMIT_EMAIL_USER,
            user_name=user_name,
            app_id=app_id,
            permit_type=permit_type,
            project_title=project_title,
            submitted_date=submitted_date,
            is_hazard=is_hazard,
            hazard_info=hazard_info
        )
        
        msg = Message(
            subject=f"Permit Application #{app_id} Submitted Successfully",
            recipients=[user_email],
            html=html_body
        )
        
        # Send asynchronously
        thread = threading.Thread(
            target=send_async_email,
            args=(current_app._get_current_object(), msg)
        )
        thread.daemon = True
        thread.start()
        
        return True
    except Exception as e:
        print(f"Error preparing email: {str(e)}")
        return False


def send_application_submitted_admin_email(app_id, user_name, user_email, permit_type,
                                           project_title, location, submitted_date, 
                                           is_hazard, hazard_info, review_link):
    """Send email to admin when a new application is submitted"""
    try:
        admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@geopermit.gov')
        
        html_body = render_template_string(
            SUBMIT_EMAIL_ADMIN,
            app_id=app_id,
            user_name=user_name,
            user_email=user_email,
            permit_type=permit_type,
            project_title=project_title,
            location=location,
            submitted_date=submitted_date,
            is_hazard=is_hazard,
            hazard_info=hazard_info,
            review_link=review_link
        )
        
        msg = Message(
            subject=f"New Application #{app_id} - {permit_type}",
            recipients=[admin_email],
            html=html_body
        )
        
        # Send asynchronously
        thread = threading.Thread(
            target=send_async_email,
            args=(current_app._get_current_object(), msg)
        )
        thread.daemon = True
        thread.start()
        
        return True
    except Exception as e:
        print(f"Error preparing admin email: {str(e)}")
        return False


def send_status_change_email(user_email, user_name, app_id, permit_type, 
                             project_title, status, decision_date, remarks):
    """Send email to user when application status changes"""
    try:
        html_body = render_template_string(
            STATUS_CHANGE_EMAIL,
            user_name=user_name,
            app_id=app_id,
            permit_type=permit_type,
            project_title=project_title,
            status=status,
            decision_date=decision_date,
            remarks=remarks
        )
        
        status_text = "APPROVED" if status == "approved" else "REJECTED"
        
        msg = Message(
            subject=f"Application #{app_id} {status_text}",
            recipients=[user_email],
            html=html_body
        )
        
        # Send asynchronously
        thread = threading.Thread(
            target=send_async_email,
            args=(current_app._get_current_object(), msg)
        )
        thread.daemon = True
        thread.start()
        
        return True
    except Exception as e:
        print(f"Error preparing email: {str(e)}")
        return False