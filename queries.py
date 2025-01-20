"""Queries"""

# ***** TABLES *****
CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS applicants (
    applicant_id SERIAL PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR(255)
    );
CREATE TABLE IF NOT EXISTS applications (
    application_id SERIAL PRIMARY KEY,
    applicant_id INTEGER REFERENCES applicants (applicant_id),
    submission_date DATE,
    due_date DATE,
    status VARCHAR(255),
    first_semester DATE,
    estimated_graduation DATE,
    active_next_year BOOLEAN,
    live_in_house BOOLEAN,
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
    semesters_involvement INTEGER,
    other_org_executive_positions_held INTEGER,
    other_org_positions_held INTEGER,
    total_community_service_hours INTEGER,
    score FLOAT
    );
CREATE TABLE IF NOT EXISTS reviewers (
    reviewer_id SERIAL PRIMARY KEY,
    channel_id VARCHAR(255),
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
"""

# ***** APPLICANTS QUERIES *****

NEW_APPLICANT_CHECK = '''
SELECT email FROM applicants WHERE email = %s;
'''

NEW_APPLICANT_INSERT = '''
INSERT INTO applicants(first_name,
                       last_name,
                       email,
                       password)
VALUES (%s, %s, %s, %s)
ON CONFLICT (applicant_id)
DO UPDATE SET first_name = excluded.first_name,
              last_name = excluded.last_name,
              email = excluded.email,
              password = excluded.password
'''
