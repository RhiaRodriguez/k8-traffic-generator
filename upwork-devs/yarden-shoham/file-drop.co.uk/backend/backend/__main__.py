from flask import Flask, request, render_template
from kubernetes import client, config
import os
import uuid


class Scheduler:
    @staticmethod
    def schedule(files):
        for file in files:
            Scheduler.__save_file(file)
            Scheduler.__schedule_job_in_kubernetes(file)

    @staticmethod
    def __save_file(file):
        file.save(f"/usr/src/app/backend/static/{file.filename}")

    @staticmethod
    def __schedule_job_in_kubernetes(file):
        job_name = f"file-drop-{uuid.uuid1()}"

        envs = [client.V1EnvVar(
                name="API_TOKEN", value=os.getenv("API_TOKEN")), client.V1EnvVar(
                name="TARGET", value=f"http://file-drop-traffic-generator-backend:5000/backend/static/{file.filename}")]

        processor_container = client.V1Container(
            name="processor",
            image="yardenshoham/file-drop-processor",
            env=envs)

        pod_spec = client.V1PodSpec(
            restart_policy="OnFailure",
            containers=[processor_container])

        # Create and configure a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(name=job_name),
            spec=pod_spec)

        # Create the specification of the job
        spec = client.V1JobSpec(
            template=template)

        # Instantiate the job object
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(name=job_name),
            spec=spec)

        client.BatchV1Api().create_namespaced_job(
            body=job,
            namespace="default")
        print(job_name)


app = Flask(import_name=__name__, static_url_path="/backend/static")


@app.route("/backend/health")
def health():
    return ""


@app.route("/backend/files", methods=["POST"])
def upload():
    uploaded_files = request.files.getlist("files[]")
    Scheduler.schedule(uploaded_files)
    return ""


if __name__ == '__main__':
    config.load_incluster_config()
    app.run(debug=True, host='0.0.0.0')
