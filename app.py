from flask import Flask, render_template, jsonify, request, send_file
import os
import subprocess
import zipfile
import io
from pathlib import Path
from flask_socketio import SocketIO, emit
from threading import Thread
import time
import uuid

app = Flask(__name__)
socketio = SocketIO(app)
main_dir = os.getcwd()
gradle_exe = os.path.join(main_dir,"builds","gradlew.bat")

def get_m2_path():
    home_dir = os.path.expanduser("~")
    m2_path = os.path.join(home_dir, ".m2", "repository")
    return m2_path


def list_jar_files(path):
    """
    List all JAR files in the given directory.
    """
    jars = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".jar"):
                jars.append(os.path.join(root, file))
    return jars


@app.route("/")
def index():
    libraries = check_m2_repository()
    if not libraries:
        run_gradle_task()
        libraries = check_m2_repository()
    return render_template("index.html", libraries=libraries)


@app.route("/get_items/", defaults={"path": ""})
@app.route("/get_items/<path:path>")
def get_items(path):
    # The base directory of the .m2 repository
    base_dir = Path(get_m2_path())
    target_dir = base_dir / path.replace(":", "/")

    if not path or target_dir.is_dir():
        # List directories and JAR files in the current directory
        items = [
            str(p.relative_to(base_dir))
            for p in target_dir.iterdir()
            if p.is_dir() or p.suffix == ".jar"
        ]
    else:
        # If the path is not a directory, list JAR files inside it
        items = list_jar_files(str(target_dir))

    return jsonify(items)


@app.route("/library/<path:library_path>")
def library_details(library_path):
    try:
        # Convert URL path to file system path
        library_path = os.path.join(get_m2_path(), library_path)
        print(library_path)
        if not os.path.isfile(library_path):
            return jsonify({"error": "File not found"}), 404

        jar_contents = get_jar_contents(library_path)
        return jsonify({"files": jar_contents})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def check_m2_repository():
    m2_path = get_m2_path()
    libraries = []

    for root, _, files in os.walk(m2_path):
        for file in files:
            if file.endswith(".jar"):
                lib_path = os.path.join(root, file)
                libraries.append(lib_path)

    return libraries


def get_jar_contents(jar_path):
    with zipfile.ZipFile(jar_path, "r") as jar:
        date = time.ctime(os.path.getmtime(jar.filename))
        print(date)
        return [
            j.filename + ":::::" + date
            for j in jar.infolist()
            if j.filename.endswith(".class")
        ]


def get_main_connector_folder_path():
    with open("main_connector_folder", "r") as file:
        return file.readline().strip()


@app.route("/run_gradle_task", methods=["POST"])
def run_gradle_task_api():
    version = request.json.get("version", "0.4.1")  # Default version if not provided

    def run_gradle():
        subprocess.run(
            [
                gradle_exe,
                "publishToMavenLocal",
                "-Pskip.signing=true",
                f"-Pversion={version}",
                "-xjavadoc",
            ], cwd=get_main_connector_folder_path()
        )
        socketio.emit("gradle_status", {"status": "Done"}, namespace="/")

    os.chdir(main_dir)
    # Start the background task using Flask-SocketIO
    socketio.start_background_task(run_gradle)
    return jsonify({"message": "Gradle task started"}), 200


@app.route("/create-launcher")
def create_launcher():
    return render_template("create_launcher.html")


@app.route('/process_code', methods=['POST'])
def process_code():
    try:
        data = request.json
        code = data['code']

        # Create a unique directory inside 'build' folder
        dir_name = os.path.join('builds', str(uuid.uuid4()))
        os.makedirs(dir_name, exist_ok=True)

        # Create a file with the code
        file_path = os.path.join(dir_name, 'build.gradle.kts')
        with open(file_path, 'w') as file:
            file.write(code)

        # Run Gradle task (assuming gradle is in the parent of 'build' directory)
        subprocess.run([gradle_exe, 'clean build'], cwd=dir_name)

        # Assuming the JAR file is created in 'build/libs' inside dir_name
        jar_path = os.path.join(dir_name, 'build', 'libs')
        jar_files = [f for f in os.listdir(jar_path) if f.endswith('.jar')]

        if jar_files:
            return send_file(os.path.join(jar_path, jar_files[0]), as_attachment=True)
        else:
            return jsonify({'status': 'error', 'message': 'JAR file not created'}), 400

    except Exception as e:
        print(e)
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
