import requests
ARGO_SERVER_URL = "http://127.0.0.1:52369"  
NAMESPACE = "argo"
TEMPLATE_NAME = "pyspark-ml-training-template"

payload = {
    "namespace": NAMESPACE,
    "resourceKind": "WorkflowTemplate",
    "resourceName": TEMPLATE_NAME,
    "submitOptions": {
        "generateName": "training-run-"
    }
}

url = f"{ARGO_SERVER_URL}/api/v1/workflows/{NAMESPACE}/submit"
response = requests.post(url, json=payload)

if response.status_code == 200:
    workflow_name = response.json()["metadata"]["name"]
    print(f"Workflow '{workflow_name}' started successfully!")
else:
    print(f"Failed to start workflow. Status: {response.status_code}")
    print(response.text)
