from modal import Stub, web_endpoint

stub = Stub()




@stub.function()
@web_endpoint()
def insert_embedding():
    return "Hello world!"