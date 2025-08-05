import subprocess
import kfp
import kfp.client
from kfp import dsl
from kfp import compiler


PIPELINE_NAME = "ex2-basic-dsl pythagorean"


@dsl.component
def square(x: float) -> float:
    return x ** 2


@dsl.component
def add(x: float, y: float) -> float:
    return x + y


@dsl.component
def square_root(x: float) -> float:
    return x ** .5


@dsl.pipeline(name=PIPELINE_NAME)
def pythagorean(a: float, b: float) -> float:
    a_sq_task = square(x=a)
    b_sq_task = square(x=b)
    sum_task = add(x=a_sq_task.output, y=b_sq_task.output)
    return square_root(x=sum_task.output).output



# Connect to the pipeline server
print("Connecting to pipeline server")
token = subprocess.check_output("oc whoami -t", shell=True, text=True).strip()
kfp_client = kfp.Client(host="https://ds-pipeline-dspa-pipeline-sandbox.apps.ocp.home.glroland.com/",
                        existing_token=token,
                        verify_ssl=False)

# Create a run for the pipeline
print("Running Pipeline")
kfp_client.create_run_from_pipeline_func(
    pythagorean,
    experiment_name=PIPELINE_NAME,
    arguments={
        "a": 10,
        "b": 4
    }
)

# Compile Pipeline
print("Compiling Pipeline")
compiler.Compiler().compile(pythagorean, 'pythagorean.yaml')
