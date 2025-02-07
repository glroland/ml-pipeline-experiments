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
def train_model_pipeline(git_url: str, db_conn_str: str):

    ex1_pipeline()

    ex2_pipeline(git_url=git_url)

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
kfp_client = kfp.Client(host="https://ds-pipeline-dspa-baseball.apps.ocp.home.glroland.com/",
                        existing_token=token,
                        verify_ssl=False)

# Create a run for the pipeline
print ("Running Pipeline")
kfp_client.create_run_from_pipeline_func(
    train_model_pipeline,
    experiment_name="v3 - experiment",
    arguments={
        "git_url": "https://github.com/glroland/ml-pipeline-experiments.git"
    }
)

# Compile Pipeline
print ("Compiling Pipeline")
compiler.Compiler().compile(train_model_pipeline, 'pipeline.yaml')
