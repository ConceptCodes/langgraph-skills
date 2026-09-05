import re

from langchain_core.tools import tool


@tool
def count_words_and_characters(text: str) -> dict:
    """Calculates word count, character count (with and without spaces), and average word length.

    Args:
        text: The text to analyze.
    """
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)
    char_count = len(text)
    char_count_no_spaces = len(text.replace(" ", "").replace("\n", "").replace("\t", ""))
    avg_word_len = (
        round(sum(len(w) for w in words) / max(word_count, 1), 2) if word_count > 0 else 0.0
    )

    return {
        "word_count": word_count,
        "char_count": char_count,
        "char_count_no_spaces": char_count_no_spaces,
        "average_word_length": avg_word_len,
    }


@tool
def analyze_sentiment(text: str) -> dict:
    """Analyzes text tone to estimate sentiment polarity (positive, negative, or neutral).

    Args:
        text: The text content to analyze.
    """
    positive_words = {
        "good",
        "great",
        "excellent",
        "love",
        "wonderful",
        "amazing",
        "positive",
        "success",
        "happy",
        "best",
    }
    negative_words = {
        "bad",
        "terrible",
        "horrible",
        "hate",
        "awful",
        "negative",
        "failure",
        "sad",
        "worst",
        "poor",
    }

    tokens = [w.lower() for w in re.findall(r"\b\w+\b", text)]
    pos_count = sum(1 for w in tokens if w in positive_words)
    neg_count = sum(1 for w in tokens if w in negative_words)

    if pos_count > neg_count:
        polarity = "positive"
        score = min(1.0, 0.5 + (pos_count - neg_count) * 0.15)
    elif neg_count > pos_count:
        polarity = "negative"
        score = max(-1.0, -0.5 - (neg_count - pos_count) * 0.15)
    else:
        polarity = "neutral"
        score = 0.0

    return {
        "polarity": polarity,
        "score": round(score, 2),
        "positive_signals": pos_count,
        "negative_signals": neg_count,
    }


@tool
def calculate_reading_time(text: str, wpm: int = 200) -> dict:
    """Estimates the reading time in minutes and seconds based on words per minute (wpm).

    Args:
        text: The text to evaluate.
        wpm: Average words read per minute (default is 200).
    """
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)
    minutes = word_count / max(wpm, 1)
    total_seconds = int(round(minutes * 60))

    mins_part = total_seconds // 60
    secs_part = total_seconds % 60

    return {
        "estimated_minutes": round(minutes, 2),
        "formatted_duration": f"{mins_part} min {secs_part} sec",
        "wpm_used": wpm,
    }


SKILL_TOOLS = [count_words_and_characters, analyze_sentiment, calculate_reading_time]
