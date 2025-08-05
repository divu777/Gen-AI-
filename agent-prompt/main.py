from dotenv import load_dotenv
import os
load_dotenv()
from openai import OpenAI

API_KEY = os.getenv('API_KEY')

client =  OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=API_KEY
)
messages = []

SYSTEM_PROMPT  = '''
    So you are intillegent Mathematician who is gonna just help user with maths doubt and question 

    You will break each question down into multiple steps which will include thinking excuting validiting , iterating over and over again 
    till you reach the final solution 

    Example:
    
    Input : 'What's 2+2/5*17?'

    Output: {{"step" : "thinking" , "content" :"Okh so user wants to find the solution for 2+2/5*17"}}
    Output: {{"step" : "executing" , "content" : "so lets start with applying BODMAS to this equation , so first lets solve 2/5 = 0.4 now lets multiply with 17, 17*0.4 = 6.8 and finally we add 2 making the final output , 6.8+2=8.8"  }}
    Output: {{"step" : "validating" , "content" : "okh so lets validate this , okh seems like yes this will be the answer"}}
    Output: {{"step" : "result" ,"content" : "the answer is 8.8"}}


    **IMPORTANT**
    Always give output in valid json, no markdown , no xml tags and no triple backslashes
'''

messages.append({'role':"system", "content":SYSTEM_PROMPT})

user = input('/')

messages.append({'role':"user","content":user})
import json
while True:
    completion = client.chat.completions.create(
    model='deepseek-ai/DeepSeek-V3:fireworks-ai',
    messages=messages,
    response_format= {"type":"json_object"}
    )

    print(completion.choices[0].message.content)

    response = json.loads(completion.choices[0].message.content)

    messages.append({"role":"assistant","content":completion.choices[0].message.content})

    if(response['step']=='result'):
        break


    



print(API_KEY)