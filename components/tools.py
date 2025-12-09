import os

def create_dir(path:str)->str:
    try:
        os.makedirs(path, exist_ok=True) # can create nested directories like project/src/components/main.js in one command
        return f"{path} directory has been created successfully"

    except Exception as e:
        return f"Error faced: {e}"

def list_files()->str:
    try:
        result = os.listdir()
        return f"{result} are the list of the files present here."
    except Exception as e:
        return f"Error faced: {e}"

def change_dir(path:str)->str:
    try:
        os.chdir(path)
        return f"current working directory is {os.getcwd()}"
    except Exception as e:
        return f"Error faced: {e}"

def read_file(filepath:str)->str:
    try:
        with open(filepath, "r") as f:
            content = f.read()
            return content
    except Exception as e:
        return f"Error faced: {e}"

    


def write_to_file(filepath, content , mode='w')->str:
    try:
        with open(file=filepath, mode=mode) as f:
            f.write(content + "\n")
            return f"{content} has been written successfully"

    except Exception as e:
        return f"Error faced: {e}"
    



toolsDefinition:list= [
    {
        "type": "function",
        "function": {
            "name": "createDir", # Ensure this matches your dict key if you use it for lookup
            "description": "Creates directory recursively. Requires 'path'.",
            "strict": True, # <--- REQUIRED FOR PARSE()
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to create (e.g., 'src/components')."
                    }
                },
                "required": ["path"], # <--- ALL params must be here
                "additionalProperties": False # <--- REQUIRED FOR PARSE()
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Lists files in current directory.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "change_dir",
            "description": "Changes current directory.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Destination path."
                    }
                },
                "required": ["path"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_to_file",
            "description": "Writes content to file.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file."
                    },
                    "content": {
                        "type": "string",
                        "description": "File content."
                    },
                    "mode": {
                        "type": "string",
                        "description": "Mode: 'w' for write, 'a' for append."
                    }
                },
                "required": ["filepath", "content", "mode"], # <--- 'mode' must be required now
                "additionalProperties": False
            }
        }
    }, {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads content from file.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file."
                    },
                },
                "required": ["filepath"],
                "additionalProperties": False
            }
        }
    }
]