from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import os
import tempfile
import time

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/run', methods=['POST'])
def run_code():
    data = request.get_json()
    language = data.get('language', '').lower()
    code = data.get('code', '')

    if not code:
        return jsonify({'status': 'ERROR', 'output': 'No code provided.'}), 400

    start_time = time.time()

    try:
        if language == 'cpp':
            result, status = execute_cpp(code)
        elif language == 'java':
            result, status = execute_java(code)
        elif language == 'python':
            result, status = execute_python(code)
        else:
            return jsonify({'status': 'ERROR', 'output': 'Unsupported language.'}), 400

        exec_time = int((time.time() - start_time) * 1000)
        return jsonify({
            'status': status,
            'output': result,
            'executionTime': exec_time
        })

    except Exception as e:
        return jsonify({'status': 'ERROR', 'output': str(e)}), 500


def execute_cpp(code):
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = os.path.join(temp_dir, "main.cpp")
        exec_path = os.path.join(temp_dir, "main.exe" if os.name == 'nt' else "main")

        with open(source_path, "w") as f:
            f.write(code)

        # Compile
        compile_process = subprocess.run(
            ["g++", source_path, "-o", exec_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        if compile_process.returncode != 0:
            return compile_process.stderr, "COMPILATION_ERROR"

        # Execute
        try:
            run_process = subprocess.run(
                [exec_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            return run_process.stdout or run_process.stderr, "SUCCESS"
        except subprocess.TimeoutExpired:
            return "Execution Timed Out (Limit: 5 Seconds)", "TIME_LIMIT_EXCEEDED"


def execute_java(code):
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = os.path.join(temp_dir, "Main.java")

        with open(source_path, "w") as f:
            f.write(code)

        # Compile
        compile_process = subprocess.run(
            ["javac", source_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        if compile_process.returncode != 0:
            return compile_process.stderr, "COMPILATION_ERROR"

        # Execute
        try:
            run_process = subprocess.run(
                ["java", "-cp", temp_dir, "Main"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return run_process.stdout or run_process.stderr, "SUCCESS"
        except subprocess.TimeoutExpired:
            return "Execution Timed Out (Limit: 5 Seconds)", "TIME_LIMIT_EXCEEDED"


def execute_python(code):
    try:
        run_process = subprocess.run(
            ["python", "-c", code],
            capture_output=True,
            text=True,
            timeout=5
        )
        output = run_process.stdout if run_process.returncode == 0 else run_process.stderr
        return output, "SUCCESS" if run_process.returncode == 0 else "RUNTIME_ERROR"
    except subprocess.TimeoutExpired:
        return "Execution Timed Out (Limit: 5 Seconds)", "TIME_LIMIT_EXCEEDED"


if __name__ == '__main__':
    print("--------------------------------------------------")
    print(" Python Code Evaluator Server Started!")
    print(" Local Access: http://127.0.0.1:5000")
    print("--------------------------------------------------")
    app.run(debug=True, port=5000)