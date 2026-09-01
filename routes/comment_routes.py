from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db

comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/comments.php', methods=['GET', 'POST'])
def comments_page():
    user_id = request.cookies.get('user_id', '')
    if not user_id:
        return redirect(url_for('home.home_page'))

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

    query = """
        SELECT c.*, cnt.title AS content_title, cnt.id AS content_id
        FROM `comments` c
        JOIN `content` cnt ON c.content_id = cnt.id
        WHERE c.user_id = %s
    """
    cursor.execute(query, (user_id,))
    comments = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('comments.html', comments=comments, edit_comment=edit_comment_data)
