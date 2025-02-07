# Examples for Running MLFlow Pipelines in OpenShift Pipelines

## Setup Instructions

From the OpenShift AI environment in which you would like to run these examples:

1. Create a project where you would like to run these tests.  i.e. MLFlow
2. Create a data connection for pipeline assets in the project.
3. Create a pipeline server in the project that uses the previously created data connection.
4. Once the pipeline server is created, create a workbench of the type "Standard Data Science".
5. Open the workbench
6. Checkout this git repository
7. Create a terminal within the workbench
8. Change to the git rep folder (cd directory_name)
9. pip install -r requirements.txt
10. Set the following environment variables (in context within the terminal is fine):
 - export AWS_ACCESS_KEY_ID = your_access_key
 - export AWS_SECRET_ACCESS_KEY = your_secret_key
 - export AWS_DEFAULT_REGION = your_region
 - export MLFLOW_S3_ENDPOINT_URL = your_s3_endpoint_for_mlflow
 - export MLFLOW_S3_IGNORE_TLS = true_or_false

## Run Each Test

### Example 1

In the workbench GUI:

1. Change to the ex1-mlflow_and_visual_pipeline directory.
2. Open the visual_pipeline.pipeline file.
3. Click on the single node in the diagram.
4. Change the environment variables to your own S3 connections.
5. Click the run button.
6. Open the link to observe the status of the run.
7. Back in the workbench, for use in example 3, export the pipeline to YAML using default settings and choose to overwrite.

### Example 2

In the workbench GUI:

1. Change to the ex2-mlflow_and_python_dsl_pipeline directory.
2. Open pipeline.py
3. Change the pipeline server URL and save.
4. Go back to the terminal that was created in the setup instructions.
5. Change to the ex2-mlflow_and_python_dsl_pipeline directory.
6. python pipeline.py
7. Go to the experiments UI in the OpenShift AI UI and view the status of the running pipeline.

### Example 3

In the workbench GUI:

1. Change to the ex3-extended_python_dsl_pipeline directory.
2. Open pipeline.py
3. Change the pipeline server URL and save.
4. Go back to the terminal that was created in the setup instructions.
5. Change to the ex3-extended_python_dsl_pipeline directory.
6. python pipeline.py
7. Go to the experiments UI in the OpenShift AI UI and view the status of the running pipeline.
