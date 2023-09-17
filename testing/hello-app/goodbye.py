from modal import Image, Stub, wsgi_app

@wsgi_app()
def testing(test_id):
    return "Testing " + test_id + "!"