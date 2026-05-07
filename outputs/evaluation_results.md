# Evaluation Results

## Evaluation Setup

I evaluated Review-to-Action on six synthetic skincare review scenarios. Each scenario represents a realistic customer review batch that a skincare product manager might need to review.

The app was compared against two simpler baselines:

1. Keyword and rating baseline
2. Prompt-only LLM baseline

The keyword and rating baseline uses frequent words, bigrams, average rating, and low-rating count. The prompt-only baseline uses the same review content, but without the app's fixed workflow structure.

## Evaluation Rubric

Each case was scored from 0 to 2 on four dimensions.

| Dimension | Score Range | Meaning |
|---|---:|---|
| Issue grouping accuracy | 0-2 | Did the output group semantically similar complaints into useful product issue categories? |
| Evidence support | 0-2 | Did the output support each issue with review evidence or representative quotes? |
| Action usefulness | 0-2 | Did the output suggest useful owners, next steps, or escalation actions? |
| Human review boundary | 0-2 | Did the output clearly identify where a human should verify or make the final decision? |

Maximum score per case: 8.

## Summary Results

| Case | Main Issue Pattern | Keyword/Rating Baseline | Prompt-only Baseline | Review-to-Action App |
|---|---|---:|---:|---:|
| Case 1 | Irritation, greasy texture, packaging leakage | 4/8 | 6/8 | 8/8 |
| Case 2 | White cast, sticky feel, strong smell | 4/8 | 6/8 | 7/8 |
| Case 3 | Burning, redness, breakouts | 3/8 | 6/8 | 8/8 |
| Case 4 | Dryness, tight skin, sensitive skin complaints | 4/8 | 6/8 | 7/8 |
| Case 5 | Unclear effect, fragrance, expectation mismatch | 3/8 | 5/8 | 7/8 |
| Case 6 | Vague and emotional mixed feedback | 3/8 | 5/8 | 6/8 |

## Key Findings

The keyword and rating baseline was useful for quick descriptive statistics. It identified frequent terms and low-rating patterns, but it could not reliably group semantically similar complaints. For example, words such as "burning," "redness," "irritation," and "too harsh" may describe the same product issue, but the baseline treated them as separate terms.

The prompt-only baseline often produced helpful summaries, but the structure changed across cases. It did not always include severity levels, suggested owners, or clear human review boundaries.

Review-to-Action performed better because it forced the model to follow the same business workflow every time. The app consistently produced an issue triage table, risk flags, recommended actions, a manager-ready memo, and a human review checklist.

## Where the App Worked Best

The app worked best when the reviews contained repeated and concrete complaints, such as irritation, packaging leakage, greasy texture, or white cast. In these cases, the app grouped related comments into useful issue categories and provided reasonable next steps.

## Where the App Struggled

The app was weaker when reviews were short, vague, emotional, or mixed. In those cases, the model could still produce a structured report, but the evidence was less reliable. The app should not be trusted to make final product safety, medical, or recall decisions.

## Human Review Boundary

This tool is designed for first-pass product issue triage. A human product manager should review the original comments before making product changes. Safety-like complaints should be escalated to a human reviewer rather than treated as final evidence.
