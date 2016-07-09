import json
import os
import dotenv

dotenv.read_dotenv()

from getenv import env

DATA_PATH = env("DATA_PATH", "/data")


def v1_tagignore_post(body):
    with open(os.path.join(DATA_PATH, 'tagignore'), 'a') as f:
        f.write('\n')
        f.writelines('\n'.join(body['tagignore']))
    return json.dumps({})
