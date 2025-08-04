import os
import subprocess
import kfp
import kfp.client
from kfp import dsl, components
from kfp.dsl import InputPath, Output, Artifact, Model
from kfp import compiler

ex1_pipeline = components.load_component_from_file('../ex1-mlflow_and_visual_pipeline/visual_pipeline.yaml')

ex2_pipeline = components.load_component_from_file('../ex2-mlflow_and_python_dsl_pipeline/pipeline.yaml')

@dsl.component
def store_assets():
    pass

@dsl.component
def register_models():
    pass

@dsl.pipeline(name="ex3 pipeline")
def train_model_pipeline(git_url: str, env: dict):

    ex1_pipeline()

    ex2_pipeline(git_url=git_url, env=env)

    # Store Assets
    store_assets_task = store_assets()
    store_assets_task.set_display_name("store-assets")
    store_assets_task.after(ex1_pipeline)
    store_assets_task.after(ex2_pipeline)

    # Register Models
    register_models_task = register_models()
    register_models_task.set_display_name("register-models")
    register_models_task.after(store_assets_task)


# Get OpenShift Token
token = subprocess.check_output("oc whoami -t", shell=True, text=True).strip()

# Connect to the pipeline server
print ("Connecting to pipeline server")
kfp_client = kfp.Client(host="https://ds-pipeline-dspa-pipeline-experiments.apps.ocp.home.glroland.com/",
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
    train_model_pipeline,
    experiment_name="ex3 - experiment",
    arguments={
        "git_url": "https://github.com/glroland/ml-pipeline-experiments.git",
        "env": env_to_propagate
    }
)

# Compile Pipeline
print ("Compiling Pipeline")
compiler.Compiler().compile(train_model_pipeline, 'pipeline.yaml')
