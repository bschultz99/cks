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
    submission_date DATE,
    status VARCHAR(255),
    applicant_id INTEGER REFERENCES applicants (applicant_id),
    document_path VARCHAR(255),
    due_date DATE
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

APPLICANTS_INSERT = '''
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
