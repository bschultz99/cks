from flask import Flask, Response
from queries import *
import os, psycopg2
import secrets
import string
import csv

app = Flask(__name__)


# Applicant

@app.route('/newapplicant', methods=['POST'])
def newApplicant():
    """Create a new applicant in the database and send them an email to fill out initial information."""
    with open('./Settings/new_applicants.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            print(row)
    return Response(), 200

















if __name__ == "__main__":
    conn = psycopg2.connect(database=os.getenv("PGDATABASE"),
                            host=os.getenv("PGHOST"),
                            user=os.getenv("POSTGRES_USER"),
                            password=os.getenv("POSTGRES_PASSWORD"),
                            port=os.getenv("PGPORT"))
    cursor = conn.cursor()
    cursor.execute("DROP TABLE applicants;")
    conn.commit()
    cursor.execute("DROP TABLE applications;")
    conn.commit()
    cursor.execute("DROP TABLE reviewers;")
    conn.commit()
    cursor.execute("DROP TABLE reviews;")
    conn.commit()
    cursor.execute(CREATE_TABLES)
    conn.commit()
    app.run(debug=True, port=8080)