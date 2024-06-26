"""Constants used by the application."""

from __future__ import annotations

import os
from pathlib import Path

CACHE_DIR = Path(os.getenv("CACHE_DIR", ".cache"))
CACHE_DIR.mkdir(exist_ok=True, parents=True)

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
DATA_DIR.mkdir(exist_ok=True, parents=True)

MODEL_DIR = Path(os.getenv("MODEL_DIR", "models"))
MODEL_DIR.mkdir(exist_ok=True, parents=True)

TOKENIZER_CACHE_DIR = CACHE_DIR / "tokenizer"
TOKENIZER_CACHE_DIR.mkdir(exist_ok=True, parents=True)

SENTIMENT140_PATH = DATA_DIR / "sentiment140.csv"
SENTIMENT140_URL = "https://www.kaggle.com/datasets/kazanova/sentiment140"

AMAZONREVIEWS_PATH = DATA_DIR / "amazonreviews.txt.bz2"
AMAZONREVIEWS_URL = "https://www.kaggle.com/datasets/bittlingmayer/amazonreviews"

IMDB50K_PATH = DATA_DIR / "imdb50k.csv"
IMDB50K_URL = "https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews"

TEST_DATASET_PATH = DATA_DIR / "test.csv"
TEST_DATASET_URL = "https://github.com/Tymec/sentiment-analysis/blob/main/data/test.csv?raw=true"

SLANGMAP_PATH = DATA_DIR / "slang.json"
SLANGMAP_URL = "https://github.com/Tymec/sentiment-analysis/blob/main/data/slang.json?raw=true"
