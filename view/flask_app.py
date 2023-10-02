# flask_app.py
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import glob

app = Flask(__name__)

stored_data = {}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/autocomplete", methods=["POST"])
def autocomplete():
    partial_path = request.json["partial_path"]
    print(partial_path)
    matching_folders = glob.glob(f"{partial_path}*")
    sorted_folders = sorted(matching_folders)
    print(sorted_folders)
    return jsonify({"suggestions": sorted_folders})


@app.route("/zarrify", methods=["POST"])
def zarrify():
    data = request.get_json()
    project_folder = data["project_folder"]
    stored_data["project_folder"] = project_folder
    sub_folders = glob.glob(f"{project_folder}*")
    sub_folders = [
        os.path.basename(folder) for folder in sub_folders if "." not in folder
    ]
    stored_data["sub_folders"] = sub_folders
    return jsonify(stored_data)


@app.route("/getdata", methods=["GET"])
def getdata():
    print(stored_data)
    return jsonify(stored_data)  # Return stored data


if __name__ == "__main__":
    CORS(app)
    app.run(port=5001)
