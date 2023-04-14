import gensim
from gensim.models.doc2vec import Doc2Vec
from data_collection.places import Location
from numpy import dot
from numpy.linalg import norm

class Model:
    def __init__(self):
        self.model = Doc2Vec.load("models/text8_model")

    def _cosine_similarity(self, text1: str, text2: str) -> float:
        embed1 = self.model.infer_vector(gensim.utils.simple_preprocess(text1))
        embed2 = self.model.infer_vector(gensim.utils.simple_preprocess(text2))
        # Cosine similarity
        return dot(embed1, embed2) / (norm(embed1)) / (norm(embed2)).item()

    def top(self, keyword: str, locations: list[Location]) \
            -> list[tuple[Location, float]]:
        def get_similarity(word: str, location: Location) -> float:
            information = location.name + ' '.join(location.information)
            return self._cosine_similarity(word, information)

        result = []
        for loc in locations:
            result.append((loc, get_similarity(keyword, loc)))

        result.sort(key=lambda x: x[1])
        return result
