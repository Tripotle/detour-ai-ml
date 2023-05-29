"""
Alex Dang and Frank Lee 2023

Reference:
https://towardsdatascience.com/build-deploy-a-react-flask-app-47a89a5d17d9
"""
import os

from src import get_detours, api

from flask import Flask, request, Response
from flask_cors import CORS


def create_app() -> Flask:
    # create and configure the app

    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY')
    )

    @app.route('/')
    def serve():
        key = request.args.get('key',
                               type=str)
        if key != api.get_backend_key():
            return Response("Invalid key", status=401)

        keyword = request.args.get('keyword',
                                   type=str)
        # useful test: 'ChIJh2oa9apw44kRPCAIs6WO4NA' for MIT
        origin = request.args.get('origin',
                                  type=str)
        # useful test: 'ChIJLw8wo4Vw44kRWkWR0c03LH4' for Boston City Hall
        destination = request.args.get('destination',
                                       type=str)

        target_count = request.args.get('targetCount',
                                        default=None,
                                        type=int)
        if target_count is not None and target_count <= 0:
            return Response("target count must be positive", status=400)

        model_weight = request.args.get('modelWeight',
                                        default=None,
                                        type=float)
        if model_weight is not None and model_weight < 0:
            return Response("model weight must be non-negative", status=400)

        distance_weight = request.args.get('distanceWeight',
                                           default=None,
                                           type=float)
        if distance_weight is not None and distance_weight < 0:
            return Response("distance weight must be non-negative", status=400)

        popularity_weight = request.args.get('popularityWeight',
                                             default=None,
                                             type=float)
        if popularity_weight is not None and popularity_weight < 0:
            return Response("popularity weight must be non-negative", status=400)

        if model_weight is not None or distance_weight is not None or popularity_weight is not None:
            sum = 0
            if model_weight is not None:
                sum += model_weight
            if distance_weight is not None:
                sum += distance_weight
            if popularity_weight is not None:
                sum += popularity_weight
            if sum <= 0:
                return Response("sums of weights must be positive", status=400)

        return get_detours(keyword, origin, destination, target_count, model_weight, distance_weight, popularity_weight).to_dict()

    CORS(app)

    return app
