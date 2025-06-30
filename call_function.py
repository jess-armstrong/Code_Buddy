from google.genai import types

from functions.get_files_info import get_files_info, schema_get_files_info
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.write_file import write_file, schema_write_file
from functions.run_python_file import run_python_file, schema_run_python_file
from config import WORKING_DIR

available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_write_file,
            schema_run_python_file
        ]
    )

def call_function(function_call_part, verbose = False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f"Calling function: {function_call_part.name}")

    function_dict = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "write_file" : write_file,
        "run_python_file" : run_python_file,
    }

    func_name = function_call_part.name
    if func_name not in function_dict:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name = func_name,
                    response={"error": f"Unknown function: {func_name}"},
                )
            ]
        )
    
    args = dict(function_call_part.args)
    args["working_directory"] = WORKING_DIR
    func_result = function_dict[func_name](**args)
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
            name = func_name,
            response={"result": func_result},
        )
    ],
)
    