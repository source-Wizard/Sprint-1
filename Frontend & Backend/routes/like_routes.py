from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db

like_bp = Blueprint('like', __name__)

@like_bp.route('/likes.php', methods=['GET', 'POST'])
def likes_page():
    user_id = request.cookies.get('user_id', '')
    if not user_id:
        return redirect(url_for('home.home_page'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST' and 'remove' in request.form:
        content_id = request.form.get('content_id', '').strip()
        cursor.execute("SELECT * FROM `likes` WHERE user_id = %s AND content_id = %s", (user_id, content_id))
        if cursor.fetchone():
            cursor.execute("DELETE FROM `likes` WHERE user_id = %s AND content_id = %s", (user_id, content_id))
            db.commit()
            flash('removed from likes!')

    query = """
        SELECT cnt.*, t.name AS tutor_name, t.image AS tutor_image
        FROM `likes` l
        JOIN `content` cnt ON l.content_id = cnt.id
        JOIN `tutors` t ON cnt.tutor_id = t.id
        WHERE l.user_id = %s
        ORDER BY cnt.date DESC
    """
    cursor.execute(query, (user_id,))
    liked_videos = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('likes.html', liked_videos=liked_videos)
