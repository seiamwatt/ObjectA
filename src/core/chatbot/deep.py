# DEEP API 

import os 
import requests
import json 
import re 
from dotenv import load_dotenv

load_dotenv()


def create_prompt(prompt): 

    prompt_output = " "



    return prompt_output


def parse_txt_to_deepseek(api_key,prompt_content,model = "deepseek-chat",max_retries = 5,base_delay = 1):

    if not prompt_content or not prompt_content.strip():
        return None
    
    prompt = create_prompt(prompt_content)


    for attempt in range(max_retries):
          api_url = "https://api.deepseek.com/v1/chat/completions"
          headers = {
               "Content-Type": "application/json",
               "Authorization": f"Bearer {api_key}"
          } 


          payload = {
               "model": model,
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "max_tokens": 8000,
    "temperature": 0
          }

          response = requests.post(api_url,headers=headers,json=payload)





       

       

        


