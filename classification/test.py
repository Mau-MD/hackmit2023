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

# def ask_gpt(context, qry):
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": """Imagine you are a very enthusiastic professor at a very prestigious university. You just gave a lecture,
#              and a student has a question for you. Answer in a helpful way, using content only from the lecture you just gave. If you don't know the answer,
#              do not invent things, simply say that you currently cannot help with the question, or that you don't know the answer.
#              The lecture you just gave is: """ + context + ". The question the student has is: " + qry + "."},
#             {"role": "user", "content": "Professor, I have a question about the lecture. My question is: " + qry},
#         ],
#         temperature=0.7
#     )

#     return response['choices'][0]['text']['message']['content']


def get_txt(source):
    from PyPDF2 import PdfReader

    reader = PdfReader(source)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    return text

import csv

def read_config():
    configs = []
    with open('config.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            configs.append(row)
    return configs

import requests

if __name__ == "__main__":
    configs = read_config()
    print(configs)

    for lec_name, lec_id, class_name, class_id, youtube_link, pdf_link in configs:
        print(lec_name, lec_id)
        response_text = get_txt(f'lecture_materials/{lec_name}.pdf')
        with open(f'lecture_converted/{lec_name}.txt', 'w') as file:
            file.write(response_text)    

            file.close()

    for lec_name, lec_id, class_name, class_id, youtube_link, pdf_link in configs:
        with open(f'lecture_converted/{lec_name}.txt', 'r') as file:
            contents = file.read().split()
            contents = ' '.join(contents)
            contents = re.split('\.|\!|\?', contents)

            file.close()
        
        # Add class
        base_url = "https://mau-md--embeddings-app.modal.run/add-class"
        params = {
            "class_name": class_name,
        }
        response = requests.post(base_url, json=params)
        class_id = response.text

        print(lec_name, class_id, youtube_link, pdf_link)

        # Add Lecture
        base_url = "https://mau-md--embeddings-app.modal.run/add-lecture"
        params = {
            "lecture_name": lec_name,
            "class_id": class_id,
            "youtube_link": youtube_link,
            "pdf_link": pdf_link
        }
        response = requests.post(base_url, json=params)
        lec_id = response.text

        i = 0
        sz = 15
        categories = {}
        chunk = []
        while i*sz < len(contents):

            base_url = "https://mau-md--embeddings-app.modal.run/add-context"

            params = {
                "lecture_id": lec_id,
                "query": ". ".join(contents[i*sz:(i+2)*sz])
            }

            # print(params)

            response = requests.post(base_url, json=params)
            print(response)

            i += 1