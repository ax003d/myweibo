import os
from settings import DATA_PATH


def v1_tagignore_post(body):
    with open(os.path.join(DATA_PATH, 'tagignore'), 'a') as f:
        f.write('\n')
        f.writelines('\n'.join(body['tagignore']))
    return ''
