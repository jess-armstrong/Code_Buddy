import os
import subprocess
from google.genai import types

def run_python_file(working_directory, file_path, args=None):
    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

    if not abs_file_path.startswith(abs_working_dir):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(abs_file_path):
        return f'Error: File "{file_path}" not found'
    if not abs_file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file'
    try:
        commands = ["python", abs_file_path]
        if args:
            commands.extend(args)
        result = subprocess.run(
            commands, 
            timeout=30, 
            capture_output=True, 
            text=True,
            cwd=abs_working_dir
        )
        output = []
        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")

        if result.returncode != 0:
            output.append(f"Process exited with code {result.returncode}")

        return "\n".join(output) if output else "No output"
    except Exception as e:
        return f'Error executing python file: {e}'

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Run the specified python file, constrained to the working directory. Also returns output from the intrepreter",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file to execute, relative to working directory",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                    description="Optional arguments to pass to Python file"
                ),
                description="Optional arguments to pass to Python file"
            )
        },
        required=["file_path"],
    ),
)