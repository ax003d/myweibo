import os
from settings import DATA_PATH


def v1_tagignore_post(body):
    with open(os.path.join(DATA_PATH, 'tagignore'), 'ab') as f:
        for i in body['tagignore']:
            f.write(i.encode())
            f.write('\n'.encode())
    return ''
