from flask import Flask, request, jsonify, Response, stream_with_context
import json
import time
import os
import datetime

from api.data_db import save_commits_to_db, get_commits_from_db, save_analysis_to_db, save_repo_to_db, \
    get_all_repos_from_db, get_analysis_from_db
from core.git_operations import clone_repo, repo_exists, extract_contributions
from core.utils.code_files_loader import read_files_from_dict_list
from core.ml_operations.loader import load_codebert_model
from core.analysis.codebert_sliding_window import codebert_sliding_window
from config.settings import CLONED_REPO_BASE_PATH, CODEBERT_BASE_PATH

app = Flask(__name__)

# Load model
model = load_codebert_model(CODEBERT_BASE_PATH, 27)

def init_routes(app):
    @app.route('/commits', methods=['POST'])
    def list_commits():
        data = request.get_json()
        repo_url = data.get('repo_url')
        commit_limit = data.get('limit', 50)

        if not repo_url:
            return jsonify({"error": "Repository URL is required"}), 400

        repo_name = repo_url.split('/')[-1].replace('.git', '')

        if not repo_exists(repo_name):
            clone_repo(repo_url, os.path.join(CLONED_REPO_BASE_PATH, "fake_session_id", str(repo_name)))

        commits = extract_contributions(os.path.join(CLONED_REPO_BASE_PATH, "fake_session_id", repo_name),
                                        commit_limit=commit_limit)

        #print(commits)
        save_commits_to_db(repo_name, commits)

        return jsonify(commits)

    @app.route('/repos', methods=['POST'])
    def create_repo():
        data = request.json
        repo_name = data.get('repo_name')
        url = data.get('url', '')
        description = data.get('description', '')
        comments = data.get('comments', '')

        try:
            save_repo_to_db(repo_name, url, description, comments)
            return jsonify({"message": "Repository created successfully"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/repos/<string:repo_name>', methods=['PUT'])
    def edit_repo(repo_name):
        data = request.json
        url = data.get('url', '')
        description = data.get('description', '')
        comments = data.get('comments', '')

        try:
            save_repo_to_db(repo_name, url, description, comments)
            return jsonify({"message": "Repository updated successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/repos', methods=['GET'])
    def list_repos():
        try:
            repos = get_all_repos_from_db()
            return jsonify(repos), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/analyze', methods=['GET'])
    def analyze():
        repo_url = request.args.get('repo_url')

        if not repo_url:
            return jsonify({"error": "Repository URL is required"}), 400

        repo_name = repo_url.split('/')[-1].replace('.git', '')

        commits = get_commits_from_db(repo_name)

        if not commits:
            return jsonify({"error": "No commits found for the repository"}), 400

        files = read_files_from_dict_list(commits)

        analysis_results = []

        @stream_with_context
        def generate():
            for file in files.values():
                start_time = time.time()
                results = codebert_sliding_window([file], 35, 35, 1, 25, model)
                end_time = time.time()
                elapsed_time = end_time - start_time

                if isinstance(file.timestamp, datetime.datetime):
                    timestmp = file.timestamp.isoformat()
                else:
                    timestmp = file.timestamp

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

            save_analysis_to_db(repo_name, analysis_results)
            yield "data: end\n\n"

        return Response(generate(), mimetype='text/event-stream')

    from flask import Flask, jsonify, request

    app = Flask(__name__)

    @app.route('/analyzedb', methods=['GET'])
    def analyzedb():
        try:
            # Παίρνουμε το repo_name από τα query parameters (π.χ., /analyzedb?repo_name=my_repo)
            repo_name = request.args.get('repo_name')

            if not repo_name:
                return jsonify({"error": "repo_name parameter is required"}), 400

            # Καλούμε τη συνάρτηση για να ανακτήσουμε τα δεδομένα από τη βάση
            analysis_data = get_analysis_from_db(repo_name)

            if analysis_data is None:
                return jsonify({"error": "Failed to retrieve analysis data"}), 500

            # Επιστρέφουμε τα δεδομένα σε μορφή JSON
            return jsonify(analysis_data), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    if __name__ == '__main__':
        app.run(debug=True)


if __name__ == '__main__':
    app.run(debug=True)
