import os
from pathlib import Path

import pandas as pd
import streamlit as st
from openai import OpenAI
from sklearn.feature_extraction.text import CountVectorizer


APP_TITLE = "Review-to-Action: Skincare Product Issue Triage Tool"


def run_keyword_rating_baseline(df: pd.DataFrame) -> str:
    required_cols = {"review_id", "product_name", "rating", "review_text"}
    missing = required_cols - set(df.columns)
    if missing:
        return f"Missing required columns: {missing}"

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


def build_review_records(df: pd.DataFrame) -> str:
    records = []
    for _, row in df.iterrows():
        records.append(
            {
                "review_id": str(row.get("review_id", "")),
                "product_name": str(row.get("product_name", "")),
                "rating": str(row.get("rating", "")),
                "review_date": str(row.get("review_date", "")),
                "review_text": str(row.get("review_text", "")),
            }
        )
    return pd.DataFrame(records).to_json(orient="records", indent=2)


def run_genai_triage(df: pd.DataFrame, product_type: str, business_goal: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return (
            "ERROR: OPENAI_API_KEY is not set.\n\n"
            "Please set it in Terminal with:\n\n"
            "export OPENAI_API_KEY='your_api_key_here'\n\n"
            "Then run the Streamlit app again."
        )

    client = OpenAI(api_key=api_key)

    prompt_path = Path("prompts/triage_prompt.md")
    system_prompt = prompt_path.read_text(encoding="utf-8")

    review_records = build_review_records(df)

    user_prompt = f"""
Product type: {product_type}
Business goal: {business_goal}

Customer review records:
{review_records}

Please produce the product issue triage report using the required output format.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.2,
        max_output_tokens=2500,
    )

    return response.output_text


def load_sample_data() -> pd.DataFrame:
    sample_path = Path("data/sample_reviews_moisturizer.csv")
    return pd.read_csv(sample_path)


def validate_dataframe(df: pd.DataFrame) -> list:
    required_cols = ["review_id", "product_name", "rating", "review_date", "review_text"]
    issues = []

    for col in required_cols:
        if col not in df.columns:
            issues.append(f"Missing column: {col}")

    if "rating" in df.columns:
        try:
            pd.to_numeric(df["rating"])
        except Exception:
            issues.append("Column 'rating' must be numeric.")

    if len(df) == 0:
        issues.append("The uploaded file has no rows.")

    return issues


def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")

    st.title(APP_TITLE)

    st.write(
        "This app helps skincare product managers convert customer review exports "
        "into issue categories, severity levels, evidence quotes, suggested owners, "
        "and a manager-ready action memo."
    )

    st.info(
        "This is an internal product management workflow tool, not a consumer shopping assistant. "
        "It supports first-pass triage and keeps final decisions with a human reviewer."
    )

    st.sidebar.header("Input Settings")

    product_type = st.sidebar.selectbox(
        "Product type",
        ["Moisturizer", "Cleanser", "Sunscreen", "Serum", "Acne Treatment", "Other"]
    )

    business_goal = st.sidebar.selectbox(
        "Business goal",
        [
            "Product improvement",
            "Packaging issue review",
            "Marketing claim review",
            "Safety-like complaint triage",
            "Customer support prioritization",
        ]
    )

    uploaded_file = st.sidebar.file_uploader(
        "Upload review CSV",
        type=["csv"]
    )

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        data_source = "Uploaded CSV"
    else:
        df = load_sample_data()
        data_source = "Sample CSV"

    st.subheader("Review Data")
    st.caption(f"Data source: {data_source}")
    st.dataframe(df, use_container_width=True)

    validation_issues = validate_dataframe(df)

    if validation_issues:
        st.error("The review file has problems:")
        for issue in validation_issues:
            st.write(f"- {issue}")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Baseline: Keyword and Rating Summary")
        baseline_output = run_keyword_rating_baseline(df)
        st.markdown(baseline_output)

    with col2:
        st.subheader("GenAI Review-to-Action Triage")
        st.write(
            "Click the button below to generate issue categories, severity scores, "
            "risk flags, suggested owners, and a manager-ready memo."
        )

        if st.button("Run GenAI Triage"):
            with st.spinner("Generating product issue triage report..."):
                try:
                    triage_output = run_genai_triage(df, product_type, business_goal)
                    st.markdown(triage_output)

                    Path("outputs").mkdir(exist_ok=True)
                    Path("outputs/sample_output_moisturizer.md").write_text(
                        triage_output,
                        encoding="utf-8"
                    )

                    st.success("Output saved to outputs/sample_output_moisturizer.md")
                except Exception as e:
                    st.error("OpenAI API call failed.")
                    st.write(str(e))


if __name__ == "__main__":
    main()
