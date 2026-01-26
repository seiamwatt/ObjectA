# Deep API - takes prompt and gives output to main business logic
import os
import csv
import json
import argparse
import pandas as pd
import requests
import re
import time
from tqdm import tqdm
from dotenv import load_dotenv
import PyPDF2
from pathlib import Path


# imported modules 
import Helper
my_helper = Helper.helper()

load_dotenv()


def parse_DeepSeek(api_key,prompt,other_notes,model = "deepseek-chat"):

    try:
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
            "max_tokens": 4000,
            "temperature": 0
        }

        response = requests.post(api_url,headers=headers,json=payload)
        response.raise_for_status()

        result = response.json()

        return result
    
    except Exception as e:

        print("error connecting DeepSeek")
        return None





















