from flask import Flask, request, jsonify, render_template
from kubernetes import client, config
import base64

app = Flask(__name__)

# Load Kubernetes configuration
config.load_incluster_config()
api = client.CustomObjectsApi()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def UploadScript():
    # Get 'script' and 'image' from the request form
    script = request.form['script']
    image = request.form['image']
    # Define the custom resource definition (CRD) payload
    body = {
        "apiVersion": "learn-k8s.com/v1",
        "kind": "PythonScriptContainer",
        "metadata": {"name": "my-python-script"},
        "spec": {
            "script": script,
            "image": image
        }
    }
    
    # Create the custom resource in the Kubernetes cluster
    api.create_namespaced_custom_object(
        group="learn-k8s.com",
        version="v1",
        namespace="default",
        plural="python-script-containers",
        body=body
    )
    
    return jsonify({"status": "success"}), 201

@app.route('/logs/<pod_name>', methods=['GET'])
def GetLogs(pod_name):
    # Create a CoreV1Api client for interacting with pods
    core_api = client.CoreV1Api()
    
    # Get the logs from the specified pod
    try:
        logs = core_api.read_namespaced_pod_log(name=pod_name, namespace='default')
    except client.exceptions.ApiException as e:
        return jsonify({"error": str(e)}), 404
    
    return jsonify({"logs": logs})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
