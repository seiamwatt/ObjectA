# base script to connect to DeepSeek and Claude 
# this script gets texts or data from CSV file and evalauate 
# how the script outputs its data needs to be changed depending on project// can be change at batch_processing func
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




#Open csv File
def load_csv(file_path):
    
    try:
        file = pd.read_csv(file_path,encoding = "utf-8")
        return file
    
    except Exception as e:
        return None
    
# Open txt file

def open_txt(file_path):

    try:
        with open(file_path,'r') as file:
            content = file.read()
            return content
    except Exception as e:
        return None



# Get Prompt

def create_prompt(other_notes):
    prompt =" "


    return prompt + other_notes

# connect to DeepSeek 

def DeepSeek_Connect(api_key,prompt,other_notes,model='deepseek-chat'):

    prompt = create_prompt(prompt,other_notes=other_notes)

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
        print("Error calling DeepSeek API")
        return None
    

# connect to Claude 

def Claude_Connect(api_key,prompt,other_notes,model = 'claude-sonnet-4-5-20250929'):
    
    prompt = create_prompt(prompt,other_notes=other_notes)

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

        response = requests.post(api_url,headers=headers,json=payload)
        response.raise_for_status()

        result = response.json()
        return result

    except Exception as e:
        print("Error calling Claude API")
        return None
    
def batch_processing(api_key, df_batch, output_file, llm_model, other_notes):
    results = []  # initialize results list

    for _, row in tqdm(df_batch.iterrows(), total=len(df_batch)):  # loop over rows
        prompt = row.get('text', '')  # adjust column name as needed
        
        if llm_model == "Claude":
            response = Claude_Connect(api_key, prompt, other_notes)
            if response:
                content = response.get('content', [{}])[0].get('text', '')
            else:
                content = ''
        else:
            response = DeepSeek_Connect(api_key, prompt, other_notes)
            if response:
                content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            else:
                content = ''

        results.append({
            'input': prompt,
            'output': content
        })

    # Write to CSV without overwriting
    fields = ['input', 'output']
    write_header = not os.path.exists(output_file) or os.path.getsize(output_file) == 0

    with open(output_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if write_header:
            writer.writeheader()
        writer.writerows(results)

    return len(results)




# Terminal command examples:
#
# For Claude:
# python3 script.py --input data.csv --output results.csv --LLM_model Claude --api_key your_api_key
#
# For DeepSeek:
# python3 script.py --input data.csv --output results.csv --LLM_model DeepSeek --api_key your_api_key
#
# With optional parameters:
# python3 script.py --input data.csv --output results.csv --LLM_model Claude --batch_size 25 --start_row 0 --end_row 100 --other_notes "additional instructions"
#
# Using environment variables for API key:
# export ANTHROPIC_API_KEY=your_key   (for Claude)
# export DEEPSEEK_API_KEY=your_key    (for DeepSeek)
# python3 script.py --input data.csv --output results.csv --LLM_model Claude
#Console settings
def main():
    parser = argparse.ArgumentParser(description="Claude/DeepSeek console")
    parser.add_argument("--input", type=str, required=True, help='input file path')
    parser.add_argument("--output", type=str, required=True, help='output file path')
    parser.add_argument("--batch_size", type=int, default=50, help='num rows for batch')
    parser.add_argument("--start_row", type=int, default=0, help='start row')
    parser.add_argument("--end_row", type=int, default=None, help='end row, row indexing provided')     
    parser.add_argument("--api_key", type=str, help='API key in env')
    parser.add_argument("--LLM_model", type=str, help='choose between DeepSeek and Claude')
    parser.add_argument("--other_notes", type=str, default="", help='additional notes for prompt')

    args = parser.parse_args()

    api_key = args.api_key or os.getenv('ANTHROPIC_API_KEY') or os.getenv('DEEPSEEK_API_KEY')

    if not api_key:
        print("API key not found")
        return

    df = load_csv(args.input)

    if df is None:
        print("Failed to load CSV")
        return

    start_row = args.start_row
    end_row = args.end_row if args.end_row is not None else len(df)
    df_to_process = df.iloc[start_row:end_row].copy()

    print(f"Processing rows {start_row} to {end_row - 1} ({len(df_to_process)} rows total)")

    # Process in batches
    total_processed = 0
    for i in range(0, len(df_to_process), args.batch_size):
        batch_end = min(i + args.batch_size, len(df_to_process))
        batch = df_to_process.iloc[i:batch_end]

        print(f"Processing batch: rows {i + start_row} to {batch_end + start_row - 1}")
        processed = batch_processing(api_key, batch, args.output, args.LLM_model, args.other_notes)
        total_processed += processed

    print(f"Done. Total processed: {total_processed}")


if __name__ == "__main__":
    main()




