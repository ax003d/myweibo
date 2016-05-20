import os
import dotenv
import json
import jieba.analyse

from getenv import env
from functools import wraps
from weibo import Client
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from datetime import datetime

dotenv.read_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
API_KEY = env("API_KEY", "")
API_SECRET = env("API_SECRET", "")
REDIRECT_URI = env("REDIRECT_URI", "")
ES_HOSTS = env("ES_HOSTS", '["localhost:9200"]')
ES_INDEX = env("ES_INDEX", "myweibo")

client = Client(API_KEY, API_SECRET, REDIRECT_URI)
es = Elasticsearch(ES_HOSTS)
es.indices.create(index=ES_INDEX, ignore=400)


def authenticated(func):
    @wraps(func)
    def authenticate(*args, **kwargs):
        auth_path = os.path.join(BASE_DIR, ".auth.json")
        if os.path.exists(auth_path):
            with open(auth_path, 'r') as f:
                token = json.loads(f.read())
            client.set_token(token)
            if client.alive:
                return func(*args, **kwargs)
            print "token expired"
        print "visit this url to get code:"
        print client.authorize_url
        code = raw_input("code: ")
        if not code:
            print "no code input, exit now!"
            exit(0)
        client.set_code(code)
        with open(auth_path, 'w') as f:
            f.write(json.dumps(client.token))
        return func(*args, **kwargs)
    return authenticate


@authenticated
def welcome():
    try:
        me = es.get(
            index=ES_INDEX,
            doc_type="users",
            id=client.token["uid"])['_source']
    except NotFoundError:
        me = client.get('users/show', uid=client.token['uid'])
        me['timestamp'] = datetime.utcnow()
        es.index(
            index=ES_INDEX,
            doc_type="users",
            id=client.token["uid"],
            body=me)
    print "welcome {}!".format(me['name'])


def index_status(status):
    try:
        es.get(
            index=ES_INDEX,
            doc_type="status",
            id=status["id"])
    except NotFoundError:
        status["timestamp"] = datetime.utcnow()
        status["tags"] = list(jieba.analyse.extract_tags(status["text"]))
        es.index(
            index=ES_INDEX,
            doc_type="status",
            id=status["id"],
            body=status)


@authenticated
def status():
    resp = client.get('statuses/friends_timeline', count=100)
    statuses = resp['statuses']
    print "get {}".format(statuses)
    for i in statuses:
        index_status(i)


if __name__ == '__main__':
    # welcome()
    status()
