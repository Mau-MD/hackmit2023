import modal
from modal import Stub, Image, wsgi_app, Secret, Mount
from pathlib import Path


stub = Stub("embeddings")
image = Image.debian_slim().apt_install("libpq-dev").pip_install("flask", "openai", "python-dotenv", "psycopg2", "flask-swagger-ui", "PyYAML", "flask_cors")

assets_path = Path(__file__).parent / "assets"
@stub.function(image=image, secret=modal.Secret.from_name("DB"), mounts=[Mount.from_local_dir(assets_path, remote_path="/assets")])
@wsgi_app()
def app():
    from flask import Flask
    import os
    import pickle
    import openai
    import psycopg2
    from urllib.parse import unquote


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
            try:
                self.cursor.execute(query)
                return self.cursor.fetchall()
            except:
                return []
        
        def execute_and_commit(self, query):
            try:
                self.cursor.execute(query)
                self.conn.commit()
            except:
                self.conn.rollback()
                return False
        
        def convert_to_vector(self,embedding):
            return "{" + ",".join([str(x) for x in embedding]) + "}"

        def get_match(self, query_embedding, lecture_id, n = 10):
            # vector = self.convert_to_vector(query_embedding)
            query = f"SELECT lecture_id, text, l2sq_dist(vector, ARRAY{query_embedding}) AS dist FROM embeddings WHERE lecture_id = {lecture_id} ORDER BY vector <-> ARRAY{query_embedding} LIMIT {n};"
            return self.execute_and_fetch(query)

        def add_class(self, class_name):
            query = f"INSERT INTO class (name) VALUES ('{class_name}') RETURNING class_id;"
            self.cursor.execute(query)
            class_id = self.cursor.fetchone()[0]
            self.conn.commit()
            return class_id
        
        def add_lecture(self, lecture_name, class_id, url):
            query = f"INSERT INTO lecture (name, class_id, url) VALUES ('{lecture_name}', {class_id}, '{url}') RETURNING lecture_id;"
            self.cursor.execute(query)
            lecture_id = self.cursor.fetchone()[0]
            self.conn.commit()
            return lecture_id

        def get_lecture_id_by_url(self, url):
            query = f"SELECT lecture_id FROM lecture WHERE url = '{url}';"
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            if result is None:
                return -1
            else:
                return result[0]

        def kill(self):
            query = "DELETE FROM embeddings;"
            self.execute_and_commit(query)

            query = "DELETE FROM lecture;"
            self.execute_and_commit(query)

            query = "DELETE FROM class;"
            self.execute_and_commit(query)

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
                DO NOT USE INFORMATION AND DO NOT ADD IT TO THE ANSWER IF IS NOT PROVIDED IN THE CONTEXT. If you don't have context to answer the question just say "I don't know the answer to that question" or "I don't have enough information to answer that question" or something similar."""},
            ],
            temperature=0.7
        )

        return response['choices'][0]['message']['content']

    from flask import Flask, request
    from flask_cors import CORS
    from flask_swagger_ui import get_swaggerui_blueprint

    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})  # This will enable CORS for all routes

    embeddings = Embeddings()

    SWAGGER_URL = '/docs'  # URL for exposing Swagger UI (without trailing '/')
    API_URL='https://mau-md--embeddings-app.modal.run/spec'

    # Call factory function to create our blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
        API_URL,
        config={  # Swagger UI config overrides
            'app_name': "Embeddings API"
        }
    )

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

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
        return {'response': response}

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

    @app.route('/add-class', methods=['POST'])
    def add_class():
        json = request.get_json()
        class_name = json['class_name'].replace("'", "")

        res = embeddings.db.add_class(class_name)
        return str(res)

    @app.route('/add-lecture', methods=['POST'])
    def add_lecture():
        json = request.get_json()

        lecture_name = json['lecture_name'].replace("'", "")
        class_id = json['class_id']
        url = json['url'].replace("'", "")


        res =  embeddings.db.add_lecture(lecture_name, class_id, url)
        return str(res)

    @app.route('/get-lecture-id/<url>')
    def get_lecture_id(url):

        url = url.replace("'", "")
        decoded_url = unquote(url)

        res = embeddings.db.get_lecture_id_by_url(decoded_url)
        return {'id': str(res)}


    @app.route('/kill')
    def kill(url):
        res = embeddings.db.kill()
        return 'ok'

    from flask import send_file

    @app.route('/spec', methods=['GET'])
    def spec_yaml():
        return send_file('/assets/spec.yaml', mimetype='text/yaml')


    from flask import Response

    @app.route("/get-watson", methods=['GET'])
    def get_watson():
        data = """
            window.watsonAssistantChatOptions = {
                integrationID: "aec400f8-ffeb-4672-a3b0-5c0ec7582f75", // The ID of this integration.
                region: "us-east", // The region your integration is hosted in.
                serviceInstanceID: "e5fa945d-0470-491c-a731-719f63cd76ff", // The ID of your service instance.
                onLoad: function(instance) { instance.render(); }
            };
            setTimeout(function(){
                const t=document.createElement('script');
                t.src="https://web-chat.global.assistant.watson.appdomain.cloud/versions/" + (window.watsonAssistantChatOptions.clientVersion || 'latest') + "/WatsonAssistantChatEntry.js";
                document.head.appendChild(t);
            });
        """

        return Response(data, mimetype='application/javascript')
    return app

