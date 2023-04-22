"""
Alex Dang and Frank Lee 2023

Reference:
https://towardsdatascience.com/build-deploy-a-react-flask-app-47a89a5d17d9
"""

from src import api

from flask import Flask, request
def create_app() -> Flask:
    # create and configure the app

    app = Flask(__name__)

    @app.route('/')
    def index():
        origin = request.args.get('origin',
                                  default='ChIJh2oa9apw44kRPCAIs6WO4NA', # MIT
                                  type=str)
        destination = request.args.get('destination',
                                       default='ChIJLw8wo4Vw44kRWkWR0c03LH4', # Boston City Hall
                                       type=str)

        return f"desired route: {origin} -> {destination}"


    return app
