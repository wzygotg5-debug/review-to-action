import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from pathlib import Path


def run_keyword_rating_baseline(csv_path: str) -> str:
    df = pd.read_csv(csv_path)

    required_cols = {"review_id", "product_name", "rating", "review_text"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    product_name = df["product_name"].iloc[0]
    avg_rating = df["rating"].mean()
    low_rating_count = (df["rating"] <= 2).sum()
    total_reviews = len(df)

    texts = df["review_text"].fillna("").astype(str)

    vectorizer = CountVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=15
    )
    X = vectorizer.fit_transform(texts)
    terms = vectorizer.get_feature_names_out()
    counts = X.toarray().sum(axis=0)

    top_terms = sorted(zip(terms, counts), key=lambda x: x[1], reverse=True)

    output = []
    output.append(f"# Keyword and Rating Baseline Report: {product_name}\n")
    output.append(f"Total reviews: {total_reviews}")
    output.append(f"Average rating: {avg_rating:.2f}")
    output.append(f"Low-rating reviews (rating <= 2): {low_rating_count}\n")

    output.append("## Top Keywords and Phrases")
    for term, count in top_terms:
        output.append(f"- {term}: {count}")

    output.append("\n## Baseline Limitation")
    output.append(
        "This baseline can identify frequent words and rating patterns, "
        "but it cannot reliably group semantically similar complaints, "
        "assign issue owners, judge severity, or produce a manager-ready action memo."
    )

    return "\n".join(output)


if __name__ == "__main__":
    result = run_keyword_rating_baseline("data/sample_reviews_moisturizer.csv")
    Path("outputs").mkdir(exist_ok=True)
    Path("outputs/baseline_output_moisturizer.md").write_text(result, encoding="utf-8")
    print(result)
