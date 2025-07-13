from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import os
from werkzeug.utils import secure_filename
from database import db

auth = Blueprint('auth', __name__, url_prefix='/auth')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth.route('/register')
def register():
    return redirect(url_for('auth.register_step1'))

@auth.route('/register/step1', methods=['GET', 'POST'])
def register_step1():
    if request.method == 'POST':
        # Store step 1 data in session
        session['step1_data'] = {
            'full_name': request.form.get('full_name'),
            'faculty': request.form.get('faculty'),
            'course': request.form.get('course'),
            'group': request.form.get('group'),
            'telegram': request.form.get('telegram'),
            'github': request.form.get('github'),
            'portfolio': request.form.get('portfolio')
        }
        
        # Handle file upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                session['step1_data']['photo'] = filename
        
        return redirect(url_for('auth.register_step2'))
    
    return render_template('auth/register_step1.html')

@auth.route('/register/step2', methods=['GET', 'POST'])
def register_step2():
    if request.method == 'POST':
        purpose = request.form.get('purpose')
        session['step2_data'] = {'purpose': purpose}
        
        # If purpose is "explore", skip step 3 and go to step 4
        if purpose == 'explore':
            return redirect(url_for('auth.register_step4'))
        else:
            return redirect(url_for('auth.register_step3'))
    
    return render_template('auth/register_step2.html')

@auth.route('/register/step3', methods=['GET', 'POST'])
def register_step3():
    # Check if we have step2 data
    if 'step2_data' not in session:
        return redirect(url_for('auth.register_step2'))
    
    purpose = session['step2_data']['purpose']
    
    if request.method == 'POST':
        step3_data = {}
        
        if purpose == 'find_people':
            step3_data = {
                'project_description': request.form.get('project_description'),
                'looking_for': request.form.get('looking_for')
            }
        elif purpose == 'join_project':
            step3_data = {
                'what_to_do': request.form.get('what_to_do'),
                'interests': request.form.get('interests'),
                'time_commitment': request.form.getlist('time_commitment')
            }
        elif purpose == 'expand_network':
            step3_data = {
                'meet_with': request.form.getlist('meet_with'),
                'communication_format': request.form.getlist('communication_format'),
                'discuss_topics': request.form.get('discuss_topics')
            }
        
        session['step3_data'] = step3_data
        return redirect(url_for('auth.register_step4'))
    
    return render_template('auth/register_step3.html')

@auth.route('/register/step4', methods=['GET', 'POST'])
def register_step4():
    # Check if we have previous step data
    if 'step1_data' not in session or 'step2_data' not in session:
        return redirect(url_for('auth.register_step1'))
    
    if request.method == 'POST':
        about = request.form.get('about')
        
        if len(about) < 50:
            flash('Описание должно содержать минимум 50 символов', 'error')
            return render_template('auth/register_step4.html')
        
        try:
            # Combine all user data
            user_data = session['step1_data'].copy()
            user_data['purpose'] = session['step2_data']['purpose']
            
            # Get step3 data if it exists
            step3_data = session.get('step3_data')
            
            # Save to database
            user_id = db.save_user_registration(user_data, step3_data, about)
            
            # Clear session data
            session.pop('step1_data', None)
            session.pop('step2_data', None)
            session.pop('step3_data', None)
            
            flash('Регистрация успешно завершена!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Ошибка при регистрации: {str(e)}', 'error')
            return render_template('auth/register_step4.html')
    
    return render_template('auth/register_step4.html') 