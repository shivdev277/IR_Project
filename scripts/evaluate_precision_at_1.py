import json
import os
import sys

# Ensure project root is on path when script is run from scripts/ directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.search import search_top_k


def normalize_name(name: str) -> str:
    return os.path.basename(name.strip()).lower()


def evaluate_precision_at_1(test_set_path: str) -> float:
    """Compute Precision@1 using manual relevance labels from a JSON test set."""
    if not os.path.exists(test_set_path):
        raise FileNotFoundError(f"Test set not found: {test_set_path}")

    with open(test_set_path, "r", encoding="utf-8") as file:
        test_queries = json.load(file)

    if not test_queries:
        raise ValueError("Test set is empty. Add at least one query in evaluation/test_queries.json")

    total = 0
    correct = 0

    print("\nPrecision@1 Evaluation\n")
    print("-" * 110)
    print(f"{'#':<3} {'Course':<8} {'Query':<45} {'Top-1 File':<38} {'Relevant':<8}")
    print("-" * 110)

    for index, item in enumerate(test_queries, start=1):
        course = item["course"]
        query = item["query"]
        relevant_files = [normalize_name(name) for name in item.get("relevant_files", [])]

        embedding_file = os.path.join("embeddings", f"{course}.pkl")
        ranked = search_top_k(query=query, embedding_file=embedding_file, k=1)

        if not ranked:
            top_file = "<no-result>"
            is_relevant = False
        else:
            top_file = ranked[0]["page"].get("pdf", "Unknown")
            is_relevant = normalize_name(top_file) in relevant_files

        total += 1
        correct += int(is_relevant)

        query_preview = query if len(query) <= 44 else f"{query[:41]}..."
        file_preview = top_file if len(top_file) <= 37 else f"{top_file[:34]}..."
        print(f"{index:<3} {course:<8} {query_preview:<45} {file_preview:<38} {str(is_relevant):<8}")

    precision_at_1 = correct / total

    print("-" * 110)
    print(f"Total Queries      : {total}")
    print(f"Correct Top Result : {correct}")
    print(f"Precision@1        : {precision_at_1:.4f}")
    print("-" * 110)

    return precision_at_1


if __name__ == "__main__":
    evaluate_precision_at_1(os.path.join("evaluation", "test_queries.json"))
