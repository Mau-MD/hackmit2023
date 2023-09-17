import modal
from modal import Stub, Image, wsgi_app, Secret


stub = Stub("embeddings")
image = Image.debian_slim().apt_install("libpq-dev").pip_install("flask", "openai", "python-dotenv", "psycopg2")


@stub.function(image=image, secret=modal.Secret.from_name("DB"))
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

        def get_context(self, query, lecture_id):
            embedding = self._get_embedding(query)
            return self._get_embedding_best_match(embedding, lecture_id)

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
            query = f"INSERT INTO embeddings (lecture_id, text, vector) VALUES ({lecture_id}, '{text}', '{self.db.convert_to_vector(embedding)}')"
            self.db.execute_and_commit(query)
        
        def _get_embedding_best_match(self, embedding, lecture_id):
            return self.db.get_match(embedding, lecture_id)
        
    class DB:
        # constructor
        def __init__(self):
            self.conn = psycopg2.connect(database="opentutor",
                            host=os.environ["DB_HOST"],
                            user=os.environ["DB_USER"],
                            password=os.environ["DB_PASSWORD"],
                            port="5432")
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

        def get_match(self, query_embedding, lecture_id, n = 10):
            # vector = self.convert_to_vector(query_embedding)
            query = f"SELECT lecture_id, text, l2sq_dist(vector, ARRAY{query_embedding}) AS dist FROM embeddings WHERE lecture_id = {lecture_id} ORDER BY vector <-> ARRAY{query_embedding} LIMIT {n};"
            return self.execute_and_fetch(query)


        def __del__(self):
            self.conn.close()



    def ask_gpt(context, qry):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "user", "content": """
                Imagine you are a very enthusiastic professor at a very prestigious university. You just gave a lecture which I will give you as context, and a student has a question for you. Answer in a helpful way, using content ONLY from the lecture you just gave. Do not respond with information outside the context I will give to you. If you don't know the answer,
                do not invent things, simply say that you currently cannot help with the question, or that you don't know the answer. If figure examples are available always mention and reference them.
                ---
                Context: """ + context + """.
                ---
                The question the student has is:""" + qry + """
                ---
                Start the answer by saying: "As seen on the lecture..." or something similar
                ---
                DO NOT USE INFORMATION IF IS NOT PROVIDED IN THE CONTEXT. If you don't have context to answer the question just say "I don't know the answer to that question" or "I don't have enough information to answer that question" or something similar."""},
            ],
            temperature=0.7
        )

        return response['choices'][0]['message']['content']

    app = Flask(__name__)

    from flask import request

    embeddings = Embeddings()

    @app.route('/chat', methods=['POST'])
    def chat():
        json = request.get_json()

        query= json['query'].replace("'", "")
        lecture_id = json['lecture_id']

        contexts = embeddings.get_context(query, lecture_id)

        context_arr = []

        for context in contexts:
            context_text = context[1]
            context_arr.append(context_text)
        


        response = ask_gpt("\n".join(context_arr), json['query'])
        return response



    @app.route('/get-context', methods=['POST'])
    def get_context():
        json = request.get_json()
        query = json['query'].replace("'", "")
        lecture_id = json['lecture_id']
        context = embeddings.get_context(query, lecture_id)
        return context

    @app.route('/add-context', methods=['POST'])
    def add_context():
        json = request.get_json()
        query = json['query'].replace("'", "")
        lecture_id = json['lecture_id']
        embedding = embeddings.add_context(query, lecture_id)
        return "success"

    return app

