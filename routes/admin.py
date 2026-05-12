"""
routes/admin.py — Admin: review applications, manage users
"""
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session)
from routes.dashboard import admin_required
import models
from email_service import send_status_change_email
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
mysql = None


def init_admin(mysql_instance):
    global mysql
    mysql = mysql_instance


# ---------------------------------------------------------------------------
# Admin — Overview/Home (main admin page with quick stats)
# ---------------------------------------------------------------------------

@admin_bp.route('/')
@admin_bp.route('/overview')
@admin_required
def overview():
    cur           = models.get_db(mysql)
    stats         = models.get_stats(cur)
    applications  = models.get_all_applications(cur)
    cur.close()
    return render_template('admin/dashboard.html',
                           stats=stats,
                           applications=applications)


# ---------------------------------------------------------------------------
# Admin — Dashboard (statistics page)
# ---------------------------------------------------------------------------

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    cur           = models.get_db(mysql)
    stats         = models.get_stats(cur)
    applications  = models.get_all_applications(cur)
    cur.close()
    return render_template('admin/dashboard.html',
                           stats=stats,
                           applications=applications)

@admin_bp.route('/applications')
@admin_required
def applications():
    status_filter = request.args.get('status', 'all')
    cur           = models.get_db(mysql)
    applications  = models.get_all_applications(cur, status_filter)
    stats         = models.get_stats(cur)
    cur.close()
    return render_template('admin/applications.html',
                           applications=applications,
                           stats=stats,
                           current_filter=status_filter)


# ---------------------------------------------------------------------------
# Admin — approve or reject an application
# ---------------------------------------------------------------------------

@admin_bp.route('/application/<int:app_id>/review', methods=['GET', 'POST'])
@admin_required
def review_application(app_id):
    cur         = models.get_db(mysql)
    application = models.get_application_by_id(cur, app_id)

    if not application:
        cur.close()
        flash('Application not found.', 'danger')
        return redirect(url_for('admin.applications'))

    if request.method == 'POST':
        action  = request.form.get('action')  # 'approved' or 'rejected'
        remarks = request.form.get('remarks', '').strip()

        if action not in ('approved', 'rejected'):
            flash('Invalid action.', 'danger')
            cur.close()
            return redirect(url_for('admin.review_application', app_id=app_id))

        models.update_application_status(cur, app_id, action, remarks)
        mysql.connection.commit()

        # Send email to applicant about status change
        send_status_change_email(
            user_email=application['email'],
            user_name=application['full_name'],
            app_id=app_id,
            permit_type=application['permit_type_name'],
            project_title=application['project_title'],
            status=action,
            decision_date=datetime.now().strftime('%B %d, %Y'),
            remarks=remarks if remarks else None
        )

        cur.close()

        flash(f'Application #{app_id} has been {action}. Notification email sent to applicant.', 'success')
        return redirect(url_for('admin.applications'))

    documents = models.get_documents_by_application(cur, app_id)
    cur.close()
    return render_template('admin/review_application.html',
                           application=application,
                           documents=documents)


# ---------------------------------------------------------------------------
# Admin — user management
# ---------------------------------------------------------------------------

@admin_bp.route('/users')
@admin_required
def users():
    cur       = models.get_db(mysql)
    all_users = models.get_all_users(cur)
    cur.close()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    if user_id == session['user_id']:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))

    cur = models.get_db(mysql)
    models.delete_user(cur, user_id)
    mysql.connection.commit()
    cur.close()

    flash('User deleted.', 'success')
    return redirect(url_for('admin.users'))