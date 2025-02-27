import openai
from config import OPENAI_API_KEY, OPENAI_MODEL

# define API key
openai.api_key = OPENAI_API_KEY

def summarize_info(system_prompt: str, 
                   user_prompt: str) -> str:
    """
    Using OpenAI's ChatCompletion API, we summerize the information from various resources.
    """
    # construct the conversation for the API
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    response = openai.ChatCompletion.create( 
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=200
    ) # calling 
    
    final_text = response.choices[0].message["content"].strip() # generated text
    return final_text
