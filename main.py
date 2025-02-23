from flask import Flask, Response, render_template, redirect, url_for, request, jsonify, make_response
from queries import *
import os, psycopg2
import secrets
import string
import bcrypt
import math
import requests
import time
import json
from datetime import datetime
from xhtml2pdf import pisa

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

@app.route('/send_pdf', methods=['GET']) #TODO: Create a custom HTML Fomat for the PDF.
def send_pdf():
    #cursor.execute("SELECT * FROM applications WHERE applicant_id = 1;")
    #data = cursor.fetchone()
    email_body = render_template('application.html', applicant_first_name='Bryant', email='bschultz1@hawk.iit.edu')
    with  open("output.pdf", "w+b") as pdf_file:
        pisa.CreatePDF(email_body, dest=pdf_file)
    return send_email('bryantschultz99@gmail.com', email_body, 'CKS Email Test', 'output.pdf')


# Emails
def send_email(recipient, text_body, subject, pdf_path=None):
    api_key = os.getenv("MAILGUN")
    domain = os.getenv("MAILGUN_DOMAIN")
    sender = "cks@{}".format(domain)
    url = f'https://api.mailgun.net/v3/{domain}/messages'
    files={}
    if pdf_path:
        files = {'attachment': (os.path.basename(pdf_path), open(pdf_path, 'rb'))}
    response = requests.post(
        url,
        auth=('api', api_key),
        data={'from': sender,
              'to': recipient,
              'subject': subject,
              'text': text_body},
        files=files)
    
    print(response)
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

def send_closed_scholarship_email(email, first_name, last_name):
    subject = "Carroll Simons Scholarship Application Closed"
    text_body = f"""Hello {first_name} {last_name},\n\n
    The Carroll Simons Scholarship Application has been closed.\n
    Thank you for applying.\n\n
    Please come to Smoker for the scholarship announcements.\n\n
    Thank you,\n
    Carroll Simons Scholarship Committee"""
    return send_email(email, text_body, subject)


# Application Score
def accademic_score(cumulative_gpa):
    if cumulative_gpa < 3.0:
        gpa_score = 0
    else:
        gpa_score = (cumulative_gpa - 3.0) * 10
    return gpa_score

def fraternity_score(executive_positions, other_positions, conferences):
    EXECUTIVE_POINTS = 4
    OTHER_POINTS = 2
    CONFERENCE_POINTS = 1
    return (executive_positions * EXECUTIVE_POINTS) + (other_positions * OTHER_POINTS) + (conferences * CONFERENCE_POINTS)

def organization_score(executive_positions, other_positions, semesters_involved):
    EXECUTIVE_POINTS = 2
    OTHER_POINTS = 1
    SEMESTERS_INVOLVED = .5
    return (executive_positions * EXECUTIVE_POINTS) + (other_positions * OTHER_POINTS) + (semesters_involved * SEMESTERS_INVOLVED)

def community_service_score(hours):
    HOURS_POINTS = .05
    return hours * HOURS_POINTS

def total_score(academic_score, fraternity_score, organization_score, community_service_score):
    if academic_score == 0:
        return 0
    return academic_score + fraternity_score + organization_score + community_service_score

def generate_scores():
    cursor.execute("SELECT * FROM applications")
    applications = cursor.fetchall()
    for application in applications:
        gpa_score = accademic_score(application[12])
        fraternity_score = fraternity_score(application[15], application[16], application[17])
        organization_score = organization_score(application[20], application[21], application[19])
        community_service_score = community_service_score(application[23])
        score = total_score(gpa_score, fraternity_score, organization_score, community_service_score)
        cursor.execute("UPDATE applications SET score = %s WHERE application_id = %s", (score, application[0]))
    conn.commit()

