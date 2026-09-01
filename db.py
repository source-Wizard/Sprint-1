import random
import string
import mysql.connector

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="course_db"
    )

def unique_id():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=20))
