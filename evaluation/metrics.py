"""Evaluation metrics for memory systems."""

import statistics
from collections import defaultdict
from typing import Dict, List

import nltk
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
from rouge_score import rouge_scorer
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import pytorch_cos_sim

# Download required NLTK data
try:
    nltk.download("punkt", quiet=True)
    nltk.download("wordnet", quiet=True)
except Exception as e:
    print(f"Error downloading NLTK data: {e}")

# Initialize SentenceTransformer model
try:
    sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    print(f"Warning: Could not load SentenceTransformer model: {e}")
    sentence_model = None


def calculate_bleu_scores(prediction: str, reference: str) -> Dict[str, float]:
    """Calculate BLEU scores with different n-gram settings."""
    pred_tokens = nltk.word_tokenize(prediction.lower())
    ref_tokens = [nltk.word_tokenize(reference.lower())]

    weights_list = [
        (1, 0, 0, 0),  # BLEU-1
        (0.5, 0.5, 0, 0),  # BLEU-2
        (0.33, 0.33, 0.33, 0),  # BLEU-3
        (0.25, 0.25, 0.25, 0.25),  # BLEU-4
    ]
    smooth = SmoothingFunction().method1

    scores = {}
    for n, weights in enumerate(weights_list, start=1):
        try:
            score = sentence_bleu(
                ref_tokens, pred_tokens, weights=weights, smoothing_function=smooth
            )
        except Exception as e:
            print(f"Error calculating BLEU score: {e}")
            score = 0.0
        scores[f"bleu{n}"] = score

    return scores


def calculate_rouge_scores(prediction: str, reference: str) -> Dict[str, float]:
    """Calculate ROUGE scores for prediction against reference."""
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    scores = scorer.score(reference, prediction)
    return {
        "rouge1_f": scores["rouge1"].fmeasure,
        "rouge2_f": scores["rouge2"].fmeasure,
        "rougeL_f": scores["rougeL"].fmeasure,
    }


def calculate_f1_score(prediction: str, reference: str) -> float:
    """Calculate token-level F1 score."""
    pred_tokens = set(nltk.word_tokenize(prediction.lower()))
    ref_tokens = set(nltk.word_tokenize(reference.lower()))

    if not pred_tokens or not ref_tokens:
        return 0.0

    common = pred_tokens & ref_tokens
    if not common:
        return 0.0

    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(ref_tokens)

    return 2 * (precision * recall) / (precision + recall)


def calculate_semantic_similarity(prediction: str, reference: str) -> float:
    """Calculate semantic similarity using sentence embeddings."""
    if sentence_model is None:
        return 0.0

    try:
        pred_embedding = sentence_model.encode(prediction, convert_to_tensor=True)
        ref_embedding = sentence_model.encode(reference, convert_to_tensor=True)
        similarity = pytorch_cos_sim(pred_embedding, ref_embedding).item()
        return similarity
    except Exception as e:
        print(f"Error calculating semantic similarity: {e}")
        return 0.0


def calculate_metrics(prediction: str, reference: str) -> Dict[str, float]:
    """Calculate all metrics for a prediction-reference pair."""
    return {
        "f1": calculate_f1_score(prediction, reference),
        "semantic_similarity": calculate_semantic_similarity(prediction, reference),
        **calculate_bleu_scores(prediction, reference),
        **calculate_rouge_scores(prediction, reference),
    }


def aggregate_metrics(
    all_metrics: List[Dict[str, float]], all_categories: List[str]
) -> Dict:
    """Aggregate metrics across all examples, overall and per category."""
    aggregates = defaultdict(list)
    category_aggregates = defaultdict(lambda: defaultdict(list))

    # Collect all values for each metric
    for metrics, category in zip(all_metrics, all_categories):
        for metric_name, value in metrics.items():
            aggregates[metric_name].append(value)
            category_aggregates[category][metric_name].append(value)

    # Calculate statistics for overall metrics
    results = {"overall": {}}

    for metric_name, values in aggregates.items():
        results["overall"][metric_name] = {
            "mean": statistics.mean(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0.0,
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "count": len(values),
        }

    # Calculate statistics for each category
    for category in sorted(category_aggregates.keys()):
        results[f"category_{category}"] = {}
        for metric_name, values in category_aggregates[category].items():
            if values:
                results[f"category_{category}"][metric_name] = {
                    "mean": statistics.mean(values),
                    "std": statistics.stdev(values) if len(values) > 1 else 0.0,
                    "median": statistics.median(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values),
                }

    return results
