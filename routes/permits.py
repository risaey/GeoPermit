"""
routes/permits.py — Submit application, view status, hazard check API
"""
import os
import uuid
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session, jsonify, current_app)
from werkzeug.utils import secure_filename
from routes.dashboard import login_required
import models

permits_bp = Blueprint('permits', __name__)
mysql = None


def init_permits(mysql_instance):
    global mysql
    mysql = mysql_instance


def allowed_file(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in current_app.config['ALLOWED_EXTENSIONS']


# ---------------------------------------------------------------------------
# User — submit new application
# ---------------------------------------------------------------------------

@permits_bp.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    cur          = models.get_db(mysql)
    permit_types = models.get_all_permit_types(cur)

    if request.method == 'POST':
        permit_type_id      = request.form.get('permit_type_id')
        project_title       = request.form.get('project_title', '').strip()
        project_description = request.form.get('project_description', '').strip()
        lat                 = request.form.get('lat')
        lng                 = request.form.get('lng')
        address             = request.form.get('address', '').strip()

        # Validation
        if not all([permit_type_id, project_title, lat, lng]):
            flash('Please fill in all required fields and pin a location on the map.', 'danger')
            cur.close()
            return render_template('apply.html', permit_types=permit_types)

        try:
            lat = float(lat)
            lng = float(lng)
        except ValueError:
            flash('Invalid location coordinates.', 'danger')
            cur.close()
            return render_template('apply.html', permit_types=permit_types)

        # GIS hazard check
        hazard_zones = models.check_hazard(cur, lat, lng)
        is_hazard    = len(hazard_zones) > 0
        hazard_info  = '; '.join(
            f"{z['name']} ({z['hazard_type']})" for z in hazard_zones
        ) if is_hazard else None

        # Create application record
        app_id = models.create_application(
            cur,
            user_id=session['user_id'],
            permit_type_id=permit_type_id,
            project_title=project_title,
            project_description=project_description,
            lat=lat, lng=lng, address=address,
            is_hazard=is_hazard,
            hazard_info=hazard_info
        )

        # Handle file uploads
        upload_dir = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        files = request.files.getlist('documents')
        for f in files:
            if f and f.filename and allowed_file(f.filename):
                ext      = f.filename.rsplit('.', 1)[-1].lower()
                new_name = f"{uuid.uuid4().hex}.{ext}"
                f.save(os.path.join(upload_dir, new_name))
                models.save_document(cur, app_id, new_name, secure_filename(f.filename), ext)

        mysql.connection.commit()
        cur.close()

        if is_hazard:
            flash(f'Application submitted. ⚠️ Warning: selected location is in a hazard zone ({hazard_info}).', 'warning')
        else:
            flash('Application submitted successfully!', 'success')
        return redirect(url_for('permits.my_applications'))

    cur.close()
    return render_template('apply.html', permit_types=permit_types)


# ---------------------------------------------------------------------------
# User — view own applications
# ---------------------------------------------------------------------------

@permits_bp.route('/my-applications')
@login_required
def my_applications():
    cur          = models.get_db(mysql)
    applications = models.get_applications_by_user(cur, session['user_id'])
    cur.close()
    return render_template('my_applications.html', applications=applications)


# ---------------------------------------------------------------------------
# View single application (user sees own; admin sees any)
# ---------------------------------------------------------------------------

@permits_bp.route('/application/<int:app_id>')
@login_required
def view_application(app_id):
    cur         = models.get_db(mysql)
    application = models.get_application_by_id(cur, app_id)

    if not application:
        cur.close()
        flash('Application not found.', 'danger')
        return redirect(url_for('permits.my_applications'))

    # Non-admins can only see their own
    if session.get('user_role') != 'admin' and application['user_id'] != session['user_id']:
        cur.close()
        flash('Access denied.', 'danger')
        return redirect(url_for('permits.my_applications'))

    documents = models.get_documents_by_application(cur, app_id)
    cur.close()
    return render_template('view_application.html',
                           application=application,
                           documents=documents)


# ---------------------------------------------------------------------------
# API — hazard check (called by Leaflet map via fetch)
# ---------------------------------------------------------------------------

@permits_bp.route('/api/check-hazard')
@login_required
def api_check_hazard():
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid coordinates'}), 400

    cur   = models.get_db(mysql)
    zones = models.check_hazard(cur, lat, lng)
    cur.close()

    return jsonify({
        'is_hazard': len(zones) > 0,
        'zones': [
            {
                'name': z['name'],
                'hazard_type': z['hazard_type'],
                'description': z['description'],
                'distance_m': z['distance_m'],
            }
            for z in zones
        ]
    })


# ---------------------------------------------------------------------------
# API — permit type requirements (called on dropdown change)
# ---------------------------------------------------------------------------

@permits_bp.route('/api/permit-requirements/<int:permit_type_id>')
@login_required
def api_permit_requirements(permit_type_id):
    cur         = models.get_db(mysql)
    permit_type = models.get_permit_type_by_id(cur, permit_type_id)
    cur.close()

    if not permit_type:
        return jsonify({'error': 'Not found'}), 404

    return jsonify({
        'name': permit_type['name'],
        'description': permit_type['description'],
        'required_docs': permit_type['required_docs'],
    })
