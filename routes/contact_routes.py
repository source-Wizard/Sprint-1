from flask import Blueprint, render_template, request, flash
from db import get_db

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact.php', methods=['GET', 'POST'])
def contact_page():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        number = request.form.get('number', '').strip()
        msg = request.form.get('msg', '').strip()

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM `contact` WHERE name = %s AND email = %s AND number = %s AND message = %s",
                       (name, email, number, msg))
        if cursor.fetchone():
            flash('message sent already!')
        else:
            cursor.execute("INSERT INTO `contact`(name, email, number, message) VALUES(%s, %s, %s, %s)",
                           (name, email, number, msg))
            db.commit()
            flash('message sent successfully!')
        cursor.close()
        db.close()
    return render_template('contact.html')
