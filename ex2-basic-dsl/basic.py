import subprocess
import kfp
import kfp.client
from kfp import dsl
from kfp import compiler


@dsl.component
def step_1(input_name: str, input_age: int) -> str:
    import os
    print("Step #1")
    print("Name:", input_name)
    print("Age:", input_age)
    print(os.environ)

    if input_age < 18:
        return "MINOR"
    else:
        return "ADULT"


@dsl.component
def step_2(input_name: str, age_category: str) -> str:
    import os
    print("Step #2")
    print("Name:", input_name)
    print("Age Category:", age_category)
    greeting = f"Thank you for representing {age_category}s, {input_name}!"
    print(greeting)
    print(os.environ)
    return greeting


@dsl.component
def step_3(greeting: str):
    import os
    print("Step #3")
    print("Greeting:", greeting)
    print(os.environ)


@dsl.pipeline(name="ex2 simple python dsl pipeline")
def simple_dsl_pipeline(input_name: str, input_age: int):
    # Step 1
    step_1_task = step_1(input_name=input_name, input_age=input_age)

    # Step 2
    step_2_task = step_2(input_name=input_name, age_category=step_1_task.output)

    # Step 3
    step_3_task = step_3(greeting=step_2_task.output)


# Connect to the pipeline server
print("Connecting to pipeline server")
token = subprocess.check_output("oc whoami -t", shell=True, text=True).strip()
kfp_client = kfp.Client(host="https://ds-pipeline-dspa-pipeline-sandbox.apps.ocp.home.glroland.com/",
                        existing_token=token,
                        verify_ssl=False)

# Create a run for the pipeline
print("Running Pipeline")
kfp_client.create_run_from_pipeline_func(
    simple_dsl_pipeline,
    experiment_name="ex2 basic pipeline experiment",
    arguments={
        "input_name": "Jimmy John",
        "input_age": 28
    }
)

# Compile Pipeline
print("Compiling Pipeline")
compiler.Compiler().compile(simple_dsl_pipeline, 'basic.yaml')
