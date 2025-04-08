from flask import Flask, request, jsonify
import os
import subprocess

app = Flask(__name__)

@app.route("/trigger-spark", methods=["POST"])
def trigger_spark():
    cmd = "kubectl create -f spark-job.yaml" 
    subprocess.run(cmd, shell=True, check=True)
    return jsonify({"status": "Spark job submitted!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)