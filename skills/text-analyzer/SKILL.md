---
name: text-analyzer
description: Analyzes text metrics including word and character counts, estimated reading time, and sentiment polarity. Use when analyzing or evaluating written content.
version: "1.0.0"
tags: ["nlp", "text", "metrics"]
tools:
  - count_words_and_characters
  - analyze_sentiment
  - calculate_reading_time
---

# Text Analyzer Operating Procedure (SOP)

## Purpose
Provide precise, objective statistical and sentiment analysis on user-supplied text.

## Standard Workflow
1. For readability or size queries, call `count_words_and_characters`.
2. For reading duration estimates, call `calculate_reading_time`.
3. If tone, sentiment, or emotional polarity is requested, call `analyze_sentiment`.
4. Always summarize the metrics in a clean Markdown table.

## Constraints & Rules
- Do NOT guess or hallucinate text metrics without executing the tools.
- Do NOT guess sentiment without invoking `analyze_sentiment`.
- Keep the final summary concise and clear.
