from flask import Flask
import os, psycopg2

app = Flask(__name__)


CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS applicants (
    applicant_id INTEGER PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR(255)
    );
CREATE TABLE IF NOT EXISTS applications (
    application_id INTEGER PRIMARY KEY,
    submission_date DATE,
    status VARCHAR(255),
    applicant_id INTEGER REFERENCES applicants (applicant_id),
    document_path VARCHAR(255),
    due_date DATE
    );
CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY,
    application_id INTEGER REFERENCES applications (application_id),
    reviewer_id INTEGER REGERENCES reviewers (reviewer_id)
    reviewer_amount INTEGER
    );
CREATE TABLE IF NOT EXISTS reviewers (
    reviewer_id INTEGER PRIMARY KEY,
    channel_id VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR(255),
    admin BOOLEAN DEFAULT FALSE
);
"""



if __name__ == "__main__":
    conn = psycopg2.connect(database=os.getenv("PGDATABASE"),
                            host=os.getenv("PGHOST"),
                            user=os.getenv("POSTGRES_USER"),
                            password=os.getenv("POSTGRES_PASSWORD"),
                            port=os.getenv("PGPORT"))
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLES)
    conn.commit()
    app.run(debug=True, port=8080)