import os

def get_files_info(working_directory, directory = None):
    abspath = os.path.abspath(working_directory)
    if type(directory) != str: #need to check if even is directory
        return f'Error: "{directory}" is not a directory'
    in_dir, path = in_directory(working_directory, directory)
    print(f"TUPLE {in_dir}")
    if not in_dir: 
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    return f"{directory}: file_size={os.path.getsize(path)} bytes, is_dir={os.path.isdir(path)}"
    
def in_directory(working_directory, directory):
    dir_list = os.listdir(working_directory)
    if directory in dir_list:
        return True, os.path.join(working_directory,directory)
    for dir in dir_list:
        if os.path.isdir(os.path.join(working_directory,dir)):
            return in_directory(os.path.join(working_directory,dir), directory)
    return False, ""
    