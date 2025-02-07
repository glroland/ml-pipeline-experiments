import subprocess
import kfp
import kfp.client
from kfp import dsl
from kfp.dsl import InputPath, Output, Artifact, Model, ClassificationMetrics
from kfp import compiler

@dsl.component(base_image="quay.io/modh/runtime-images:runtime-pytorch-ubi9-python-3.11-20250130",
               packages_to_install=["papermill", "GitPython", "ipykernel", "jupyter", "nbconvert"])
def run_notebook_in_proc(git_url: str,
                         run_from_dir: str,
                         notebook_name: str,
                         parameters: dict,
                         env: dict,
                         jupyter_nb_output: Output[Artifact],
                         model: Output[Model],
                         metrics: Output[ClassificationMetrics]):
    # setup output directories
    import os
    temp_path = "/tmp"
    temp_repo_path = os.path.join(temp_path, "repo")
    temp_nb_output_dir = os.path.join(temp_path, "nb_output")
    temp_nb_py_script = os.path.join(temp_path, "nb_output_as.py")

    # clone git repo
    print (f"Cloning Git Repo.  URL={git_url} TempRepoPath={temp_repo_path}")
    from git import Repo
    Repo.clone_from(git_url,temp_repo_path)

    # build parameter list
    primary_parameter_list = dict(onnx_path = model.path,
                                  output_dir = temp_nb_output_dir)
    primary_parameter_list.update(parameters)
    primary_parameter_list.update(env)
    print (f"Parameters: {primary_parameter_list}")

    # change run directory
    new_dir = os.path.join(temp_repo_path, run_from_dir)
    print (f"Changing directory to: {new_dir}")
    os.chdir(new_dir)

    # append environment variables
    for key, value in env.items():
        os.environ[key] = value

    # apply parameters to notebook
    print (f"Applying parameters .  Filename={notebook_name}")
    import papermill as pm
    pm.execute_notebook(
        notebook_name,
        jupyter_nb_output.path,
        parameters=primary_parameter_list,
        kernel_name="",
        prepare_only=True
    )

    # convert notebook to python file
    import nbconvert
    exporter = nbconvert.PythonExporter()
    (body, resources) = exporter.from_filename(jupyter_nb_output.path)
#    with open(temp_nb_py_script, 'w') as f:
#        f.write(body)

    # execute notebook
    import sys
    sys.path.append(new_dir)
    exec(body, {"metrics_output": metrics})

# Compile Component
print ("Compiling Component")
compiler.Compiler().compile(run_notebook_in_proc, 'run-notebook-in-proc-component.yaml')
