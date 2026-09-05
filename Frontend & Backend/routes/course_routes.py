from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db

course_bp = Blueprint('course', __name__)

@course_bp.route('/courses.php')
def courses_page():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT p.*, t.name AS tutor_name, t.image AS tutor_image 
        FROM `playlist` p
        JOIN `tutors` t ON p.tutor_id = t.id
        WHERE p.status = 'active'
        ORDER BY p.date DESC
    """
    cursor.execute(query)
    courses = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('courses.html', courses=courses)

@course_bp.route('/playlist.php', methods=['GET', 'POST'])
def playlist_page():
    get_id = request.args.get('get_id', '').strip()
    if not get_id:
        return redirect(url_for('home.home_page'))

    user_id = request.cookies.get('user_id', '')
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST' and 'save_list' in request.form:
        if user_id:
            list_id = request.form.get('list_id', '').strip()
            cursor.execute("SELECT * FROM `bookmark` WHERE user_id = %s AND playlist_id = %s", (user_id, list_id))
            if cursor.fetchone():
                cursor.execute("DELETE FROM `bookmark` WHERE user_id = %s AND playlist_id = %s", (user_id, list_id))
                db.commit()
                flash('playlist removed!')
            else:
                cursor.execute("INSERT INTO `bookmark`(user_id, playlist_id) VALUES(%s, %s)", (user_id, list_id))
                db.commit()
                flash('playlist saved!')
        else:
            flash('please login first!')

    cursor.execute("SELECT * FROM `playlist` WHERE id = %s AND status = 'active' LIMIT 1", (get_id,))
    playlist_data = cursor.fetchone()
    total_videos, tutor_data, is_bookmarked, videos = 0, None, False, []

    if playlist_data:
        cursor.execute("SELECT COUNT(*) as cnt FROM `content` WHERE playlist_id = %s", (playlist_data['id'],))
        total_videos = cursor.fetchone()['cnt']
        cursor.execute("SELECT * FROM `tutors` WHERE id = %s LIMIT 1", (playlist_data['tutor_id'],))
        tutor_data = cursor.fetchone()
        if user_id:
            cursor.execute("SELECT * FROM `bookmark` WHERE user_id = %s AND playlist_id = %s", (user_id, playlist_data['id']))
            is_bookmarked = bool(cursor.fetchone())
        cursor.execute("SELECT * FROM `content` WHERE playlist_id = %s AND status = 'active' ORDER BY date DESC", (get_id,))
        videos = cursor.fetchall()

    cursor.close()
    db.close()
    return render_template('playlist.html', playlist=playlist_data, total_videos=total_videos,
                           tutor=tutor_data, is_bookmarked=is_bookmarked, videos=videos)
