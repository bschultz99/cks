from flask import Flask, Response, render_template, redirect, url_for, request
from queries import *
import os, psycopg2
import secrets
import string
import bcrypt
import math

app = Flask(__name__)

# Global flag to ensure code runs only once
code_executed = False

# Helper Methods
def generate_password():
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(12))
    return password

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def check_password(input_password, stored_password):
    if bcrypt.checkpw(input_password.encode('utf-8'), stored_password):
        return True
    return False

# Application Score
def accademic_score(cuumulative_gpa, semesters):
    TUNING_FACTOR = .3
    if cuumulative_gpa < 3.0:
        gpa_score = 0
    else:
        gpa_score = cuumulative_gpa * (1 + TUNING_FACTOR * math.sqrt(semesters))
    return gpa_score * 10

def fraternity_score(executive_positions, other_positions, conferences):
    EXECUTIVE_POINTS = 8
    OTHER_POINTS = 4
    CONFERENCE_POINTS = 2
    return (executive_positions * EXECUTIVE_POINTS) + (other_positions * OTHER_POINTS) + (conferences * CONFERENCE_POINTS)

def organization_score(executive_positions, other_positions):
    EXECUTIVE_POINTS = 4
    OTHER_POINTS = 2
    return (executive_positions * EXECUTIVE_POINTS) + (other_positions * OTHER_POINTS)

def community_service_score(hours, semesters_active):
    HOURS_POINTS = .2 # 50 Hours = 1 Exec position
    return (hours - (16 * semesters_active)) * HOURS_POINTS

def total_score(gpa_score, fraternity_score, organization_score, community_service_score):
    return gpa_score + fraternity_score + organization_score + community_service_score

# Applicant

@app.route('/newapplicant', methods=['GET'])
def newApplicant():
    """Create a new applicant in the database and send them an email to fill out initial information."""
    first_name = "Bryant" #request.form['first_name']
    last_name = "Schultz" #request.form['last_name']
    email = "bschultz1@hawk.iit.edu" #request.form['email']
    if cursor.execute(NEW_APPLICANT_CHECK, (email,)) is not None:
        print("Applicant already exists")
        return Response(), 409 # Applicant already exists
    password = generate_password()
    hashed_password = hash_password(password)
    print("Generting USER: ", first_name, last_name, email, password, hashed_password)
    cursor.execute(NEW_APPLICANT_INSERT, (first_name, last_name, email, hashed_password))
    conn.commit()
    return Response(), 200


@app.route('/login', methods=['POST'])
def login():
    """Login an applicant or reviewer."""
    email = request.form['email']
    password = request.form['password']
    print(email, password)
    return redirect(url_for('applicant'))



# Admin

@app.route('/start_applications', methods=['GET'])
def startApplications():
    """Start the application process."""
    return Response(), 200


@app.route('/close_applications', methods=['GET'])
def closeApplications():
    """Close all applications."""
    return Response(), 200


# Web Pages

@app.route('/applicant')
def applicant():
    return render_template('applicant.html')

@app.route('/')
def index():
    return render_template('index.html')







if __name__ == "__main__":
    if not code_executed:
        conn = psycopg2.connect(database=os.getenv("PGDATABASE"),
                                host=os.getenv("PGHOST"),
                                user=os.getenv("POSTGRES_USER"),
                                password=os.getenv("POSTGRES_PASSWORD"),
                                port=os.getenv("PGPORT"))
        cursor = conn.cursor()
        cursor.execute(CREATE_TABLES)
        conn.commit()
        newApplicant()
        newApplicant()
        code_executed = True
    app.run(debug=False, host='0.0.0.0', port=8080)