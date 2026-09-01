from flask import Flask, request
from db import get_db

from routes.auth_routes import auth_bp
from routes.home_routes import home_bp
from routes.about_routes import about_bp
from routes.course_routes import course_bp
from routes.bookmark_routes import bookmark_bp
from routes.comment_routes import comment_bp
from routes.contact_routes import contact_bp
from routes.like_routes import like_bp
from routes.admin_routes import admin_bp
from routes.user_extra_routes import user_extra_bp  # <-- IMPORT HERE

app = Flask(__name__)
app.secret_key = "super_secret_key_educa"

@app.context_processor
def inject_user():
    user_id = request.cookies.get('user_id', '')
    user_profile = None
    if user_id:
        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM `users` WHERE id = %s LIMIT 1", (user_id,))
            user_profile = cursor.fetchone()
            cursor.close()
            db.close()
        except Exception:
            user_profile = None
    return dict(user_id=user_id, user_profile=user_profile)

app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(about_bp)
app.register_blueprint(course_bp)
app.register_blueprint(bookmark_bp)
app.register_blueprint(comment_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(like_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_extra_bp)  # <-- REGISTER HERE

if __name__ == '__main__':
    app.run(debug=True, port=5000)