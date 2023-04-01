import gensim.downloader as api
import os


def download_gensim_dataset(name: str):
    return api.load(name, return_path=True)


if __name__ == '__main__':
    api.BASE_DIR = os.path.abspath(".")
    for dataset in ["text8"]:
        data_path = download_gensim_dataset(dataset)
        print(f'downloaded {dataset} at {data_path}')