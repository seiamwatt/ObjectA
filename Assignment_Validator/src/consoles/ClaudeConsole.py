# Claude API - takes prompt and gives output to main business logic
import os
import csv
import json
import argparse
import pandas as pd
import requests
import re
from tqdm import tqdm
from dotenv import load_dotenv
import anthropic
import requests

# import helper function
from Helper import Helper

helper = Helper()


# REST API


def Claude_Connect(api_key,prompt,other_notes,model = 'claude-sonnet-4-5-20250929'):

    try:
        api_url = "https://api.anthropic.com/v1/messages"

        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,                # not "Authorization: Bearer"
            "anthropic-version": "2023-06-01"    # required
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4000,
            "temperature": 0
        }

        response = requests.post(api_url,headers = headers,json = payload)
        response.raise_for_status()

        result = response.json()
        return result
 
    except Exception as e:
        print("Error calling Claude API")
        return None
    
    





