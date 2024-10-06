from flask import Flask, Response
from queries import *
import os, psycopg2
import secrets
import string
import csv

app = Flask(__name__)


# Applicant

@app.route('/newapplicant', methods=['GET'])
def newApplicant():
    """Create a new applicant in the database and send them an email to fill out initial information."""
    characters = string.ascii_letters + string.digits + string.punctuation
    with open('./Settings/new_applicants.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            password = ''.join(secrets.choice(characters) for _ in range(12))
            print(password)
    return Response(), 200

















if __name__ == "__main__":
    conn = psycopg2.connect(database=os.getenv("PGDATABASE"),
                            host=os.getenv("PGHOST"),
                            user=os.getenv("POSTGRES_USER"),
                            password=os.getenv("POSTGRES_PASSWORD"),
                            port=os.getenv("PGPORT"))
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLES)
    conn.commit()
    app.run(debug=True, host='0.0.0.0', port=8080)