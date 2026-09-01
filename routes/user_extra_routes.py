import os
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from db import get_db, unique_id

user_extra_bp = Blueprint('user_extra', __name__)
UPLOAD_FOLDER = os.path.join('static', 'uploaded_files')

@user_extra_bp.route('/search_course.php', methods=['GET', 'POST'])
def search_course():
    search = request.form.get('search_course', '').strip() if request.method == 'POST' else request.args.get('search_course', '').strip()
    courses = []

    if search:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT p.*, t.name AS tutor_name, t.image AS tutor_image
            FROM `playlist` p
            JOIN `tutors` t ON p.tutor_id = t.id
            WHERE p.title LIKE %s AND p.status = 'active'
            ORDER BY p.date DESC
        """
        cursor.execute(query, (f"%{search}%",))
        courses = cursor.fetchall()
        cursor.close()
        db.close()

    return render_template('search_course.html', search=search, courses=courses)

@user_extra_bp.route('/teachers.php')
def teachers_page():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT t.*,
            (SELECT COUNT(*) FROM `playlist` WHERE tutor_id = t.id) AS total_playlists,
            (SELECT COUNT(*) FROM `content` WHERE tutor_id = t.id) AS total_contents,
            (SELECT COUNT(*) FROM `likes` WHERE tutor_id = t.id) AS total_likes,
            (SELECT COUNT(*) FROM `comments` WHERE tutor_id = t.id) AS total_comments
        FROM `tutors` t
    """
    cursor.execute(query)
    tutors = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('teachers.html', tutors=tutors)

@user_extra_bp.route('/search_tutor.php', methods=['GET', 'POST'])
def search_tutor():
    search = request.form.get('search_tutor', '').strip() if request.method == 'POST' else ''
    tutors = []

    if search:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        query = """
            SELECT t.*,
                (SELECT COUNT(*) FROM `playlist` WHERE tutor_id = t.id) AS total_playlists,
                (SELECT COUNT(*) FROM `content` WHERE tutor_id = t.id) AS total_contents,
                (SELECT COUNT(*) FROM `likes` WHERE tutor_id = t.id) AS total_likes,
                (SELECT COUNT(*) FROM `comments` WHERE tutor_id = t.id) AS total_comments
            FROM `tutors` t
            WHERE t.name LIKE %s
        """
        cursor.execute(query, (f"%{search}%",))
        tutors = cursor.fetchall()
        cursor.close()
        db.close()

    return render_template('search_tutor.html', search=search, tutors=tutors)

