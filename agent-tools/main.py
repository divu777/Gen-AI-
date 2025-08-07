from dotenv import load_dotenv
import os
from openai import OpenAI
import json

load_dotenv()

API_KEY = os.getenv('API_KEY')


client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=API_KEY
)


SYSTEM_PROMPT = '''
#GOAL
You are a smart assistant agent that helps user with weather related data and commands that could 
be run on the user terminal

#INSTRUCTIONS
1) Analayse the user query and examine it fully before breaking it down into smaller steps
2) Start with the thinking step that how can i solve this problem in the best way possible 
3) Use the given set of tools to call them whenever needed , but make sure if you don't have enough context or information you can ask user

#TOOLS
1) get_weather - function that can be used to get the current weather of that city
    - Input: city_name
2) run_commands - function that can be called to pass linux commands in user terminal directly
    - Input: command

#Output JSON Format:
{{
    "step": "string",
    "content": "string",
    "function": "The name of function if the step is action",
    "input": "The input parameter for the function",
}}

#EXAMPLE

Input: What is the weather of the city faridabad and write it in file name weather.txt?

Output: {{"step":"think","content":"So to find the weather of the city of faridabad right now i have to first call the function that gets the weather , get_weather and observe the output and then write command to first make file and then write into the file using linux command"}}
Output: {{"step":"function_call","function":"get_weather","input":"faridabad"}}
Output: {{"step":"observe","output":"28 degree"}}
Output: {{"step":"function_call","content":"run_commands","input":"touch weather.txt && echo "Weather in faridabad is 28 degree" > weather.txt}}
Output: {{"step":"final","content":"the weather of faridabad is 29 degree right now and i have also written it in the file you asked"}}

**IMPORTANT**
Always give output in valid json, no markdown , no xml tags and no triple backslashes
'''

messages=[{"role":"system","content":SYSTEM_PROMPT}]

import requests
def get_weather(city: str):
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    
    return "Something went wrong"


def run_commands(arg):
    return os.system(arg)

function = {
    "get_weather":get_weather,
    "run_commands":run_commands
}




while True:
    query = input("--->");
    messages.append({"role":"user","content":query})



    while True:
        completion = client.chat.completions.create(
        model='deepseek-ai/DeepSeek-V3:fireworks-ai',
        messages=messages,
        response_format = {"type":"json_object"}
        )
        print(completion.choices[0].message.content)
        
        output = json.loads(completion.choices[0].message.content)
        messages.append({"role":"assistant","content":completion.choices[0].message.content})


        if(output["step"]=="function_call"):
           response =  function[output["function"]](output["input"])
           observe_msg = json.dumps({"step":"observe","output": response})

           messages.append({"role":"assistant","content": observe_msg})

            

        if(output["step"]=="final"):
            break



