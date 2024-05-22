import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_ai_response(prompt, chat_history=None):
    if chat_history is None:
        chat_history = []

    messages = [{"role": "system", "content": "You are a helpful and informative AI assistant."}] + chat_history + [{"role": "user", "content": prompt}]

    response = openai.ChatCompletion.create(
        model="text-davinci-003",  # Use a less expensive model
        messages=messages,
        temperature=0.7,
        max_tokens=150,  # Adjust as needed
    )

    message = response.choices[0].message['content'].strip()
    return message
