import psycopg2

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
    