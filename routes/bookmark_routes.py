from flask import Blueprint, render_template, request, redirect, url_for
from db import get_db

bookmark_bp = Blueprint('bookmark', __name__)

@bookmark_bp.route('/bookmark.php')
def bookmark_page():
    user_id = request.cookies.get('user_id', '')
    if not user_id:
        return redirect(url_for('home.home_page'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT p.*, t.name AS tutor_name, t.image AS tutor_image 
        FROM `bookmark` b
        JOIN `playlist` p ON b.playlist_id = p.id
        JOIN `tutors` t ON p.tutor_id = t.id
        WHERE b.user_id = %s AND p.status = 'active'
        ORDER BY p.date DESC
    """
    cursor.execute(query, (user_id,))
    bookmarks = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('bookmark.html', bookmarks=bookmarks)
