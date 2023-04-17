ML backend for Scenic Route Recommender AIM Labs Spring 2023
* Large training data files are stored in `./data`, but are obviously not included in git. 
  * Run `./data/downloader.py` to get these data files. 
* Similarly, models are stored in `./models`, but not in git

Resources:
* [Google Maps Python API](https://github.com/googlemaps/google-maps-services-python)
  * [Useful Examples](https://github.com/googlemaps/google-maps-services-python/blob/master/tests)
  * [Python Docs](https://googlemaps.github.io/google-maps-services-python/docs/index.html)
* [Env Variables](https://dev.to/jakewitcher/using-env-files-for-environment-variables-in-python-applications-55a1)
* Doc2Vec
* TripAdvisor API
* Instagram API
* Video to trip? 
* Concatenate all adjectives (part of speech labeling)
* not adjectives but nouns: hills, lakes, etc.
  * Because a lot of "good" adjectives are the same

Efficiency
* waypoints - come up with an algorithm that selects a set of waypoitns that does not have overlap
* waypoints - generate new points beyond the route to perform more nearby searches
* filtering - filter based on total reviews/rating?
* reviews - google about (editorial summary), reviews, wikipedia (free), tripadvisor?
* average word2vec
* get routes through top-performing detours

Pip packages (requirements.txt included):
* `python-dotenv`
* `googlemaps`
* `open-ai`
* `gensim`

Meeting with Zack:
* Use Doc2Vec as a first pass preprocessing to filter thousands of locations -> few dozen
  * cosine similarity
* Use ChatGPT to then compare the keywords to the reviews/ information about the few dozen locations to pick the best one. 
* ChatGPT API
  * For every prompt, to get ChatGPT to respond in a format that you want, use prompt engineering.
  * Be very specific with the prompt ("treat ChatGPT like a 5 year old"). 
  * Describe the general framework/ give instructions.
  * Ex: 
* Models on HuggingFace