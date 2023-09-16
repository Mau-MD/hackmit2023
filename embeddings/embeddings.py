

class Embeddings:
    embeddings_model = "text-embedding-ada-002"

    def __init__(self):
        load_dotenv()
        openai.api_key = os.getenv("OPENAIKEY")
        self.db = DB()

    def get_context(self, query):
        embedding = self._get_embedding(query)
        return self._get_embedding_best_match(embedding)

    def add_context(self, query, lecture_id):
        embedding = self._get_embedding(query)
        self._save_embeddings_to_db(lecture_id, query, embedding)

    def _get_embedding(self, text):
        text = text.replace("\n", " ")
        return openai.Embedding.create(input = [text], model=self.embeddings_model)['data'][0]['embedding']

    def _save_embeddings_to_file(self, embeddings, filename):
        with open(filename, 'wb') as f:
            pickle.dump(embeddings, f)
    
    def _load_embeddings_from_file(self, filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)

    def _save_embeddings_to_db(self, lecture_id, text, embedding):
        self.db.execute_and_commit(f"INSERT INTO embeddings (lecture_id, text, vector) VALUES ({lecture_id}, '{text}', '{self.db.convert_to_vector(embedding)}')")
    
    def _get_embedding_best_match(self, embedding):
        return self.db.get_match(embedding)

        
# def main():
#     load_dotenv()
#     openai.api_key = os.getenv("OPENAIKEY")
#     db = DB()

#     test_texts = ["I enjoy walking with my cute dog.", "I enjoy walking with my cute cat.", "I enjoy walking with my cute hamster."] 
#     embeddings = load_embeddings_from_file('test-embeddings.pkl')
    
#     for idx, embedding in enumerate(embeddings):
#         db.execute_and_commit(f"INSERT INTO embeddings (lecture_id, text, vector) VALUES (1, '{test_texts[idx]}', '{db.convert_to_vector(embedding)}')")
    
#     # query
#     query_test = "I like cats"
#     query_embedding = get_embedding(query_test)

#     best_match = db.get_match(query_embedding)
#     print(best_match)

# if __name__ == "__main__":
#     main()