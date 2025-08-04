import os
import subprocess
import kfp
import kfp.client
from kfp import dsl, components
from kfp import compiler

run_notebook_in_proc = components.load_component_from_file('../components/run-notebook-out-of-proc-component.yaml')

@dsl.pipeline(name="ex2 pipeline")
def mlflow_experiment_pipeline(git_url: str, env: dict):
    # Run MLFlow Experiment
    run_task = run_notebook_in_proc(git_url=git_url,
                                    run_from_dir="ex2-mlflow_and_python_dsl_pipeline",
                                    notebook_name="mlflow_parameters.ipynb",
                                    parameters = env)
    run_task.set_display_name("mlflow-experiment")
    run_task.set_caching_options(enable_caching=False)

# Get OpenShift Token
token = subprocess.check_output("oc whoami -t", shell=True, text=True).strip()

# Connect to the pipeline server
print ("Connecting to pipeline server")
kfp_client = kfp.Client(host="https://ds-pipeline-dspa-pipeline-sandbox.apps.ocp.home.glroland.com/",
                        existing_token=token,
                        verify_ssl=False)

# Grab local environment variables
env_to_propagate = dict()
if "AWS_ACCESS_KEY_ID" in os.environ:
    env_to_propagate["aws_access_key_id"] = os.environ["AWS_ACCESS_KEY_ID"]
if "AWS_SECRET_ACCESS_KEY" in os.environ:
    env_to_propagate["aws_secret_key"] = os.environ["AWS_SECRET_ACCESS_KEY"]
if "AWS_DEFAULT_REGION" in os.environ:
    env_to_propagate["aws_default_region"] = os.environ["AWS_DEFAULT_REGION"]
if "MLFLOW_S3_ENDPOINT_URL" in os.environ:
    env_to_propagate["mlflow_s3_endpoint_url"] = os.environ["MLFLOW_S3_ENDPOINT_URL"]
if "MLFLOW_S3_IGNORE_TLS" in os.environ:
    env_to_propagate["mlflow_s3_ignore_tls"] = os.environ["MLFLOW_S3_IGNORE_TLS"]

# Create a run for the pipeline
print ("Running Pipeline")
kfp_client.create_run_from_pipeline_func(
    mlflow_experiment_pipeline,
    experiment_name="ex2 - experiment",
    arguments={
        "git_url": "https://github.com/glroland/ml-pipeline-experiments.git",
        "env": env_to_propagate
    }
)

# Compile Pipeline
print ("Compiling Pipeline")
compiler.Compiler().compile(mlflow_experiment_pipeline, 'pipeline.yaml')
