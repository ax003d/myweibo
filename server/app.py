#!/usr/bin/env python3

import connexion
from settings import API_HOST

if __name__ == '__main__':
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.add_api('swagger.yaml', arguments={'host': API_HOST})
    app.run(port=8080)
