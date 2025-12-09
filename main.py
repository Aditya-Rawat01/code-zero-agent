from openai import Client
from dotenv import load_dotenv
import os
import json
from pydantic import BaseModel, Field, AfterValidator
from typing import Annotated, Optional, Callable
from components.tools import create_dir, list_files, change_dir, write_to_file, read_file

load_dotenv()

api_key = os.getenv("GROQ_API_KEY") 

client = Client(
    # base_url="https://generativelanguage.googleapis.com/v1beta/openai/",  for gemini
    base_url="https://api.groq.com/openai/v1",
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
    role: str = Field("assistant")
    stage:Annotated[str, AfterValidator(isStage)] = Field(..., description="tells about the current stage of the code completion process.")
    toolCall: Annotated[Optional[str], AfterValidator(isValidTool)] = Field(None, description="tells which tool is needed to be called.")
    params: Optional[str]= Field(None, description="tells tool params")
    description: str = Field(..., description = "tells about the description of the current step.")
    completed: bool = Field(False, description="tells if the ai has completed its process or not.")


REASONING_SYSTEM_PROMPT = """
You are CodeGenius Planner 1.0.
Your job is to think step-by-step and decide ONLY the next action.

DO NOT PRODUCE ANY JSON.

Output ONLY the following keys, as plain text:

nextStage: [plan | act | observe | reasoning | completed]
nextTool: (tool name or null)
toolParams: (a JSON object or null)
shouldComplete: (true/false)
description: (short explanation)

** all tools present are :
create_dir: Creates directory recursively. Requires 'path'.
write_to_file: Writes content to file ("required": ["filepath", "content", "mode"]),
read_file:Reads content from file.,
list_files:Lists files in current directory.,
change_dir:Changes current directory.

STRICT RULES:
- Output NOTHING except these fields.
- NEVER call multiple tools at once.
- NEVER skip stages.
- NEVER output JSON here.
"""

JSON_SYSTEM_PROMPT = """
Your job is to convert the given input string into STRICT JSON that matches the schema
provided by the client. You MUST obey the following rules:

1. Output EXACTLY one JSON object. No text before or after.
2. No comments. No explanations.
3. The output MUST validate against the provided schema:
   role, stage, toolCall, params, description, completed.
"""

def main():
    while True:
         messages = []
         print("🚀 Agent started (2-pass Groq-safe mode).")
         user_prompt = input("\n👉 ")
         messages = [{"role": "user", "content": user_prompt}]

         while True:

            reasoning_messages = [
                {"role": "system", "content": REASONING_SYSTEM_PROMPT},
                *messages
            ]
        
            try:
                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=reasoning_messages,
                )
            except Exception as e:
                print(f"API Error: {e}")
                break

            reasoning_text = response.choices[0].message.content
            print("\n🧠 REASONING:")
            print(reasoning_text)

            # Parse PASS 1 output
            parsed = {}
            for line in reasoning_text.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    parsed[key.strip()] = val.strip()

            nextStage = parsed.get("nextStage")
            nextTool = parsed.get("nextTool")
            description = parsed.get("description")
            shouldComplete = parsed.get("shouldComplete", "false").lower() == "true"
            toolParams = parsed.get("toolParams")

            if toolParams == "null":
                toolParams = None

            # -----------------------------------------
            # PASS 2 — JSON (Strict formatted output)
            # -----------------------------------------

            json_input = f"""
            nextStage: {nextStage}
            nextTool: {nextTool}
            toolParams: {toolParams}
            shouldComplete: {shouldComplete}
            description: {description}
            """

            json_messages = [
                {"role": "system", "content": JSON_SYSTEM_PROMPT},
                {"role": "user", "content": json_input}
            ]

            json_response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=json_messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "agent_step",
                        "schema": OutputFormat.model_json_schema()
                    }
                }
            )

            raw_json = json_response.choices[0].message.content
            print("\n📦 JSON OUTPUT:")
            print(raw_json)

            agent = OutputFormat.model_validate(json.loads(raw_json))
            messages.append({"role": "assistant", "content": raw_json})

            # -----------------------------------------
            # EXECUTE TOOL
            # -----------------------------------------

            if agent.completed:
                print("\n🎉 Task Completed!")
                break

            if agent.toolCall:
                tool_name = agent.toolCall
                params = json.loads(agent.params) if agent.params else {}

                print(f"\n🛠 Running tool: {tool_name} with {params}")
                result = availableTools[tool_name](**params)

                # feed observation
                messages.append({
                    "role": "user",
                    "content": f"Observation: {result}"
                })



if __name__ == "__main__":
    main()