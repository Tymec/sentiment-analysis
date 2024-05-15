from __future__ import annotations

import os
from pathlib import Path

CACHE_DIR = Path(os.getenv("CACHE_DIR", ".cache"))
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
MODELS_DIR = Path(os.getenv("MODELS_DIR", "models"))

SENTIMENT140_PATH = DATA_DIR / "sentiment140.csv"
SENTIMENT140_URL = "https://www.kaggle.com/datasets/kazanova/sentiment140"

AMAZONREVIEWS_PATH = (DATA_DIR / "amazonreviews.test.txt.bz2", DATA_DIR / "amazonreviews.train.txt.bz2")
AMAZONREVIEWS_URL = "https://www.kaggle.com/datasets/bittlingmayer/amazonreviews"

IMDB50K_PATH = DATA_DIR / "imdb50k.csv"
IMDB50K_URL = "https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews"

URL_REGEX = r"(https:\/\/www\.|http:\/\/www\.|https:\/\/|http:\/\/)?[a-zA-Z]{2,}(\.[a-zA-Z]{2,})(\.[a-zA-Z]{2,})?\/[a-zA-Z0-9]{2,}|((https:\/\/www\.|http:\/\/www\.|https:\/\/|http:\/\/)?[a-zA-Z]{2,}(\.[a-zA-Z]{2,})(\.[a-zA-Z]{2,})?)|(https:\/\/www\.|http:\/\/www\.|https:\/\/|http:\/\/)?[a-zA-Z0-9]{2,}\.[a-zA-Z0-9]{2,}\.[a-zA-Z0-9]{2,}(\.[a-zA-Z0-9]{2,})?"  # https://www.freecodecamp.org/news/how-to-write-a-regular-expression-for-a-url/
EMOTICON_MAP = {
    "SMILE": [":)", ":-)", ": )", ":D", ":-D", ": D", ";)", ";-)", "; )", ":>", ":->", ": >", ":]", ":-]", ": ]"],
    "LOVE": ["<3", ":*", ":-*", ": *"],
    "WINK": [";)", ";-)", "; )", ";>", ";->", "; >"],
    "FROWN": [":(", ":-(", ": (", ":[", ":-[", ": ["],
    "CRY": [":'(", ": (", ":' (", ":'[", ":' ["],
    "SURPRISE": [":O", ":-O", ": O", ":0", ":-0", ": 0", ":o", ":-o", ": o"],
    "ANGRY": [">:(", ">:-(", "> :(", ">:["],
}

CACHE_DIR.mkdir(exist_ok=True, parents=True)
DATA_DIR.mkdir(exist_ok=True, parents=True)
MODELS_DIR.mkdir(exist_ok=True, parents=True)