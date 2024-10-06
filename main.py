from flask import Flask, Response
from queries import *
import os, psycopg2
import secrets
import string
import csv
import bcrypt

app = Flask(__name__)

# Helper Methods
def generate_password():
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(12))
    return password

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def check_password(input_password, stored_password):
    if bcrypt.checkpw(input_password.encode('utf-8'), stored_password):
        return True
    return False




# Applicant

@app.route('/newapplicant', methods=['GET'])
def newApplicant():
    """Create a new applicant in the database and send them an email to fill out initial information."""
    with open('./Settings/new_applicants.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
           password = generate_password()
           pass_hash = hash_password(password)
           print(check_password(password, pass_hash))
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