from flask import Flask
import os, psycopg2

app = Flask(__name__)


CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS applications (
    slack_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    membership VARCHAR(255)
    );
CREATE TABLE IF NOT EXISTS takedowns (
    slack_id VARCHAR(255) PRIMARY KEY REFERENCES users(slack_id) ON DELETE CASCADE,
    takedown_count INTEGER DEFAULT 0,
    monday_lunch BOOLEAN DEFAULT FALSE,
    monday_dinner BOOLEAN DEFAULT FALSE,
    tuesday_lunch BOOLEAN DEFAULT FALSE,
    tuesday_dinner BOOLEAN DEFAULT FALSE,
    wednesday_lunch BOOLEAN DEFAULT FALSE,
    wednesday_dinner BOOLEAN DEFAULT FALSE,
    thursday_lunch BOOLEAN DEFAULT FALSE,
    thursday_dinner BOOLEAN DEFAULT FALSE,
    friday_lunch BOOLEAN DEFAULT FALSE,
    friday_dinner BOOLEAN DEFAULT FALSE
    );
CREATE TABLE IF NOT EXISTS takedown_channels (
    takedown_slot VARCHAR(255) PRIMARY KEY,
    channel_id VARCHAR(255)
    );
CREATE TABLE IF NOT EXISTS cleanup_channels (
    cleanup VARCHAR(255) PRIMARY KEY,
    channel_id VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS positions (
    position VARCHAR(255) PRIMARY KEY,
    slack_id VARCHAR(255)
    ); 
CREATE TABLE IF NOT EXISTS cleanups (
    slack_id VARCHAR(255) PRIMARY KEY REFERENCES users(slack_id) ON DELETE CASCADE,
    used BOOLEAN DEFAULT FALSE,
    disabled BOOLEAN DEFAULT FALSE,
    captain BOOLEAN DEFAULT FALSE,
    captain_count INTEGER DEFAULT 0,
    kitchen INTEGER DEFAULT 0,
    zero_deck INTEGER DEFAULT 0,
    first_deck INTEGER DEFAULT 0,
    bathrooms INTEGER DEFAULT 0,
    stairs_halls_brojo_brolo INTEGER DEFAULT 0,
    deck_brush INTEGER DEFAULT 0
);
"""



if __name__ == "__main__":
    conn = psycopg2.connect(database=os.getenv("PGDATABASE"),
                            host=os.getenv("PGHOST"),
                            user=os.getenv("POSTGRES_USER"),
                            password=os.getenv("POSTGRES_PASSWORD"),
                            port=os.getenv("PGPORT"))
    cursor = conn.cursor()
    #cursor.execute("DROP TABLE APPLICANTS;")
    #conn.commit()
    app.run(debug=True, port=8080)