@user_extra_bp.route('/tutor_profile.php', methods=['GET', 'POST'])
def tutor_profile():
    tutor_email = request.form.get('tutor_email', '').strip() if request.method == 'POST' else request.args.get('tutor_email', '').strip()
    if not tutor_email:
        return redirect(url_for('user_extra.teachers_page'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM `tutors` WHERE email = %s LIMIT 1", (tutor_email,))
    tutor = cursor.fetchone()

    if not tutor:
        cursor.close()
        db.close()
        return redirect(url_for('user_extra.teachers_page'))

    tutor_id = tutor['id']

    cursor.execute("SELECT COUNT(*) as cnt FROM `playlist` WHERE tutor_id = %s", (tutor_id,))
    total_playlists = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM `content` WHERE tutor_id = %s", (tutor_id,))
    total_contents = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM `likes` WHERE tutor_id = %s", (tutor_id,))
    total_likes = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM `comments` WHERE tutor_id = %s", (tutor_id,))
    total_comments = cursor.fetchone()['cnt']

    query = """
        SELECT p.*, t.name AS tutor_name, t.image AS tutor_image
        FROM `playlist` p
        JOIN `tutors` t ON p.tutor_id = t.id
        WHERE p.tutor_id = %s AND p.status = 'active'
    """
    cursor.execute(query, (tutor_id,))
    courses = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('tutor_profile.html', tutor=tutor, total_playlists=total_playlists,
                           total_contents=total_contents, total_likes=total_likes,
                           total_comments=total_comments, courses=courses)

@user_extra_bp.route('/profile.php')
def user_profile_page():
    user_id = request.cookies.get('user_id', '')
    if not user_id:
        return redirect(url_for('auth.login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as cnt FROM `bookmark` WHERE user_id = %s", (user_id,))
    total_bookmarked = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM `likes` WHERE user_id = %s", (user_id,))
    total_likes = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM `comments` WHERE user_id = %s", (user_id,))
    total_comments = cursor.fetchone()['cnt']

    cursor.close()
    db.close()

    return render_template('profile.html', total_bookmarked=total_bookmarked,
                           total_likes=total_likes, total_comments=total_comments)

@user_extra_bp.route('/update.php', methods=['GET', 'POST'])
def update_user_profile():
    user_id = request.cookies.get('user_id', '')
    if not user_id:
        return redirect(url_for('auth.login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM `users` WHERE id = %s LIMIT 1", (user_id,))
    user = cursor.fetchone()

    if request.method == 'POST':
        prev_pass = user['password']
        prev_image = user['image']

        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()

        if name:
            cursor.execute("UPDATE `users` SET name = %s WHERE id = %s", (name, user_id))
            flash('username updated successfully!')

        if email:
            cursor.execute("SELECT email FROM `users` WHERE id != %s AND email = %s", (user_id, email))
            if cursor.fetchone():
                flash('email already taken!')
            else:
                cursor.execute("UPDATE `users` SET email = %s WHERE id = %s", (email, user_id))
                flash('email updated successfully!')

        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            ext = os.path.splitext(secure_filename(image_file.filename))[1]
            rename_image = f"{unique_id()}{ext}"
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            image_file.save(os.path.join(UPLOAD_FOLDER, rename_image))

            cursor.execute("UPDATE `users` SET image = %s WHERE id = %s", (rename_image, user_id))
            if prev_image and prev_image != rename_image:
                old_path = os.path.join(UPLOAD_FOLDER, prev_image)
                if os.path.exists(old_path):
                    try: os.remove(old_path)
                    except Exception: pass
            flash('image updated successfully!')

        empty_sha1 = hashlib.sha1("".encode()).hexdigest()
        old_pass_val = request.form.get('old_pass', '').strip()
        new_pass_val = request.form.get('new_pass', '').strip()
        cpass_val = request.form.get('cpass', '').strip()

        old_pass = hashlib.sha1(old_pass_val.encode()).hexdigest() if old_pass_val else empty_sha1
        new_pass = hashlib.sha1(new_pass_val.encode()).hexdigest() if new_pass_val else empty_sha1
        cpass = hashlib.sha1(cpass_val.encode()).hexdigest() if cpass_val else empty_sha1

        if old_pass != empty_sha1:
            if old_pass != prev_pass:
                flash('old password not matched!')
            elif new_pass != cpass:
                flash('confirm password not matched!')
            else:
                if new_pass != empty_sha1:
                    cursor.execute("UPDATE `users` SET password = %s WHERE id = %s", (cpass, user_id))
                    flash('password updated successfully!')
                else:
                    flash('please enter a new password!')

        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('user_extra.user_profile_page'))

    cursor.close()
    db.close()
    return render_template('update.html', user=user)

@user_extra_bp.route('/watch_video.php', methods=['GET', 'POST'])
def watch_video():
    get_id = request.args.get('get_id', '').strip()
    if not get_id:
        return redirect(url_for('home.home_page'))

    user_id = request.cookies.get('user_id', '')
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST' and 'like_content' in request.form:
        if user_id:
            content_id = request.form.get('content_id', '').strip()
            cursor.execute("SELECT tutor_id FROM `content` WHERE id = %s LIMIT 1", (content_id,))
            tutor_rec = cursor.fetchone()
            if tutor_rec:
                tutor_id = tutor_rec['tutor_id']
                cursor.execute("SELECT * FROM `likes` WHERE user_id = %s AND content_id = %s", (user_id, content_id))
                if cursor.fetchone():
                    cursor.execute("DELETE FROM `likes` WHERE user_id = %s AND content_id = %s", (user_id, content_id))
                    db.commit()
                    flash('removed from likes!')
                else:
                    cursor.execute("INSERT INTO `likes` (user_id, tutor_id, content_id) VALUES (%s, %s, %s)",
                                   (user_id, tutor_id, content_id))
                    db.commit()
                    flash('added to likes!')
        else:
            flash('please login first!')

    if request.method == 'POST' and 'add_comment' in request.form:
        if user_id:
            comment_box = request.form.get('comment_box', '').strip()
            content_id = request.form.get('content_id', '').strip()
            cursor.execute("SELECT tutor_id FROM `content` WHERE id = %s LIMIT 1", (content_id,))
            cnt = cursor.fetchone()
            if cnt:
                tutor_id = cnt['tutor_id']
                cursor.execute("SELECT * FROM `comments` WHERE content_id = %s AND user_id = %s AND tutor_id = %s AND comment = %s",
                               (content_id, user_id, tutor_id, comment_box))
                if cursor.fetchone():
                    flash('comment already added!')
                else:
                    c_id = unique_id()
                    cursor.execute("INSERT INTO `comments` (id, content_id, user_id, tutor_id, comment) VALUES (%s, %s, %s, %s, %s)",
                                   (c_id, content_id, user_id, tutor_id, comment_box))
                    db.commit()
                    flash('new comment added!')
        else:
            flash('please login first!')

    if request.method == 'POST' and 'delete_comment' in request.form:
        comment_id = request.form.get('comment_id', '').strip()
        cursor.execute("SELECT * FROM `comments` WHERE id = %s", (comment_id,))
        if cursor.fetchone():
            cursor.execute("DELETE FROM `comments` WHERE id = %s", (comment_id,))
            db.commit()
            flash('comment deleted successfully!')
        else:
            flash('comment already deleted!')

    if request.method == 'POST' and 'update_now' in request.form:
        update_id = request.form.get('update_id', '').strip()
        update_box = request.form.get('update_box', '').strip()
        cursor.execute("SELECT * FROM `comments` WHERE id = %s AND comment = %s", (update_id, update_box))
        if cursor.fetchone():
            flash('comment already added!')
        else:
            cursor.execute("UPDATE `comments` SET comment = %s WHERE id = %s", (update_box, update_id))
            db.commit()
            flash('comment edited successfully!')

    edit_comment_data = None
    if request.method == 'POST' and 'edit_comment' in request.form:
        edit_id = request.form.get('comment_id', '').strip()
        cursor.execute("SELECT * FROM `comments` WHERE id = %s LIMIT 1", (edit_id,))
        edit_comment_data = cursor.fetchone()

    cursor.execute("SELECT * FROM `content` WHERE id = %s AND status = 'active' LIMIT 1", (get_id,))
    content_data = cursor.fetchone()

    tutor_data, total_likes, is_liked, comments = None, 0, False, []

    if content_data:
        cursor.execute("SELECT COUNT(*) as cnt FROM `likes` WHERE content_id = %s", (content_data['id'],))
        total_likes = cursor.fetchone()['cnt']

        if user_id:
            cursor.execute("SELECT * FROM `likes` WHERE user_id = %s AND content_id = %s", (user_id, content_data['id']))
            is_liked = bool(cursor.fetchone())

        cursor.execute("SELECT * FROM `tutors` WHERE id = %s LIMIT 1", (content_data['tutor_id'],))
        tutor_data = cursor.fetchone()

        query_comments = """
            SELECT c.*, u.name AS user_name, u.image AS user_image
            FROM `comments` c
            JOIN `users` u ON c.user_id = u.id
            WHERE c.content_id = %s
        """
        cursor.execute(query_comments, (get_id,))
        comments = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('watch_video.html', content=content_data, tutor=tutor_data,
                           total_likes=total_likes, is_liked=is_liked, comments=comments,
                           edit_comment=edit_comment_data)
