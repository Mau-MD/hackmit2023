import modal
from modal import Stub, Image, wsgi_app, Secret


stub = Stub("embeddings")
image = Image.debian_slim().apt_install("libpq-dev").pip_install("flask", "openai", "python-dotenv", "psycopg2")


@stub.function(image=image, secret=modal.Secret.from_name("OPENAIKEY"))
@wsgi_app()
def app():
    from flask import Flask
    import os
    import pickle
    import openai
    import psycopg2



    # Embeddings
    class Embeddings:
        embeddings_model = "text-embedding-ada-002"

        def __init__(self):
            openai.api_key = os.environ["OPENAIKEY"]
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
        
    class DB:
        # constructor
        def __init__(self):
            self.conn = psycopg2.connect(database="opentutor",
                            host="localhost",
                            user="postgres",
                            password="postgres",
                            port="65431")
            self.cursor = self.conn.cursor()
            self.execute_and_commit("SET enable_seqscan = off;")
        
        def execute_and_fetch(self, query):
            self.cursor.execute(query)
            return self.cursor.fetchall()

        
        def execute_and_commit(self, query):
            self.cursor.execute(query)
            self.conn.commit()
        
        def convert_to_vector(self,embedding):
            return "{" + ",".join([str(x) for x in embedding]) + "}"

        def get_match(self, query_embedding, n = 3):
            # vector = self.convert_to_vector(query_embedding)
            query = f"SELECT lecture_id, text, l2sq_dist(vector, ARRAY{query_embedding}) AS dist FROM embeddings ORDER BY vector <-> ARRAY{query_embedding} LIMIT {n};"
            return self.execute_and_fetch(query)


        def __del__(self):
            self.conn.close()


    app = Flask(__name__)

    from flask import request

    embeddings = Embeddings()

    @app.route('/get-context', methods=['POST'])
    def get_context():
        json = request.get_json()
        context = embeddings.get_context(json['query'])
        return context

    @app.route('/add-context', methods=['POST'])
    def get_context():
        json = request.get_json()
        query = json['query']
        lecture_id = json['lecture_id']
        embedding = embeddings.add_context(query, lecture_id)
        return context

    return app

