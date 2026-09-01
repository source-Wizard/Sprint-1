import os
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, make_response, flash
from werkzeug.utils import secure_filename
from db import get_db, unique_id

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
UPLOAD_FOLDER = os.path.join('static', 'uploaded_files')

def get_current_tutor():
    tutor_id = request.cookies.get('tutor_id', '')
    if not tutor_id:
        return None, None
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM `tutors` WHERE id = %s LIMIT 1", (tutor_id,))
    tutor = cursor.fetchone()
    cursor.close()
    db.close()
    return tutor_id, tutor

@admin_bp.route('/login.php', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('pass', '').strip()
        hashed_pass = hashlib.sha1(password.encode()).hexdigest()

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM `tutors` WHERE email = %s AND password = %s LIMIT 1", (email, hashed_pass))
        tutor = cursor.fetchone()
        cursor.close()
        db.close()

        if tutor:
            resp = make_response(redirect(url_for('admin.dashboard')))
            resp.set_cookie('tutor_id', tutor['id'], max_age=60 * 60 * 24 * 30, path='/')
            return resp
        else:
            flash('incorrect email or password!')
    return render_template('admin/login.html')

@admin_bp.route('/register.php', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        tutor_id = unique_id()
        name = request.form.get('name', '').strip()
        profession = request.form.get('profession', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('pass', '').strip()
        cpassword = request.form.get('cpass', '').strip()

        hashed_pass = hashlib.sha1(password.encode()).hexdigest()
        hashed_cpass = hashlib.sha1(cpassword.encode()).hexdigest()

        image_file = request.files.get('image')
        if not image_file or image_file.filename == '':
            flash('please select an image!')
            return render_template('admin/register.html')

        ext = os.path.splitext(secure_filename(image_file.filename))[1]
        rename_image = f"{unique_id()}{ext}"
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        image_path = os.path.join(UPLOAD_FOLDER, rename_image)

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM `tutors` WHERE email = %s", (email,))
        if cursor.fetchone():
            flash('email already taken!')
        elif hashed_pass != hashed_cpass:
            flash('confirm passowrd not matched!')
        else:
            image_file.save(image_path)
            cursor.execute("INSERT INTO `tutors`(id, name, profession, email, password, image) VALUES (%s, %s, %s, %s, %s, %s)",
                           (tutor_id, name, profession, email, hashed_cpass, rename_image))
            db.commit()
            flash('new tutor registered! please login now')
            cursor.close()
            db.close()
            return redirect(url_for('admin.login'))
        cursor.close()
        db.close()
    return render_template('admin/register.html')

@admin_bp.route('/logout.php')
@admin_bp.route('/components/admin_logout.php')
def logout():
    resp = make_response(redirect(url_for('admin.login')))
    resp.delete_cookie('tutor_id', path='/')
    return resp

@admin_bp.route('/dashboard.php')
@admin_bp.route('/')
def dashboard():
    tutor_id, tutor = get_current_tutor()
    if not tutor_id:
        return redirect(url_for('admin.login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as cnt FROM `content` WHERE tutor_id = %s", (tutor_id,))
    total_contents = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM `playlist` WHERE tutor_id = %s", (tutor_id,))
    total_playlists = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM `likes` WHERE tutor_id = %s", (tutor_id,))
    total_likes = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM `comments` WHERE tutor_id = %s", (tutor_id,))
    total_comments = cursor.fetchone()['cnt']
    cursor.close()
    db.close()

    return render_template('admin/dashboard.html', tutor=tutor, total_contents=total_contents,
                           total_playlists=total_playlists, total_likes=total_likes, total_comments=total_comments)

@admin_bp.route('/add_content.php', methods=['GET', 'POST'])
def add_content():
    tutor_id, tutor = get_current_tutor()
    if not tutor_id:
        return redirect(url_for('admin.login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        content_id = unique_id()
        status = request.form.get('status', '').strip()
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        playlist_id = request.form.get('playlist', '').strip()

        thumb_file = request.files.get('thumb')
        video_file = request.files.get('video')

        if thumb_file and video_file:
            thumb_ext = os.path.splitext(secure_filename(thumb_file.filename))[1]
            video_ext = os.path.splitext(secure_filename(video_file.filename))[1]

            rename_thumb = f"{unique_id()}{thumb_ext}"
            rename_video = f"{unique_id()}{video_ext}"

            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            thumb_file.save(os.path.join(UPLOAD_FOLDER, rename_thumb))
            video_file.save(os.path.join(UPLOAD_FOLDER, rename_video))

            query = """
                INSERT INTO `content` (id, tutor_id, playlist_id, title, description, video, thumb, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (content_id, tutor_id, playlist_id, title, description, rename_video, rename_thumb, status))
            db.commit()
            flash('new course uploaded!')

    cursor.execute("SELECT * FROM `playlist` WHERE tutor_id = %s", (tutor_id,))
    playlists = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('admin/add_content.html', tutor=tutor, playlists=playlists)

@admin_bp.route('/add_playlist.php', methods=['GET', 'POST'])
def add_playlist():
    tutor_id, tutor = get_current_tutor()
    if not tutor_id:
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        playlist_id = unique_id()
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', '').strip()

        image_file = request.files.get('image')
        if image_file:
            ext = os.path.splitext(secure_filename(image_file.filename))[1]
            rename_image = f"{unique_id()}{ext}"
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            image_file.save(os.path.join(UPLOAD_FOLDER, rename_image))

            db = get_db()
            cursor = db.cursor(dictionary=True)
            query = "INSERT INTO `playlist` (id, tutor_id, title, description, thumb, status) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (playlist_id, tutor_id, title, description, rename_image, status))
            db.commit()
            cursor.close()
            db.close()
            flash('new playlist created!')

    return render_template('admin/add_playlist.html', tutor=tutor)

@admin_bp.route('/contents.php', methods=['GET', 'POST'])
def contents():
    tutor_id, tutor = get_current_tutor()
    if not tutor_id:
        return redirect(url_for('admin.login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST' and 'delete_video' in request.form:
        delete_id = request.form.get('video_id', '').strip()
        cursor.execute("SELECT * FROM `content` WHERE id = %s LIMIT 1", (delete_id,))
        video_record = cursor.fetchone()
        if video_record:
            for file_name in [video_record.get('thumb'), video_record.get('video')]:
                if file_name:
                    p = os.path.join(UPLOAD_FOLDER, file_name)
                    if os.path.exists(p):
                        try: os.remove(p)
                        except Exception: pass

            cursor.execute("DELETE FROM `likes` WHERE content_id = %s", (delete_id,))
            cursor.execute("DELETE FROM `comments` WHERE content_id = %s", (delete_id,))
            cursor.execute("DELETE FROM `content` WHERE id = %s", (delete_id,))
            db.commit()
            flash('video deleted!')
        else:
            flash('video already deleted!')

    cursor.execute("SELECT * FROM `content` WHERE tutor_id = %s ORDER BY date DESC", (tutor_id,))
    videos = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('admin/contents.html', tutor=tutor, videos=videos)

@admin_bp.route('/playlists.php', methods=['GET', 'POST'])
def playlists():
    tutor_id, tutor = get_current_tutor()
    if not tutor_id:
        return redirect(url_for('admin.login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST' and 'delete' in request.form:
        delete_id = request.form.get('playlist_id', '').strip()
        cursor.execute("SELECT * FROM `playlist` WHERE id = %s AND tutor_id = %s LIMIT 1", (delete_id, tutor_id))
        playlist_record = cursor.fetchone()
        if playlist_record:
            if playlist_record.get('thumb'):
                p = os.path.join(UPLOAD_FOLDER, playlist_record['thumb'])
                if os.path.exists(p):
                    try: os.remove(p)
                    except Exception: pass

            cursor.execute("DELETE FROM `bookmark` WHERE playlist_id = %s", (delete_id,))
            cursor.execute("DELETE FROM `playlist` WHERE id = %s", (delete_id,))
            db.commit()
            flash('playlist deleted!')
        else:
            flash('playlist already deleted!')

    query = """
        SELECT p.*, (SELECT COUNT(*) FROM `content` c WHERE c.playlist_id = p.id) AS total_videos
        FROM `playlist` p
        WHERE p.tutor_id = %s
        ORDER BY p.date DESC
    """
    cursor.execute(query, (tutor_id,))
    playlists_data = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('admin/playlists.html', tutor=tutor, playlists=playlists_data)

@admin_bp.route('/comments.php', methods=['GET', 'POST'])
def comments():
    tutor_id, tutor = get_current_tutor()
    if not tutor_id:
        return redirect(url_for('admin.login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST' and 'delete_comment' in request.form:
        delete_id = request.form.get('comment_id', '').strip()
        cursor.execute("SELECT * FROM `comments` WHERE id = %s", (delete_id,))
        if cursor.fetchone():
            cursor.execute("DELETE FROM `comments` WHERE id = %s", (delete_id,))
            db.commit()
            flash('comment deleted successfully!')
        else:
            flash('comment already deleted!')

    query = """
        SELECT c.*, cnt.title AS content_title, cnt.id AS content_id
        FROM `comments` c
        JOIN `content` cnt ON c.content_id = cnt.id
        WHERE c.tutor_id = %s
    """
    cursor.execute(query, (tutor_id,))
    tutor_comments = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('admin/comments.html', tutor=tutor, comments=tutor_comments)

@admin_bp.route('/profile.php')
def profile():
    tutor_id, tutor = get_current_tutor()
    if not tutor_id:
        return redirect(url_for('admin.login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as cnt FROM `playlist` WHERE tutor_id = %s", (tutor_id,))
    total_playlists = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM `content` WHERE tutor_id = %s", (tutor_id,))
    total_contents = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM `likes` WHERE tutor_id = %s", (tutor_id,))
    total_likes = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM `comments` WHERE tutor_id = %s", (tutor_id,))
    total_comments = cursor.fetchone()['cnt']
    cursor.close()
    db.close()

    return render_template('admin/profile.html', tutor=tutor, total_playlists=total_playlists,
                           total_contents=total_contents, total_likes=total_likes, total_comments=total_comments)

@admin_bp.route('/update.php', methods=['GET', 'POST'])
def update_profile():
    tutor_id, tutor = get_current_tutor()
    if not tutor_id:
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM `tutors` WHERE id = %s LIMIT 1", (tutor_id,))
        current_data = cursor.fetchone()

        prev_pass = current_data['password']
        prev_image = current_data['image']

        name = request.form.get('name', '').strip()
        profession = request.form.get('profession', '').strip()
        email = request.form.get('email', '').strip()

        if name:
            cursor.execute("UPDATE `tutors` SET name = %s WHERE id = %s", (name, tutor_id))
            flash('username updated successfully!')

        if profession:
            cursor.execute("UPDATE `tutors` SET profession = %s WHERE id = %s", (profession, tutor_id))
            flash('profession updated successfully!')

        if email:
            cursor.execute("SELECT email FROM `tutors` WHERE id != %s AND email = %s", (tutor_id, email))
            if cursor.fetchone():
                flash('email already taken!')
            else:
                cursor.execute("UPDATE `tutors` SET email = %s WHERE id = %s", (email, tutor_id))
                flash('email updated successfully!')

        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            ext = os.path.splitext(secure_filename(image_file.filename))[1]
            rename_image = f"{unique_id()}{ext}"
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            image_path = os.path.join(UPLOAD_FOLDER, rename_image)
            image_file.save(image_path)

            cursor.execute("UPDATE `tutors` SET image = %s WHERE id = %s", (rename_image, tutor_id))
            if prev_image and prev_image != rename_image:
                old_p = os.path.join(UPLOAD_FOLDER, prev_image)
                if os.path.exists(old_p):
                    try: os.remove(old_p)
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
                    cursor.execute("UPDATE `tutors` SET password = %s WHERE id = %s", (cpass, tutor_id))
                    flash('password updated successfully!')
                else:
                    flash('please enter a new password!')

        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('admin.profile'))

    return render_template('admin/update.html', tutor=tutor)

@admin_bp.route('/update_content.php', methods=['GET', 'POST'])
def update_content():
    tutor_id, tutor = get_current_tutor()
    if not tutor_id:
        return redirect(url_for('admin.login'))

    get_id = request.args.get('get_id', '').strip()
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST' and 'update' in request.form:
        video_id = request.form.get('video_id', '').strip()
        status = request.form.get('status', '').strip()
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        playlist = request.form.get('playlist', '').strip()

        cursor.execute("UPDATE `content` SET title = %s, description = %s, status = %s WHERE id = %s",
                       (title, description, status, video_id))
        if playlist:
            cursor.execute("UPDATE `content` SET playlist_id = %s WHERE id = %s", (playlist, video_id))

        old_thumb = request.form.get('old_thumb', '').strip()
        thumb_file = request.files.get('thumb')
        if thumb_file and thumb_file.filename != '':
            ext = os.path.splitext(secure_filename(thumb_file.filename))[1]
            rename_thumb = f"{unique_id()}{ext}"
            thumb_file.save(os.path.join(UPLOAD_FOLDER, rename_thumb))
            cursor.execute("UPDATE `content` SET thumb = %s WHERE id = %s", (rename_thumb, video_id))
            if old_thumb and old_thumb != rename_thumb:
                old_p = os.path.join(UPLOAD_FOLDER, old_thumb)
                if os.path.exists(old_p):
                    try: os.remove(old_p)
                    except Exception: pass

        old_video = request.form.get('old_video', '').strip()
        video_file = request.files.get('video')
        if video_file and video_file.filename != '':
            ext = os.path.splitext(secure_filename(video_file.filename))[1]
            rename_video = f"{unique_id()}{ext}"
            video_file.save(os.path.join(UPLOAD_FOLDER, rename_video))
            cursor.execute("UPDATE `content` SET video = %s WHERE id = %s", (rename_video, video_id))
            if old_video and old_video != rename_video:
                old_p = os.path.join(UPLOAD_FOLDER, old_video)
                if os.path.exists(old_p):
                    try: os.remove(old_p)
                    except Exception: pass

        db.commit()
        flash('content updated!')

    if request.method == 'POST' and 'delete_video' in request.form:
        delete_id = request.form.get('video_id', '').strip()
        cursor.execute("SELECT * FROM `content` WHERE id = %s LIMIT 1", (delete_id,))
        video_record = cursor.fetchone()
        if video_record:
            for f in [video_record.get('thumb'), video_record.get('video')]:
                if f:
                    p = os.path.join(UPLOAD_FOLDER, f)
                    if os.path.exists(p):
                        try: os.remove(p)
                        except Exception: pass
            cursor.execute("DELETE FROM `likes` WHERE content_id = %s", (delete_id,))
            cursor.execute("DELETE FROM `comments` WHERE content_id = %s", (delete_id,))
            cursor.execute("DELETE FROM `content` WHERE id = %s", (delete_id,))
            db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('admin.contents'))

    cursor.execute("SELECT * FROM `content` WHERE id = %s AND tutor_id = %s", (get_id, tutor_id))
    video_data = cursor.fetchone()
    cursor.execute("SELECT * FROM `playlist` WHERE tutor_id = %s", (tutor_id,))
    playlists = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('admin/update_content.html', tutor=tutor, video=video_data, playlists=playlists)

@admin_bp.route('/update_playlist.php', methods=['GET', 'POST'])
def update_playlist():
    tutor_id, tutor = get_current_tutor()
    if not tutor_id:
        return redirect(url_for('admin.login'))

    get_id = request.args.get('get_id', '').strip()
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST' and 'submit' in request.form:
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', '').strip()

        cursor.execute("UPDATE `playlist` SET title = %s, description = %s, status = %s WHERE id = %s",
                       (title, description, status, get_id))

        old_image = request.form.get('old_image', '').strip()
        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            ext = os.path.splitext(secure_filename(image_file.filename))[1]
            rename_image = f"{unique_id()}{ext}"
            image_file.save(os.path.join(UPLOAD_FOLDER, rename_image))
            cursor.execute("UPDATE `playlist` SET thumb = %s WHERE id = %s", (rename_image, get_id))
            if old_image and old_image != rename_image:
                old_p = os.path.join(UPLOAD_FOLDER, old_image)
                if os.path.exists(old_p):
                    try: os.remove(old_p)
                    except Exception: pass

        db.commit()
        flash('playlist updated!')

    if request.method == 'POST' and 'delete' in request.form:
        delete_id = request.form.get('playlist_id', '').strip()
        cursor.execute("SELECT * FROM `playlist` WHERE id = %s LIMIT 1", (delete_id,))
        pl = cursor.fetchone()
        if pl and pl.get('thumb'):
            p = os.path.join(UPLOAD_FOLDER, pl['thumb'])
            if os.path.exists(p):
                try: os.remove(p)
                except Exception: pass
        cursor.execute("DELETE FROM `bookmark` WHERE playlist_id = %s", (delete_id,))
        cursor.execute("DELETE FROM `playlist` WHERE id = %s", (delete_id,))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('admin.playlists'))

    cursor.execute("SELECT * FROM `playlist` WHERE id = %s AND tutor_id = %s", (get_id, tutor_id))
    playlist_data = cursor.fetchone()
    total_videos = 0
    if playlist_data:
        cursor.execute("SELECT COUNT(*) as cnt FROM `content` WHERE playlist_id = %s", (playlist_data['id'],))
        total_videos = cursor.fetchone()['cnt']

    cursor.close()
    db.close()

    return render_template('admin/update_playlist.html', tutor=tutor, playlist=playlist_data, total_videos=total_videos)

@admin_bp.route('/view_content.php', methods=['GET', 'POST'])
def view_content():
    tutor_id, tutor = get_current_tutor()
    if not tutor_id:
        return redirect(url_for('admin.login'))

    get_id = request.args.get('get_id', '').strip()
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST' and 'delete_comment' in request.form:
        comment_id = request.form.get('comment_id', '').strip()
        cursor.execute("DELETE FROM `comments` WHERE id = %s", (comment_id,))
        db.commit()
        flash('comment deleted successfully!')

    if request.method == 'POST' and 'delete_video' in request.form:
        delete_id = request.form.get('video_id', '').strip()
        cursor.execute("SELECT * FROM `content` WHERE id = %s LIMIT 1", (delete_id,))
        v = cursor.fetchone()
        if v:
            for f in [v.get('thumb'), v.get('video')]:
                if f:
                    p = os.path.join(UPLOAD_FOLDER, f)
                    if os.path.exists(p):
                        try: os.remove(p)
                        except Exception: pass
            cursor.execute("DELETE FROM `likes` WHERE content_id = %s", (delete_id,))
            cursor.execute("DELETE FROM `comments` WHERE content_id = %s", (delete_id,))
            cursor.execute("DELETE FROM `content` WHERE id = %s", (delete_id,))
            db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('admin.contents'))

    cursor.execute("SELECT * FROM `content` WHERE id = %s AND tutor_id = %s", (get_id, tutor_id))
    video_data = cursor.fetchone()

    total_likes, total_comments, comments = 0, 0, []
    if video_data:
        cursor.execute("SELECT COUNT(*) as cnt FROM `likes` WHERE tutor_id = %s AND content_id = %s", (tutor_id, get_id))
        total_likes = cursor.fetchone()['cnt']
        cursor.execute("SELECT COUNT(*) as cnt FROM `comments` WHERE tutor_id = %s AND content_id = %s", (tutor_id, get_id))
        total_comments = cursor.fetchone()['cnt']

        query = """
            SELECT c.*, u.name AS user_name, u.image AS user_image
            FROM `comments` c
            JOIN `users` u ON c.user_id = u.id
            WHERE c.content_id = %s
        """
        cursor.execute(query, (get_id,))
        comments = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin/view_content.html', tutor=tutor, video=video_data,
                           total_likes=total_likes, total_comments=total_comments, comments=comments)

@admin_bp.route('/view_playlist.php', methods=['GET', 'POST'])
def view_playlist():
    tutor_id, tutor = get_current_tutor()
    if not tutor_id:
        return redirect(url_for('admin.login'))

    get_id = request.args.get('get_id', '').strip()
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST' and 'delete' in request.form:
        delete_id = request.form.get('playlist_id', '').strip()
        cursor.execute("SELECT * FROM `playlist` WHERE id = %s LIMIT 1", (delete_id,))
        pl = cursor.fetchone()
        if pl and pl.get('thumb'):
            p = os.path.join(UPLOAD_FOLDER, pl['thumb'])
            if os.path.exists(p):
                try: os.remove(p)
                except Exception: pass
        cursor.execute("DELETE FROM `bookmark` WHERE playlist_id = %s", (delete_id,))
        cursor.execute("DELETE FROM `playlist` WHERE id = %s", (delete_id,))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('admin.playlists'))

    if request.method == 'POST' and 'delete_video' in request.form:
        delete_id = request.form.get('video_id', '').strip()
        cursor.execute("SELECT * FROM `content` WHERE id = %s LIMIT 1", (delete_id,))
        v = cursor.fetchone()
        if v:
            for f in [v.get('thumb'), v.get('video')]:
                if f:
                    p = os.path.join(UPLOAD_FOLDER, f)
                    if os.path.exists(p):
                        try: os.remove(p)
                        except Exception: pass
            cursor.execute("DELETE FROM `likes` WHERE content_id = %s", (delete_id,))
            cursor.execute("DELETE FROM `comments` WHERE content_id = %s", (delete_id,))
            cursor.execute("DELETE FROM `content` WHERE id = %s", (delete_id,))
            db.commit()
            flash('video deleted!')

    cursor.execute("SELECT * FROM `playlist` WHERE id = %s AND tutor_id = %s", (get_id, tutor_id))
    playlist_data = cursor.fetchone()

    total_videos, videos = 0, []
    if playlist_data:
        cursor.execute("SELECT COUNT(*) as cnt FROM `content` WHERE playlist_id = %s", (playlist_data['id'],))
        total_videos = cursor.fetchone()['cnt']
        cursor.execute("SELECT * FROM `content` WHERE tutor_id = %s AND playlist_id = %s", (tutor_id, playlist_data['id']))
        videos = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin/view_playlist.html', tutor=tutor, playlist=playlist_data,
                           total_videos=total_videos, videos=videos)

@admin_bp.route('/search_page.php', methods=['GET', 'POST'])
def search_page():
    tutor_id, tutor = get_current_tutor()
    if not tutor_id:
        return redirect(url_for('admin.login'))

    search_query = request.form.get('search', '').strip() if request.method == 'POST' else ''
    videos = []
    playlists_data = []

    if search_query:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM `content` WHERE title LIKE %s AND tutor_id = %s ORDER BY date DESC",
                       (f"%{search_query}%", tutor_id))
        videos = cursor.fetchall()

        query = """
            SELECT p.*, (SELECT COUNT(*) FROM `content` c WHERE c.playlist_id = p.id) AS total_videos
            FROM `playlist` p
            WHERE p.title LIKE %s AND p.tutor_id = %s
            ORDER BY p.date DESC
        """
        cursor.execute(query, (f"%{search_query}%", tutor_id))
        playlists_data = cursor.fetchall()

        cursor.close()
        db.close()

    return render_template('admin/search_page.html', tutor=tutor, search_query=search_query,
                           videos=videos, playlists=playlists_data)
