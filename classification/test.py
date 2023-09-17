import openai
import os
import re
from dotenv import load_dotenv
from multiprocessing import Process

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# def get_summary(text):
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant"},
#             {"role": "user", "content": "I will give you a few sentences and you will return a small summary for those sentences"},
#             {"role": "assistant", "content": "How should I give you an output?"},
#             {"role": "user", "content": "As a string of text, without any headers, just the summary. Again, no headers, just the summary."},
#             {"role": "assistant", "content": "Got it. So, I will give you a string of text."},
#             {"role": "user", "content": "Yes. Now, this is the text: " + text}
#         ],
#         temperature=0.2
#     )

#     return {str(response['choices'][0]['message']['content']): str(text)}

def ask_gpt(context, qry):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": """Imagine you are a very enthusiastic professor at a very prestigious university. You just gave a lecture,
             and a student has a question for you. Answer in a helpful way, using content only from the lecture you just gave. If you don't know the answer,
             do not invent things, simply say that you currently cannot help with the question, or that you don't know the answer.
             The lecture you just gave is: """ + context + ". The question the student has is: " + qry + "."},
            {"role": "user", "content": "Professor, I have a question about the lecture. My question is: " + qry},
        ],
        temperature=0.7
    )

    return response['choices'][0]['text']['message']['content']

if __name__ == "__main__":
    with open('16.842 transcr.txt', 'r') as file:
        contents = file.read().split()
        contents = ' '.join(contents)
        contents = re.split('\.|\!|\?', contents)

        file.close()

    i = 0
    sz = 10
    categories = {}
    chunk = []
    while i*sz < len(contents):
        import requests

        base_url = "http://your-api-url.com"

        params = {
            "lecture_id": 1,
            "query": contents[i*sz:(i+1)*sz]
        }

        response = requests.post(base_url, params=params)

        i += sz - 2