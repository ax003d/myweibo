import os
import dotenv
import json

from getenv import env
from functools import wraps
from weibo import Client


dotenv.read_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
API_KEY = env("API_KEY", "")
API_SECRET = env("API_SECRET", "")
REDIRECT_URI = env("REDIRECT_URI", "")

client = Client(API_KEY, API_SECRET, REDIRECT_URI)


def authenticated(func):
    @wraps(func)
    def authenticate(func):
        auth_path = os.path.join(BASE_DIR, ".auth.json")
        if os.path.exists(auth_path):
            with open(auth_path) as f:
                token = json.loads(f.read())
            client.set_token(token)
            if client.alive():
                return
            print "token expired"
        print "visit this url to get code:"
        print client.authorize_url
        code = raw_input("code: ")
        if not code:
            print "no code input, exit now!"
            exit(0)
        client.set_code(code)
        with open(auth_path) as f:
            f.write(json.dumps(client.token))
    return authenticate


@authenticated
def welcome():
    print client.get('/users/show')


if __name__ == '__main__':
    welcome()
