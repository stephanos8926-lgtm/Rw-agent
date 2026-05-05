import subprocess

def deploy_to_cloud_run(project_id: str, service_name: str, region: str = "us-east1"):
    """
    Simulates deployment to Google Cloud Run utilizing gcloud CLI.
    """
    cmd = [
        "gcloud", "run", "deploy", service_name,
        "--source", ".",
        "--region", region,
        "--project", project_id,
        "--allow-unauthenticated"
    ]
    # return subprocess.check_output(cmd, text=True)
    return f"Successfully deployed {service_name} to Cloud Run in {region}."

def deploy_to_vercel(token: str):
    """
    Simulates deployment to Vercel via Vercel CLI.
    """
    cmd = ["vercel", "--prod", "--token", token]
    # return subprocess.check_output(cmd, text=True)
    return "Successfully deployed project to Vercel."
