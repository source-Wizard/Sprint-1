# EDUCA -  
Educa is a lightweight, responsive web platform built with Python PHP and MySQL that facilitates structured, playlist-based online course distribution and interactive student-tutor engagement.

## Features
* Student registration and secure login  
* Tutor registration and admin authentication  
* Browse, filter, and search video playlists and courses
* Search expert tutors and view public instructor profiles
* HTML5 video player with interactive tutorials
* Like tutorials and bookmark playlists
* Add, edit, and delete video comments
* Instructor analytics dashboard with counters for videos, playlists, likes, and comments  
* Upload and manage video lectures with thumbnails and playlist mapping  
* Create, update, and delete course playlists  
* Moderate user comments across tutor content  Contact us inquiry form submission
* Dark mode and light mode interface toggling  

## Technologies Used
* HTML  
* CSS  
* JavaScript  
* Python
* Flask
* Jinja2
* MySQL 

## Project Structure

```text
Educa/
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py
│   ├── home_routes.py
│   ├── about_routes.py
│   ├── course_routes.py
│   ├── bookmark_routes.py
│   ├── comment_routes.py
│   ├── contact_routes.py
│   ├── like_routes.py
│   ├── admin_routes.py
│   └── user_extra_routes.py
├── static/
│   ├── css/
│   │   ├── style.css
│   │   └── admin_style.css
│   ├── js/
│   │   ├── script.js
│   │   └── admin_script.js
│   ├── images/
│   └── uploaded_files/
├── templates/
│   ├── admin/
│   │   ├── add_content.html
│   │   ├── add_playlist.html
│   │   ├── comments.html
│   │   ├── contents.html
│   │   ├── dashboard.html
│   │   ├── login.html
│   │   ├── playlists.html
│   │   ├── profile.html
│   │   ├── register.html
│   │   ├── search_page.html
│   │   ├── update.html
│   │   ├── update_content.html
│   │   ├── update_playlist.html
│   │   ├── view_content.html
│   │   └── view_playlist.html
│   ├── components/
│   │   ├── admin_header.html
│   │   ├── footer.html
│   │   └── user_header.html
│   ├── about.html
│   ├── bookmark.html
│   ├── comments.html
│   ├── contact.html
│   ├── courses.html
│   ├── home.html
│   ├── likes.html
│   ├── login.html
│   ├── playlist.html
│   ├── profile.html
│   ├── register.html
│   ├── search_course.html
│   ├── search_tutor.html
│   ├── teachers.html
│   ├── tutor_profile.html
│   ├── update.html
│   └── watch_video.html
├── app.py
├── config.py
├── db.py
├── requirements.txt
├── .gitignore
└── README.md
