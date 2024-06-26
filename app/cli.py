"""CLI using Click."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Literal

import click
import joblib
import pandas as pd

from app.constants import TOKENIZER_CACHE_DIR

__all__ = ["cli_wrapper"]

DONE_STR = click.style("DONE", fg="green")


def _load_dataset(
    dataset: str,
    batch_size: int = 512,
    n_jobs: int = 4,
    force_cache: bool = False,
) -> tuple[pd.Series, pd.Series]:
    """Helper function to load and tokenize the dataset or use cached data if available.

    Args:
        dataset: Name of the dataset
        batch_size: Batch size for tokenization
        n_jobs: Number of parallel jobs
        force_cache: Whether to force using the cached data

    Returns:
        Tokenized text data and label data
    """
    from app.data import load_data, tokenize
    from app.utils import deserialize, serialize

    token_cache_path = TOKENIZER_CACHE_DIR / f"{dataset}_tokenized.pkl"
    label_cache_path = TOKENIZER_CACHE_DIR / f"{dataset}_labels.pkl"
    use_cached_data = False

    if token_cache_path.exists() and label_cache_path.exists():
        use_cached_data = force_cache or click.confirm(
            f"Found existing tokenized data for '{dataset}'. Use it?",
            default=True,
        )

    if use_cached_data:
        click.echo("Loading cached data... ", nl=False)
        token_data = pd.Series(deserialize(token_cache_path))
        label_data = joblib.load(label_cache_path)
        click.echo(DONE_STR)
    else:
        click.echo("Loading dataset... ", nl=False)
        text_data, label_data = load_data(dataset)
        click.echo(DONE_STR)

        click.echo("Tokenizing data... ")
        token_data = tokenize(text_data, batch_size=batch_size, n_jobs=n_jobs, show_progress=True)
        serialize(token_data, token_cache_path, show_progress=True)
        joblib.dump(label_data, label_cache_path, compress=3)

    click.echo("Dataset vocabulary size: ", nl=False)
    vocab = token_data.explode().value_counts()
    click.secho(str(len(vocab)), fg="blue")

    return token_data, label_data


@click.group()
def cli() -> None: ...


@cli.command()
@click.option(
    "--model",
    "model_path",
    required=True,
    help="Path to the trained model",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True, path_type=Path),
)
@click.option(
    "--share/--no-share",
    default=False,
    help="Whether to create a shareable link",
)
def gui(model_path: Path, share: bool) -> None:
    """Launch the Gradio GUI"""
    from app.gui import launch_gui

    os.environ["MODEL_PATH"] = model_path.as_posix()
    launch_gui(share)


@cli.command()
@click.option(
    "--model",
    "model_path",
    required=True,
    help="Path to the trained model",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True, path_type=Path),
)
@click.argument("text", nargs=-1)
def predict(model_path: Path, text: list[str]) -> None:
    """Perform sentiment analysis on the provided text.

    Note: Piped input takes precedence over the text argument
    """
    from app.model import infer_model

    # Combine the text arguments into a single string
    text = " ".join(text).strip()
    if not sys.stdin.isatty():
        # If there is piped input, read it
        piped_text = sys.stdin.read().strip()
        text = piped_text or text

    if not text:
        msg = "No text provided"
        raise click.UsageError(msg)

    click.echo("Loading model... ", nl=False)
    model = joblib.load(model_path)
    click.echo(DONE_STR)

    click.echo("Performing sentiment analysis... ", nl=False)
    prediction = infer_model(model, [text])[0]
    if prediction == 0:
        sentiment = click.style("NEGATIVE", fg="red")
    elif prediction == 1:
        sentiment = click.style("POSITIVE", fg="green")
    else:
        sentiment = click.style("NEUTRAL", fg="yellow")
    click.echo(sentiment)


@cli.command()
@click.option(
    "--dataset",
    default="test",
    help="Dataset to evaluate the model on",
    type=click.Choice(["test", "sentiment140", "amazonreviews", "imdb50k"]),
)
@click.option(
    "--model",
    "model_path",
    required=True,
    help="Path to the trained model",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True, path_type=Path),
)
@click.option(
    "--cv",
    default=5,
    help="Number of cross-validation folds",
    show_default=True,
    type=click.IntRange(2, 50),
)
@click.option(
    "--token-batch-size",
    default=512,
    help="Size of the batches used in tokenization",
    show_default=True,
)
@click.option(
    "--token-jobs",
    default=4,
    help="Number of parallel jobs to run for tokenization",
    show_default=True,
)
@click.option(
    "--eval-jobs",
    default=1,
    help="Number of parallel jobs to run for evaluation",
    show_default=True,
)
@click.option(
    "--force-cache",
    is_flag=True,
    help="Always use the cached tokenized data (if available)",
)
def evaluate(
    dataset: Literal["test", "sentiment140", "amazonreviews", "imdb50k"],
    model_path: Path,
    cv: int,
    token_batch_size: int,
    token_jobs: int,
    eval_jobs: int,
    force_cache: bool,
) -> None:
    """Evaluate the model on the the specified dataset"""
    from app.model import evaluate_model

    token_data, label_data = _load_dataset(dataset, token_batch_size, token_jobs, force_cache)

    click.echo("Loading model... ", nl=False)
    model = joblib.load(model_path)
    click.echo(DONE_STR)

    click.echo("Evaluating model... ")
    acc_mean, acc_std = evaluate_model(
        model,
        token_data,
        label_data,
        cv=cv,
        n_jobs=eval_jobs,
    )
    click.secho(f"{acc_mean:.2%} ± {acc_std:.2%}", fg="blue")


@cli.command()
@click.option(
    "--dataset",
    required=True,
    help="Dataset to train the model on",
    type=click.Choice(["sentiment140", "amazonreviews", "imdb50k"]),
)
@click.option(
    "--vectorizer",
    default="tfidf",
    help="Vectorizer to use",
    type=click.Choice(["tfidf", "count", "hashing"]),
)
@click.option(
    "--max-features",
    default=20000,
    help="Maximum number of features (should be greater than 2^15 when using hashing vectorizer)",
    show_default=True,
    type=click.IntRange(1, None),
)
@click.option(
    "--min-df",
    default=5,
    help="Minimum document frequency for the features (ignored for hashing)",
    show_default=True,
)
@click.option(
    "--cv",
    default=5,
    help="Number of cross-validation folds",
    show_default=True,
    type=click.IntRange(2, 50),
)
@click.option(
    "--token-batch-size",
    default=512,
    help="Size of the batches used in tokenization",
    show_default=True,
)
@click.option(
    "--token-jobs",
    default=4,
    help="Number of parallel jobs to run for tokenization",
    show_default=True,
)
@click.option(
    "--train-jobs",
    default=1,
    help="Number of parallel jobs to run for training",
    show_default=True,
)
@click.option(
    "--seed",
    default=42,
    help="Random seed (-1 for random seed)",
    show_default=True,
    type=click.IntRange(-1, None),
)
@click.option(
    "--overwrite",
    is_flag=True,
    help="Overwrite the model file if it already exists",
)
@click.option(
    "--force-cache",
    is_flag=True,
    help="Always use the cached tokenized data (if available)",
)
def train(
    dataset: Literal["sentiment140", "amazonreviews", "imdb50k"],
    vectorizer: Literal["tfidf", "count", "hashing"],
    max_features: int,
    min_df: int,
    cv: int,
    token_batch_size: int,
    token_jobs: int,
    train_jobs: int,
    seed: int,
    overwrite: bool,
    force_cache: bool,
) -> None:
    """Train the model on the provided dataset"""
    from app.constants import MODEL_DIR
    from app.model import train_model

    model_path = MODEL_DIR / f"{dataset}_{vectorizer}_ft{max_features}.pkl"
    if model_path.exists() and not overwrite:
        click.confirm(f"Model file '{model_path}' already exists. Overwrite?", abort=True)

    token_data, label_data = _load_dataset(dataset, token_batch_size, token_jobs, force_cache)

    click.echo("Training model... ")
    model, accuracy = train_model(
        token_data,
        label_data,
        vectorizer=vectorizer,
        max_features=max_features,
        min_df=min_df,
        cv=cv,
        n_jobs=train_jobs,
        seed=seed,
    )

    click.echo("Model accuracy: ", nl=False)
    click.secho(f"{accuracy:.2%}", fg="blue")

    click.echo("Model saved to: ", nl=False)
    joblib.dump(model, model_path, compress=3)
    click.secho(str(model_path), fg="blue")


def cli_wrapper() -> None:
    cli(max_content_width=120)


if __name__ == "__main__":
    cli_wrapper()