def generate_scholarship_amounts():
    SCHOLARHIP_AMOUNT = 30000
    SMALLEST_SCHOLARSHIP = 1000
    cursor.execute(COUNT_OF_APPLICATIONS)
    count = cursor.fetchone()[0]
    budget = SCHOLARHIP_AMOUNT - (SMALLEST_SCHOLARSHIP * count)
    if budget < 0:
        return "Not enough budget"
    cursor.execute("SELECT application_id, score, live_in_house FROM applications ORDER BY score DESC")
    applications = cursor.fetchall()
    max_score = applications[0][1]
    min_score = applications[-1][1]
    score_range = max_score - min_score
    total_weight = sum(((application[1] - min_score) / score_range) for application in applications)
    temp_scholarships = []
    for application in applications:
        if total_weight > 0:
            additional_scholarship = (((application[1] - min_score) / score_range) / total_weight) * budget
            additional_scholarship = round(additional_scholarship/1000)*1000
        else:
            additional_scholarship = 0
        temp_scholarships.append((application[0], SMALLEST_SCHOLARSHIP + additional_scholarship))

    scholarship_sum = sum(scholarship[1] for scholarship in temp_scholarships)

    for scholarship in temp_scholarships:
        cursor.execute("UPDATE applications SET recommended_scholarship_amount = %s WHERE application_id = %s", (scholarship[2], scholarship[0]))
        conn.commit()

    return scholarship_sum
            


# Application

def save_application_data(data):
    # General Information
    email = data.get('email') if data.get('email') else None
    a_number = data.get('a_number') if data.get('a_number') else None
    first_semester = data.get('first_semester') if data.get('first_semester') else None
    estimated_graduation = data.get('estimated_graduation') if data.get('estimated_graduation') else None
    active_next_year = data.get('active_next_year') if data.get('active_next_year') else None
    live_in_house = data.get('live_in_house') if data.get('live_in_house') else None
    # Academic Information
    first_major = data.get('first_major') if data.get('first_major') else None
    second_major = data.get('second_major') if data.get('second_major') else None
    first_minor = data.get('first_minor') if data.get('first_minor') else None
    second_minor = data.get('second_minor') if data.get('second_minor') else None
    cumulative_gpa = data.get('cumulative_gpa') if data.get('cumulative_gpa') else None
    previous_gpa = data.get('previous_gpa') if data.get('previous_gpa') else None
    # Fraternity Information
    semester_initiated = data.get('semester_initiated') if data.get('semester_initiated') else None
    executive_positions_held = data.get('executive_posions_held')  if data.get('executive_posions_held') else None
    other_positions_held = data.get('other_positions_held') if data.get('other_positions_held') else None
    fraternity_conferences_attended = data.get('fraternity_conferences_attended') if data.get('fraternity_conferences_attended') else None
    fraternity_text = data.get('fraternity_text') if data.get('fraternity_text') else None
    # Other Organization Information
    semesters_involvement = data.get('semesters_involvement') if data.get('semesters_involvement') else None
    other_org_executive_positions_held = data.get('other_org_executive_positions_held') if data.get('other_org_executive_positions_held') else None
    other_org_positions_held = data.get('other_org_positions_held') if data.get('other_org_positions_held') else None
    other_org_text = data.get('other_org_text') if data.get('other_org_text') else None
    # Community Service Information
    total_community_service_hours = data.get('total_community_service_hours') if data.get('total_community_service_hours') else None
    last_semester_community_service_hours = data.get('last_semester_community_service_hours') if data.get('last_semester_community_service_hours') else None
    community_service_text = data.get('community_service_text') if data.get('community_service_text') else None

    updated_at = datetime.now()
    cursor.execute(APPLICANT_ID, (email,))
    applicant_id = cursor.fetchone()[0]
    try:
        cursor.execute(NEW_APPLICATION_INSERT, (applicant_id, updated_at, a_number, first_semester, estimated_graduation, active_next_year, live_in_house, first_major, second_major, first_minor, second_minor, cumulative_gpa, previous_gpa, semester_initiated, executive_positions_held, other_positions_held, fraternity_conferences_attended, fraternity_text, semesters_involvement, other_org_executive_positions_held, other_org_positions_held, other_org_text, total_community_service_hours, last_semester_community_service_hours, community_service_text))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    return {"status": "success"}

