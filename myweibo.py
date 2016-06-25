import os
import dotenv
import json
import jieba
import jieba.analyse

from getenv import env
from functools import wraps
from weibo import Client
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError, RequestError
from datetime import datetime, timedelta

dotenv.read_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = env("DATA_PATH", "/data")
API_KEY = env("API_KEY", "")
API_SECRET = env("API_SECRET", "")
REDIRECT_URI = env("REDIRECT_URI", "")
ES_HOSTS = env("ES_HOSTS", '["localhost:9200"]')
ES_INDEX = env("ES_INDEX", "myweibo")
ES_MAPPINGS = {
    "mappings": {
        "status": {
            "properties": {
                "text": {
                    "type": "string",
                    "analyzer": "smartcn"
                },
                "tags": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "index": "not_analyzed"
                        }
                    }
                },
                "geo": {
                    "type": "object",
                    "properties": {
                        "coordinates": {
                            "type": "geo_point"
                        }
                    }
                }
            }
        }
    }
}

client = Client(API_KEY, API_SECRET, REDIRECT_URI)
es = Elasticsearch(ES_HOSTS)
if not es.indices.exists(ES_INDEX):
    es.indices.create(index=ES_INDEX, body=ES_MAPPINGS)
jieba.load_userdict(os.path.join(DATA_PATH, 'usr_dict.txt'))
tags_ignored = set()
with open(os.path.join(DATA_PATH, 'tagignore'), 'r') as f:
    tags_ignored.update([i.strip().decode('utf8') for i in f.readlines()])


def authenticated(func):
    @wraps(func)
    def authenticate(*args, **kwargs):
        auth_path = os.path.join(DATA_PATH, ".auth.json")
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
        return False
    except NotFoundError:
        status["timestamp"] = datetime.strptime(status['created_at'], '%a %b %d %H:%M:%S +0800 %Y') - timedelta(hours=8)
        status["tags"] = list(
            set(jieba.analyse.extract_tags(status["text"])) - tags_ignored)
        status["url"] = "http://api.weibo.com/2/statuses/go?uid={}&id={}".format(
            status['user']['idstr'], status['idstr'])
        geo = status['geo']
        if geo is not None:
            geo['coordinates'] = geo['coordinates'][::-1]
        es.index(
            index=ES_INDEX,
            doc_type="status",
            id=status["id"],
            body=status)
        return True


@authenticated
def status(since_id=None, max_id=None):
    print "status since_id {} max_id {}".format(since_id, max_id)
    if since_id is None:
        try:
            since_id = es.search(
                index='myweibo',
                doc_type='status',
                sort='id:desc',
                size=1)['hits']['hits'][0]["_source"]["id"]
        except NotFoundError:
            since_id = 0
        except RequestError:
            since_id = 0
    if max_id is None:
        resp = client.get('statuses/friends_timeline', count=100, since_id=since_id)
    else:
        resp = client.get('statuses/friends_timeline', count=100, since_id=since_id, max_id=max_id)
    statuses = resp['statuses']
    if len(statuses) == 0:
        return

    cnt = 0
    for i in statuses:
        if index_status(i):
            cnt += 1
    print "indexed {} status".format(cnt)
    max_id = statuses[-1]["id"]
    if cnt == 100 and since_id != 0:
        status(since_id, max_id)


if __name__ == '__main__':
    status()
