import json
from datetime import datetime

import psycopg2

# Database connection settings
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'test'
DB_USER = 'root'
DB_PASSWORD = '30a301d725711'


def get_db_connection():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn


def create_tables():
    commands = [
        '''
        CREATE TABLE commits (
            id SERIAL PRIMARY KEY,
            repo_name VARCHAR(255),
            author VARCHAR(255),
            file_content TEXT,
            changed_lines INTEGER[],
            temp_filepath VARCHAR(255),
            timestamp TIMESTAMP,
            sha VARCHAR(255)
        )


        ''',
        '''
        CREATE TABLE analysis_results (
            id SERIAL PRIMARY KEY,
            repo_name VARCHAR(255),
            filename VARCHAR(255),
            author VARCHAR(255),
            timestamp TIMESTAMP,
            sha VARCHAR(255),
            detected_kus JSONB,
            elapsed_time FLOAT
        )
        '''
    ]

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        cur.close()
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn is not None:
            conn.close()


def save_commits_to_db(repo_name, commits):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        for commit in commits:
            cur.execute('''
                INSERT INTO commits (repo_name, sha, author, file_content, changed_lines, temp_filepath, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                repo_name,
                commit.get('sha'),
                commit.get('author'),
                commit.get('file_content'),
                commit.get('changed_lines'),
                commit.get('temp_filepath'),
                commit.get('timestamp')
            ))
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()




def get_commits_from_db(repo_name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT sha, author, file_content, changed_lines, temp_filepath, timestamp
            FROM commits
            WHERE repo_name = %s
        ''', (repo_name,))
        rows = cur.fetchall()
        cur.close()

        # Convert the list of tuples to a list of dictionaries
        commits = []
        for row in rows:
            commit = {
                "sha": row[0],
                "author": row[1],
                "file_content": row[2],
                "changed_lines": row[3],
                "temp_filepath": row[4],
                "timestamp": row[5]
            }
            commits.append(commit)

        return commits
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        conn.close()


def save_analysis_to_db(repo_name, analysis_data):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        for data in analysis_data:
            detected_kus_serialized = json.dumps(data["detected_kus"],
                                                 default=str)  # Convert detected_kus to JSON string
            timestamp_serialized = data["timestamp"].isoformat() if isinstance(data["timestamp"], datetime) else data[
                "timestamp"]
            cur.execute('''
                INSERT INTO analysis_results (repo_name, filename, author, timestamp, sha, detected_kus, elapsed_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                repo_name,
                data["filename"],
                data["author"],
                timestamp_serialized,
                data["sha"],
                detected_kus_serialized,
                data["elapsed_time"]
            ))
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()