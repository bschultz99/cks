from flask import Flask, Response, render_template, redirect, url_for, request
from queries import *
import os, psycopg2
import secrets
import string
import bcrypt
import math
import requests

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
    if bcrypt.checkpw(input_password.encode('utf-8'), stored_password.encode('utf-8')):
        return True
    return False

# Emails
def send_email(recipient, text_body, subject):
    api_key = os.getenv("MAILGUN")
    domain = os.getenv("MAILGUN_DOMAIN")
    sender = "cks@{}".format(domain)
    url = f'https://api.mailgun.net/v3/{domain}/messages'
    response = requests.post(
        url,
        auth=('api', api_key),
        data={'from': sender,
              'to': recipient,
              'subject': subject,
              'text': text_body})
    return response.status_code

def send_new_applicant_email(email, password, first_name, last_name):
    subject = "Carroll Simons Scholarship Application Login"
    text_body = f"""Hello {first_name} {last_name},\n\n
    An account has been created for you to apply for the Carroll Simons Scholarship.\n
    Your email is: {email} and your password is: {password}\n\n
    Please login at https://cks-production.up.railway.app to complete your application.\n\n
    Thank you,\n
    Carroll Simons Scholarship Committee"""
    return send_email(email, text_body, subject)

def send_forgot_password_email(email, password, first_name, last_name):
    subject = "Carroll Simons Scholarship Application Password Reset"
    text_body = f"""Hello {first_name} {last_name},\n\n
    Your password has been reset for the Carroll Simons Scholarship Application.\n
    Your email is: {email}\n\n
    Your new password is: {password}\n\n
    Please login at https://cks-production.up.railway.app to complete your application.\n\n
    Thank you,\n
    Carroll Simons Scholarship Committee"""
    return send_email(email, text_body, subject)

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


# Button Logic
@app.route('/newapplicant', methods=['GET'])
def newApplicant():
    """Create a new applicant in the database and send them an email to fill out initial information."""
    first_name = "Bryant" #request.form['first_name']
    last_name = "Schultz" #request.form['last_name']
    email = "bschultz1@hawk.iit.edu" #request.form['email']d
    cursor.execute(APPLICANT_CHECK, (email,))
    if  cursor.fetchall():
        print("Applicant already exists")
        return redirect(url_for('error', message='Applicant already exists'))
    password = generate_password()
    hashed_password = hash_password(password)
    send_new_applicant_email(email, password, first_name, last_name)
    cursor.execute(NEW_APPLICANT_INSERT, (first_name, last_name, email, hashed_password))
    conn.commit()
    return Response(), 200

@app.route('/login', methods=['POST'])
def login():
    """Login an applicant or reviewer."""
    email = request.form['email']
    password = request.form['password']
    cursor.execute(APPLICANT_LOGIN, (email,))
    stored_password = cursor.fetchone()
    if not stored_password:
        print("oh no")
        return redirect(url_for('error', message='Applicant does not exist'))
    if check_password(password, stored_password[0]):
        cursor.execute(APPLICANT_NAME, (email,))
        name = cursor.fetchone()
        return redirect(url_for('application', applicant_first_name=name[0]))
    else:
        return redirect(url_for('error', message='Incorrect password'))

@app.route('/forgot_password', methods=['POST'])
def forgotPassword():
    """Send an email to the applicant with their password."""
    email = "bschultz1@hawk.iit.edu" #request.form['email']
    cursor.execute(APPLICANT_CHECK, (email,))
    if not cursor.fetchone():
        return redirect(url_for('error', message='Applicant does not exist'))
    password = generate_password()
    hashed_password = hash_password(password)
    cursor.execute(APPLICANT_NAME, (email,))
    first_name, last_name = cursor.fetchone()
    send_forgot_password_email(email, password, first_name, last_name)
    cursor.execute(NEW_APPLICANT_INSERT, (first_name, last_name, email, hashed_password))
    conn.commit()
    return redirect(url_for('index'))

@app.route('/start_applications', methods=['GET'])
def startApplications():
    """Start the application process."""
    return Response(), 200

@app.route('/close_applications', methods=['GET'])
def closeApplications():
    """Close all applications."""
    return Response(), 200

# Main Pages

@app.route('/application')
def application():
    applicant_name = request.args.get('applicant_first_name', '')
    if applicant_name == '':
        return redirect(url_for('error', message='Please login.'))
    return render_template('application.html', applicant_first_name=applicant_name)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/error')
def error():
    error_message = request.args.get('message', 'An error occurred.')
    return render_template('error.html', error_message=error_message)

@app.route('/forgot_password_page', methods=['GET'])
def forgotPasswordPage():
    return render_template('forgot_password.html')

# Main Loop
if __name__ == "__main__":
    if not code_executed:
        conn = psycopg2.connect(database=os.getenv("PGDATABASE"),
                                host=os.getenv("PGHOST"),
                                user=os.getenv("POSTGRES_USER"),
                                password=os.getenv("POSTGRES_PASSWORD"),
                                port=os.getenv("PGPORT"))
        cursor = conn.cursor()
        #cursor.execute("DROP TABLE IF EXISTS applicants CASCADE;")
        #conn.commit()
        cursor.execute(CREATE_TABLES)
        conn.commit()
        code_executed = True
    app.run(debug=False, host='0.0.0.0', port=8080)