"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are stubbed below because the brief names those three. They are
stubs, not implementations: what they compute is yours, and so is how you
combine them.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics

import config


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    How much sentence length varies: standard deviation of sentence lengths (in
    words) divided by their mean, so long and short texts compare.

    Higher means lumpier, which reads as more human. Typical human prose lands
    around 0.5-0.8; evenly paced prose 0.2-0.3.

    A one-sentence text has no spread to measure. It returns 0.45, the middle of
    the range, which means "no evidence either way" and not "robotic".
    """
    lengths = [len(words(s)) for s in sentences(text)]
    lengths = [n for n in lengths if n > 0]
    if len(lengths) < 2:
        return 0.45
    return round(statistics.stdev(lengths) / statistics.mean(lengths), 4)


def type_token_ratio(text: str, window: int = 50) -> float:
    """
    Unique words over total words, 0-1. Higher means more varied vocabulary.

    A plain ratio falls as text gets longer, so this averages the ratio over a
    sliding window of 50 words. A text under 50 words uses the plain ratio.
    """
    ws = words(text)
    if not ws:
        return 0.0
    if len(ws) <= window:
        return round(len(set(ws)) / len(ws), 4)
    ratios = [
        len(set(ws[i:i + window])) / window
        for i in range(len(ws) - window + 1)
    ]
    return round(sum(ratios) / len(ratios), 4)


_UNCOMMON_MARKS = set(";:—–()!?\"“”…")


def punctuation_density(text: str) -> float:
    """
    Uncommon punctuation marks per 100 words. Higher means more varied
    punctuation, which reads as more human.

    Full stops and commas are left out on purpose: nearly everyone uses them.
    Semicolons, dashes, brackets, quotes and exclamation marks vary far more
    between writers.
    """
    n = len(words(text))
    if n == 0:
        return 0.0
    marks = sum(1 for ch in text if ch in _UNCOMMON_MARKS)
    return round(100 * marks / n, 4)


def _ai_ness(value: float, human_end: float, ai_end: float) -> float:
    """Map a raw measure onto 0 (human-ish end) to 1 (AI-ish end), clamped."""
    t = (value - human_end) / (ai_end - human_end)
    return min(max(t, 0.0), 1.0)


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    The style signal as a 0-1 score. **Higher means more likely AI.**

    Each measure is flipped and scaled to 0-1 "AI-ness" using the ranges in
    config.py, then the three are averaged equally:

      sentence_length_spread   low spread  -> AI-ish
      type_token_ratio         low variety -> AI-ish
      punctuation_density      few uncommon marks -> AI-ish
    """
    parts = [
        _ai_ness(sentence_length_spread(text), *config.STYLE_SPREAD_RANGE),
        _ai_ness(type_token_ratio(text), *config.STYLE_TTR_RANGE),
        _ai_ness(punctuation_density(text), *config.STYLE_PUNCT_RANGE),
    ]
    return round(sum(parts) / len(parts), 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
    print("\nAll zeros? These are stubs — Milestone 4 is where you build them.")
