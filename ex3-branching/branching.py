import subprocess
import kfp
import kfp.client
from kfp import dsl
from kfp import compiler


@dsl.component
def is_number(input_str: str) -> bool:
    print("Is Number Step")
    print("Input:", input_str)

    if input_str is None or len(input_str) == 0:
        return False
    return input_str.isnumeric()


@dsl.component
def is_even(input_str: str) -> bool:
    print("Is Even Step")
    print("Input:", input_str)

    input_num = int(input_str)
    return input_num % 2 == 0


@dsl.component
def print_input(input_str: str):
    print("Print Input Step")
    print("Input:", input_str)


@dsl.pipeline(name="ex3 branching pipeline")
def branching_pipeline(input_str: str):
    # Step 1
    is_number_task = is_number(input_str=input_str)

    # Handle Non-Numeric Input
    with dsl.If(is_number_task.output==False, 'is_number_condition'):
        print_input(input_str=f"{input_str} is NOT A NUMBER!")

    with dsl.Else():
        is_even_task = is_even(input_str=input_str)

        with dsl.If(is_even_task.output==True, 'is_even_condition'):
            print_input(input_str=f"{input_str} is EVEN")

        with dsl.Else():
            print_input(input_str=f"{input_str} is ODD")


# Connect to the pipeline server
print("Connecting to pipeline server")
token = subprocess.check_output("oc whoami -t", shell=True, text=True).strip()
kfp_client = kfp.Client(host="https://ds-pipeline-dspa-pipeline-sandbox.apps.ocp.home.glroland.com/",
                        existing_token=token,
                        verify_ssl=False)

# Create a run for the pipeline
print("Running Pipeline")
kfp_client.create_run_from_pipeline_func(
    branching_pipeline,
    experiment_name="ex3 branching pipeline experiment",
    arguments={
        "input_str": "Not a Number"
    }
)

# Create a run for the pipeline
print("Running Pipeline")
kfp_client.create_run_from_pipeline_func(
    branching_pipeline,
    experiment_name="ex3 branching pipeline experiment",
    arguments={
        "input_str": "10"
    }
)

# Create a run for the pipeline
print("Running Pipeline")
kfp_client.create_run_from_pipeline_func(
    branching_pipeline,
    experiment_name="ex3 branching pipeline experiment",
    arguments={
        "input_str": "103"
    }
)

# Compile Pipeline
print("Compiling Pipeline")
compiler.Compiler().compile(branching_pipeline, 'basic.yaml')
