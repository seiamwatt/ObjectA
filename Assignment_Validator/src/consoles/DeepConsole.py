import requests


def DeepSeek_Connect(api_key, prompt, model="deepseek-chat"):
    """
    Sends a prompt to DeepSeek API and returns the response.
    """
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

        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"DeepSeek API HTTP error: {e}")
        return None
    except requests.exceptions.ConnectionError:
        print("DeepSeek API connection error - check your internet")
        return None
    except Exception as e:
        print(f"DeepSeek API error: {e}")
        return None


def extract_response(result):
    """
    Extracts the text content from DeepSeek's API response.
    """
    if result and "choices" in result:
        return result["choices"][0]["message"]["content"]
    return None