"""Queries"""

# ***** TABLES *****
CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS applicants (
    applicant_id SERIAL PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255)
    );
CREATE TABLE IF NOT EXISTS applications (
    application_id SERIAL PRIMARY KEY,
    applicant_id INTEGER REFERENCES applicants (applicant_id) UNIQUE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    a_number VARCHAR(255),
    first_semester DATE,
    estimated_graduation DATE,
    active_next_year VARCHAR(255),
    live_in_house VARCHAR(255),
    first_major VARCHAR(255),
    second_major VARCHAR(255),
    first_minor VARCHAR(255),
    second_minor VARCHAR(255),
    cumulative_gpa FLOAT,
    previous_gpa FLOAT,
    semester_initiated DATE,
    executive_posions_held INTEGER,
    other_positions_held INTEGER,
    fraternity_conferences_attended INTEGER,
    fraternity_text VARCHAR(10000),
    semesters_involvement INTEGER,
    other_org_executive_positions_held INTEGER,
    other_org_positions_held INTEGER,
    other_org_text VARCHAR(10000),
    total_community_service_hours INTEGER,
    last_semester_community_service_hours INTEGER,
    community_service_text VARCHAR(10000),
    essay_question_1 VARCHAR(10000),
    essay_question_2 VARCHAR(10000),
    essay_question_3 VARCHAR(10000),
    essay_question_4 VARCHAR(10000),
    score FLOAT,
    recommended_scholarship_amount INTEGER
    );
CREATE TABLE IF NOT EXISTS reviewers (
    reviewer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR(255),
    admin BOOLEAN DEFAULT FALSE
);
CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications (application_id),
    reviewer_id INTEGER REFERENCES reviewers (reviewer_id),
    reviewer_amount INTEGER
    );
CREATE TABLE IF NOT EXISTS key_values (
    scholarship_total INTEGER,
    start_date DATE,
    end_date DATE
    );
"""

# ***** APPLICANTS QUERIES *****

APPLICANT_CHECK = '''
SELECT password FROM applicants WHERE email = %s;
'''

APPLICANT_NAME = '''
SELECT first_name, last_name FROM applicants WHERE email = %s;
'''

NEW_APPLICANT_INSERT = '''
INSERT INTO applicants(first_name,
                       last_name,
                       email,
                       password)
VALUES (%s, %s, %s)
ON CONFLICT (email)
DO UPDATE SET first_name = excluded.first_name,
              last_name = excluded.last_name,
              email = excluded.email;
'''

NEW_APPLICANT_PASSWORD_UPDATE = '''
UPDATE applicants SET password = %s WHERE email = %s;
'''

NEW_APPLICANT_PASSWORD_SETUP = '''
SELECT * FROM applicants;
'''

APPLICANT_ID = '''
SELECT applicant_id FROM applicants WHERE email = %s;
'''

APPLICANT_LOGIN = '''
SELECT password FROM applicants WHERE email = %s;
'''

REMOVE_ALL_PASSWORDS = '''
UPDATE applicants SET password = NULL;
'''

# ***** APPLICATION QUERIES *****
NEW_APPLICATION_INSERT = '''
INSERT INTO applications(applicant_id,
updated_at,
a_number,
first_semester,
estimated_graduation,
active_next_year,
live_in_house,
first_major,
second_major,
first_minor,
second_minor,
cumulative_gpa,
previous_gpa,
semester_initiated,
executive_posions_held,
other_positions_held,
fraternity_conferences_attended,
fraternity_text,
semesters_involvement,
other_org_executive_positions_held,
other_org_positions_held,
other_org_text,
total_community_service_hours,
last_semester_community_service_hours,
community_service_text,
essay_question_1,
essay_question_2,
essay_question_3,
essay_question_4)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (applicant_id) DO UPDATE SET
updated_at = excluded.updated_at,
a_number = excluded.a_number,
first_semester = excluded.first_semester,
estimated_graduation = excluded.estimated_graduation,
active_next_year = excluded.active_next_year,
live_in_house = excluded.live_in_house,
first_major = excluded.first_major,
second_major = excluded.second_major,
first_minor = excluded.first_minor,
second_minor = excluded.second_minor,
cumulative_gpa = excluded.cumulative_gpa,
previous_gpa = excluded.previous_gpa,
semester_initiated = excluded.semester_initiated,
executive_posions_held = excluded.executive_posions_held,
other_positions_held = excluded.other_positions_held,
fraternity_conferences_attended = excluded.fraternity_conferences_attended,
fraternity_text = excluded.fraternity_text,
semesters_involvement = excluded.semesters_involvement,
other_org_executive_positions_held = excluded.other_org_executive_positions_held,
other_org_positions_held = excluded.other_org_positions_held,
other_org_text = excluded.other_org_text,
total_community_service_hours = excluded.total_community_service_hours,
last_semester_community_service_hours = excluded.last_semester_community_service_hours,
community_service_text = excluded.community_service_text,
essay_question_1 = excluded.essay_question_1,
essay_question_2 = excluded.essay_question_2,
essay_question_3 = excluded.essay_question_3,
essay_question_4 = excluded.essay_question_4;
'''


# ***** SCORE QUERIES *****
COUNT_OF_APPLICATIONS = '''
SELECT COUNT(*) FROM applications;
'''