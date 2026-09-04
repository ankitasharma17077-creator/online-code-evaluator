from flask import Flask, render_template, request, jsonify
import subprocess
import os
import uuid

app = Flask(__name__)

TEMP_DIR = "temp_code"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run_code():
    data = request.get_json()
    code = data.get("code", "")
    language = data.get("language", "python")
    user_input = data.get("input", "")

    file_id = str(uuid.uuid4())
    
    try:
        if language == "python":
            # Safe wrapper to catch EOFError automatically for input()
            safe_code = f"""import sys

def _safe_input(prompt=""):
    try:
        line = sys.stdin.readline()
        if not line:
            return ""
        return line.rstrip("\\r\\n")
    except Exception:
        return ""

input = _safe_input

{code}
"""
            file_path = os.path.join(TEMP_DIR, f"{file_id}.py")
            with open(file_path, "w") as f:
                f.write(safe_code)
            
            process = subprocess.run(
                ["python3", file_path],
                input=user_input,
                text=True,
                capture_output=True,
                timeout=10
            )
            output = process.stdout if process.returncode == 0 else process.stderr

        elif language == "cpp":
            file_path = os.path.join(TEMP_DIR, f"{file_id}.cpp")
            exe_path = os.path.join(TEMP_DIR, f"{file_id}.out")
            with open(file_path, "w") as f:
                f.write(code)
            
            compile_process = subprocess.run(
                ["g++", file_path, "-o", exe_path],
                capture_output=True,
                text=True
            )
            
            if compile_process.returncode != 0:
                output = compile_process.stderr
            else:
                run_process = subprocess.run(
                    [exe_path],
                    input=user_input,
                    text=True,
                    capture_output=True,
                    timeout=10
                )
                output = run_process.stdout if run_process.returncode == 0 else run_process.stderr
                if os.path.exists(exe_path):
                    os.remove(exe_path)

        elif language == "java":
            class_name = f"Main_{file_id.replace('-', '_')}"
            formatted_code = code.replace("class Main", f"class {class_name}")
            file_path = os.path.join(TEMP_DIR, f"{class_name}.java")
            
            with open(file_path, "w") as f:
                f.write(formatted_code)
            
            compile_process = subprocess.run(
                ["javac", file_path],
                capture_output=True,
                text=True
            )
            
            if compile_process.returncode != 0:
                output = compile_process.stderr
            else:
                run_process = subprocess.run(
                    ["java", "-cp", TEMP_DIR, class_name],
                    input=user_input,
                    text=True,
                    capture_output=True,
                    timeout=10
                )
                output = run_process.stdout if run_process.returncode == 0 else run_process.stderr
                class_file = os.path.join(TEMP_DIR, f"{class_name}.class")
                if os.path.exists(class_file):
                    os.remove(class_file)

        else:
            output = "Unsupported Language"

    except subprocess.TimeoutExpired:
        output = "Error: Code Execution Timed Out"
    except Exception as e:
        output = str(e)
    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

    return jsonify({"output": output})

if __name__ == "__main__":
    app.run(debug=True)