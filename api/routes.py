from flask import Flask, request, jsonify, Response, stream_with_context
import json
import time
import os

from api.data_db import save_commits_to_db, get_commits_from_db, save_analysis_to_db
from core.git_operations import clone_repo, repo_exists, extract_contributions
from core.utils.code_files_loader import read_files_from_dict_list
from core.ml_operations.loader import load_codebert_model
from core.analysis.codebert_sliding_window import codebert_sliding_window
from config.settings import CLONED_REPO_BASE_PATH, CODEBERT_BASE_PATH
import datetime

app = Flask(__name__)

# Load model
model = load_codebert_model(CODEBERT_BASE_PATH, 27)


def init_routes(app):
    @app.route('/commits', methods=['POST'])
    def list_commits():
        # Get parameters from the request
        data = request.get_json()
        repo_url = data.get('repo_url')
        commit_limit = data.get('limit', 50)

        # If the repository URL is not provided, return an error
        if not repo_url:
            return jsonify({"error": "Repository URL is required"}), 400

        # Remove the .git extension (if present) and extract the repository name
        repo_name = repo_url.split('/')[-1].replace('.git', '')

        # If the repository is already cloned, use the existing clone
        if not repo_exists(repo_name):
            clone_repo(repo_url, os.path.join(CLONED_REPO_BASE_PATH, "fake_session_id", str(repo_name)))

        # Extract the commits from the repository and limit the number of examined commits
        commits = extract_contributions(os.path.join(CLONED_REPO_BASE_PATH, "fake_session_id", repo_name),
                                        commit_limit=commit_limit)

        # Store the selected commits in memory
        selected_commits = {}
        selected_commits[repo_name] = commits

        print(commits)
        # Save the commits to the database
        save_commits_to_db(repo_name, commits)

        # Return the list of commits and their details
        return jsonify(commits)

    @app.route('/analyze', methods=['GET'])
    def analyze():
        # Get parameters from the query string
        repo_url = request.args.get('repo_url')

        # If the repository URL is not provided, return an error
        if not repo_url:
            return jsonify({"error": "Repository URL is required"}), 400

        # Remove the .git extension (if present) and extract the repository name
        repo_name = repo_url.split('/')[-1].replace('.git', '')

        # Get the commits from the database
        commits = get_commits_from_db(repo_name)

        # If no commits are found, return an error
        if not commits:
            return jsonify({"error": "No commits found for the repository"}), 400

        # Prepare the list of files to analyze
        files = read_files_from_dict_list(commits)

        analysis_results = []

        @stream_with_context
        def generate():
            for file in files.values():
                # Perform the analysis on a single file
                start_time = time.time()  # Start the timer
                results = codebert_sliding_window([file], 35, 35, 1, 25, model)
                end_time = time.time()  # Stop the timer
                elapsed_time = end_time - start_time

                if isinstance(file.timestamp, datetime.datetime):
                    timestmp=file.timestamp.isoformat()

                file_data = {
                    "filename": file.filename,
                    "author": file.author,
                    "timestamp": timestmp,
                    "sha": file.sha,
                    "detected_kus": file.ku_results,
                    "elapsed_time": elapsed_time
                }
                analysis_results.append(file_data)
                yield f"data: {json.dumps(file_data)}\n\n"

            # Save analysis results to the database
            save_analysis_to_db(repo_name, analysis_results)

            # Send a special message to indicate the end of the stream
            yield "data: end\n\n"

        return Response(generate(), mimetype='text/event-stream')
