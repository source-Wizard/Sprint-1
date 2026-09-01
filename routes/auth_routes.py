import os
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, make_response, flash
from werkzeug.utils import secure_filename
from db import get_db, unique_id

auth_bp = Blueprint('auth', __name__)
UPLOAD_FOLDER = os.path.join('static', 'uploaded_files')

@auth_bp.route('/login.php', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('pass', '').strip()
        hashed_pass = hashlib.sha1(password.encode()).hexdigest()

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM `users` WHERE email = %s AND password = %s LIMIT 1", (email, hashed_pass))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            resp = make_response(redirect(url_for('home.home_page')))
            resp.set_cookie('user_id', user['id'], max_age=60 * 60 * 24 * 30, path='/')
            return resp
        else:
            flash('incorrect email or password!')
    return render_template('login.html')

@auth_bp.route('/register.php', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_new_id = unique_id()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('pass', '').strip()
        cpassword = request.form.get('cpass', '').strip()

        hashed_pass = hashlib.sha1(password.encode()).hexdigest()
        hashed_cpass = hashlib.sha1(cpassword.encode()).hexdigest()

        image_file = request.files.get('image')
        if not image_file or image_file.filename == '':
            flash('please select an image!')
            return render_template('register.html')

        ext = os.path.splitext(secure_filename(image_file.filename))[1]
        rename_image = f"{unique_id()}{ext}"
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        image_path = os.path.join(UPLOAD_FOLDER, rename_image)

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM `users` WHERE email = %s", (email,))
        if cursor.fetchone():
            flash('email already taken!')
        elif hashed_pass != hashed_cpass:
            flash('confirm passowrd not matched!')
        else:
            image_file.save(image_path)
            cursor.execute("INSERT INTO `users`(id, name, email, password, image) VALUES (%s, %s, %s, %s, %s)",
                           (user_new_id, name, email, hashed_cpass, rename_image))
            db.commit()
            cursor.close()
            db.close()
            resp = make_response(redirect(url_for('home.home_page')))
            resp.set_cookie('user_id', user_new_id, max_age=60 * 60 * 24 * 30, path='/')
            return resp
        cursor.close()
        db.close()
    return render_template('register.html')

@auth_bp.route('/logout.php')
@auth_bp.route('/components/user_logout.php')
def logout():
    resp = make_response(redirect(url_for('home.home_page')))
    resp.delete_cookie('user_id', path='/')
    return resp
