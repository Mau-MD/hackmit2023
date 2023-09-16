import os
import pickle
from dotenv import load_dotenv
import openai
from db import DB

embeddings_model = "text-embedding-ada-002"

def save_embeddings_to_file(embeddings, filename):
    with open(filename, 'wb') as f:
        pickle.dump(embeddings, f)

def load_embeddings_from_file(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

def get_embeddings(text):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input = [text], model=embeddings_model)['data'][0]['embedding']



def main():
    load_dotenv()
    openai.api_key = os.getenv("OPENAIKEY")
    db = DB()

    test_texts = ["I enjoy walking with my cute dog.", "I enjoy walking with my cute cat.", "I enjoy walking with my cute hamster."] 
    embeddings = load_embeddings_from_file('test-embeddings.pkl')
    
    for idx, embedding in enumerate(embeddings):
        db.execute_and_commit(f"INSERT INTO embeddings (lecture_id, text, vector) VALUES (1, '{test_texts[idx]}', '{db.convert_to_vector(embedding)}')")
    
    # query
    query_test = "I like cats"
    query_embedding = get_embeddings(query_test)

    best_match = db.get_match(query_embedding)
    print(best_match)

if __name__ == "__main__":
    main()