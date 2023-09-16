from flask import Flask
from embeddings import Embeddings

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

if __name__ == '__main__':
    app.run(debug=True)
