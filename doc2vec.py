import gensim.downloader as api
from pprint import pprint
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


if __name__ == '__main__':
    sample_corpora: dict[str, any] = api.info()['corpora']
    for (name, info) in sample_corpora.items():
        pprint(f'name: {name}')
        pprint(info['description'])
