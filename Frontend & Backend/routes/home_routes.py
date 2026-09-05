from flask import Blueprint, render_template, request
from db import get_db

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
@home_bp.route('/home.php')
def home_page():
    user_id = request.cookies.get('user_id', '')
    total_likes, total_comments, total_bookmarked = 0, 0, 0
    courses = []

    db = get_db()
    cursor = db.cursor(dictionary=True)
    if user_id:
        cursor.execute("SELECT COUNT(*) as cnt FROM `likes` WHERE user_id = %s", (user_id,))
        total_likes = cursor.fetchone()['cnt']
        cursor.execute("SELECT COUNT(*) as cnt FROM `comments` WHERE user_id = %s", (user_id,))
        total_comments = cursor.fetchone()['cnt']
        cursor.execute("SELECT COUNT(*) as cnt FROM `bookmark` WHERE user_id = %s", (user_id,))
        total_bookmarked = cursor.fetchone()['cnt']

    query = """
        SELECT p.*, t.name AS tutor_name, t.image AS tutor_image 
        FROM `playlist` p
        JOIN `tutors` t ON p.tutor_id = t.id
        WHERE p.status = 'active'
        ORDER BY p.date DESC LIMIT 6
    """
    cursor.execute(query)
    courses = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('home.html', total_likes=total_likes, total_comments=total_comments,
                           total_bookmarked=total_bookmarked, courses=courses)
