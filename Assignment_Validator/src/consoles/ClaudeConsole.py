# Claude API - takes prompt and gives output to main business logic
import requests


def Claude_Connect(api_key, prompt, model="claude-sonnet-4-5-20250929"):
    """
    Sends a prompt to Claude API and returns the response.
    
    Args:
        api_key: Anthropic API key
        prompt: The text prompt to send
        model: Model to use (default: claude-sonnet-4-5-20250929)
    
    Returns:
        dict: Full API response JSON, or None if error
    """
    try:
        api_url = "https://api.anthropic.com/v1/messages"

        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
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
        print(f"Claude API HTTP error: {e}")
        return None
    except requests.exceptions.ConnectionError:
        print("Claude API connection error - check your internet")
        return None
    except Exception as e:
        print(f"Claude API error: {e}")
        return None


def extract_response(result):
    """
    Extracts the text content from Claude's API response.
    
    Args:
        result: The JSON response from Claude_Connect()
    
    Returns:
        str: The text response, or None if error
    """
    if result and "content" in result:
        return result["content"][0]["text"]
    return None