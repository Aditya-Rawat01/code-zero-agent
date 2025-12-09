from openai import Client
from dotenv import load_dotenv
import os
import json
from pydantic import BaseModel, Field, AfterValidator
from typing import Annotated, Optional, Callable
from components.tools import create_dir, list_files, change_dir, write_to_file, read_file

load_dotenv()

api_key = os.getenv("gemini_api_key") 

client = Client(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/", 
    api_key=api_key)


"""
complete the chat part, 
give the while true (chain of thought prompt engineering technique), 
give the pydantic schema for the strictness.


tools to be present here: ls, mkdir, touch

"""


availableTools:dict[str, Callable] = {
    "create_dir":create_dir,
    "write_to_file":write_to_file,
    "read_file":read_file,
    "list_files":list_files,
    "change_dir":change_dir
}
def isStage(val:str):
    stageFormat = ["plan","act","observe","reasoning","completed"]
    if not(val in stageFormat):
        raise ValueError(f"The stage is not in correct format of {stageFormat}")
    return val

def isValidTool(val:str|None):
    print("validity is being checked and found error rhere", val)
    if val is None:
        return val
    if not(val in availableTools):
        raise ValueError(f"The tool is not present in the {availableTools}")
    return val

class OutputFormat(BaseModel):
    stage:Annotated[str, AfterValidator(isStage)] = Field(..., description="tells about the current stage of the code completion process.")
    toolCall: Annotated[Optional[str], AfterValidator(isValidTool)] = Field(None, description="tells which tool is needed to be called.")
    params: Optional[str]= Field(None, description="tells tool params")
    description: str = Field(..., description = "tells about the description of the current step.")
    completed: bool = Field(False, description="tells if the ai has completed its process or not.")


SYSTEM_PROMPT = SYSTEM_PROMPT = """
# SYSTEM INSTRUCTION: Code Agent Profile (CodeGenius Agent 5.0)

## 1. Role and Core Mandate
You are **CodeGenius Agent 5.0**, a specialized, Level 5 Agentic Software Engineer. Your sole, non-negotiable function is to assist with professional software development tasks using a strictly structured workflow.

## 2. Available Tools
You have access to the following file system tools. You must use these to perform actions:
1. **create_dir**: Creates a new directory.
   - Params: `{"path": "string"}` (e.g., "src/components")

2. **write_to_file**: Writes content to a file.
   - Params: `{"filepath": "string", "content": "string", "mode": "w"}` 
   - Note: `mode` is strictly required. Use "w" for overwrite, "a" for append.

3. **list_files**: Lists files in the current directory.
   - Params: `{}` (Empty JSON object)

4. **change_dir**: Changes the working directory.
   - Params: `{"path": "string"}`

4. **read_file**: reads from the file.
   - Params: `{"filepath": "string"}`
   
## 3. Interaction Protocol (Strict JSON Schema)
You do NOT write standard text or Markdown responses. You interact **only** by filling the following structured fields:

* **stage**: Must be one of `["plan", "act", "reasoning"]`.
* **toolCall**: The exact name of the tool to call (e.g., "create_dir") or `null` if no tool is needed.
* **params**: A valid JSON string representing the arguments for the tool (e.g., '{"path": "src"}' ). Set to `null` if no tool is called.
* **description**: Your thought process, plan details, or reasoning explanation.
* **completed**: Set to `true` ONLY when the entire user request is fully resolved.

## 4. Mandatory Agentic Workflow
You must loop through these stages until the task is done:

### STAGE 1: 'plan'
* **Action:** Set `stage` to "plan".
* **Content:** In the `description` field, outline your step-by-step strategy, target language/framework, and design patterns. Do NOT call tools here.

### STAGE 2: 'act'
* **Action:** Set `stage` to "act".
* **Content:** Set `toolCall` to the required tool name and `params` to the JSON string of arguments. Keep `description` brief (e.g., "Creating the project directory").

### STAGE 3: 'observe'
* **Action:** None, you will receive the observe stage as the result of the tool call".
* **Content:** In the `description` field, observe the result of the tool call.

### STAGE 4: 'reasoning'
* **Action:** Set `stage` to "reasoning".
* **Content:** In the `description` field, analyze the result of the tool call (which you will receive in the next turn) or explain why the code implementation satisfies the plan.

### STAGE 5: 'completed'
* **Action:** Set `stage` to "completed" and nothing else.
* **Content:** In the `description` field, summarize if you have completed the assigned task.


## 5. Constraints
* **Strictly Technical:** If the user asks a non-coding question, set `completed=True` and put the refusal message in `description`.
* **No Markdown Headers:** Do not put "### Stage 1" in your output. The `stage` field handles this.
"""
def main():
    while True:
        messages:list=[
            
            {"role": "system", "content": SYSTEM_PROMPT},
        ]
        user_prompt = input("👉 ")
        messages.append({"role":"user", "content": user_prompt})


        while True:
            try:
                response = client.chat.completions.parse(
                    model="gemini-2.5-flash",
                    messages=messages,
                    response_format=OutputFormat
                )
            except Exception as e:
                print(f"API Error: {e}")
                break

            agentResponse = response.choices[0].message
            parsed_content = agentResponse.parsed
            
            # Print the description to the console so we see what's happening
            print(f"🤖 [{parsed_content.stage}]: {parsed_content.description}")

            # IMPORTANT: Append the Assistant's JSON response to history
            # We must use the raw content (string) so the API knows what was said
            messages.append(agentResponse) 

            # Check for completion
            if parsed_content.completed:
                print("✅ Task Completed.")
                break

            # Check for Tool Execution
            if parsed_content.toolCall:
                fn_name = parsed_content.toolCall
                params_str = parsed_content.params
                
                print(f"   🛠️ Executing: {fn_name} with {params_str}")

                if params_str is None:
                    args = {}
                else:
                    try:
                        args = json.loads(params_str)
                    except json.JSONDecodeError as e:
                        result = f"Error parsing params JSON string: {e}"
                        args = None

                if args is not None:
                    try:
                        fnSignature = availableTools[fn_name]
                        result = fnSignature(**args)
                    except Exception as e:
                        result = f"Error executing tool: {e}"
                
                # FIX IS HERE: 
                # Use role="user" to represent the "Observation"
                # Do NOT use role="tool" unless using native function calling
                tool_observation_msg = {
                    "role": "user", 
                    "content": f"Observation from {fn_name}: {result}"
                }
                
                messages.append(tool_observation_msg)



if __name__ == "__main__":
    main()