@app.route('/load_application', methods=['GET'])
def load_application():
    email = request.args.get('email')
    cursor.execute("SELECT * FROM applications WHERE applicant_id = (SELECT applicant_id FROM applicants WHERE email = %s)", (email,))
    data = cursor.fetchone()
    
    if data:
        columns = [desc[0] for desc in cursor.description]
        application_data = dict(zip(columns, data))
        for key, value in application_data.items():
            if isinstance(value, datetime):
                application_data[key] = value.strftime('%Y-%m-%d')
        return jsonify(application_data)
    else:
        return jsonify({"status": "no_data"})


# Admin Routes
@app.route('/add_applicants', methods=['POST'])
def add_applicants():
    """Add applicants to the database."""
    # Load in Data via CSV our form, going to assume form untill front end is done for ADMIN
    # Going to need this to be in a FOR LOOP
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    cursor.execute(NEW_APPLICANT_INSERT, (first_name, last_name, email,))
    conn.commit()
    return Response(), 200

@app.route('/begin_scholarship_process', methods=['POST'])
def begin_scholarship_process():
    """Creates a password for all applicants and sends them an email. Starts the application process."""
    cursor.execute(NEW_APPLICANT_PASSWORD_SETUP)
    applicants = cursor.fetchall()
    for applicant in applicants:
        password = generate_password()
        hashed_password = hash_password(password)
        cursor.execute(NEW_APPLICANT_PASSWORD_UPDATE, (hashed_password, applicant[3]))
        send_new_applicant_email(applicant[3], password, applicant[1], applicant[2])
        conn.commit()
        time.sleep(5) # Sleep for 5 seconds to avoid rate limiting and being marked as spam-
    return Response(), 200

@app.route('/close_scholarship_process', methods=['POST'])
def close_scholarship_process():
    """Closes the scholarship process and calculates the scores for all applicants."""
    generate_scores()
    cursor.execute(REMOVE_ALL_PASSWORDS)
    conn.commit()
    #send_closed_scholarship_email() HAVE THIS FORMAT WITH THEIR HISTORICAL RESPONSES
    return Response(), 200



# Login Logic
@app.route('/login', methods=['POST'])
def login():
    """Login an applicant or reviewer."""
    email = request.form['email']
    password = request.form['password']
    cursor.execute(APPLICANT_LOGIN, (email,))
    stored_password = cursor.fetchone()
    if not stored_password:
        return redirect(url_for('error', message='Applicant does not exist'))
    if check_password(password, stored_password[0]):
        cursor.execute(APPLICANT_NAME, (email,))
        name = cursor.fetchone()
        return redirect(url_for('application', applicant_first_name=name[0], applicant_email=email))
    else:
        return redirect(url_for('error', message='Incorrect password'))

@app.route('/forgot_password', methods=['POST'])
def forgotPassword():
    """Send an email to the applicant with their password."""
    email = request.form['email']
    cursor.execute(APPLICANT_CHECK, (email, ))
    temp = cursor.fetchone()
    if not temp or temp[0] == None:
        return redirect(url_for('error', message='Applicant does not exist'))
    password = generate_password()
    hashed_password = hash_password(password)
    cursor.execute(APPLICANT_NAME, (email,))
    first_name, last_name = cursor.fetchone()
    send_forgot_password_email(email, password, first_name, last_name)
    cursor.execute(NEW_APPLICANT_INSERT, (first_name, last_name, email, hashed_password))
    conn.commit()
    return redirect(url_for('index'))

# Main Pages

@app.route('/application')
def application():
    applicant_name = request.args.get('applicant_first_name', '')
    if applicant_name == '':
        return redirect(url_for('error', message='Please login.'))
    return render_template('application.html', applicant_first_name=applicant_name, email=request.args.get('applicant_email'))

@app.route('/save_application', methods=['POST'])
def saveApplication():
    data = request.get_data(as_text=True)
    data = json.loads(data)
    return save_application_data(data)

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
        cursor.execute("DROP TABLE IF EXISTS applications CASCADE;")
        conn.commit()
        cursor.execute(CREATE_TABLES)
        conn.commit()
        code_executed = True
    app.run(debug=False, host='0.0.0.0', port=8080)