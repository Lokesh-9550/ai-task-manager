"""
Generative AI summarization for meeting notes.

If OPENAI_API_KEY is set, meeting notes are summarized and turned into a
short action-item list by the OpenAI API. Otherwise an extractive fallback
(sentence-ranking via word frequency, no external dependencies) keeps the
feature fully functional offline.
"""
import os
import re


def summarize_notes(notes: str) -> str:
    notes = (notes or "").strip()
    if not notes:
        return ""

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        result = _summarize_with_openai(notes, api_key)
        if result:
            return result

    return _summarize_extractive(notes)


def _summarize_with_openai(notes: str, api_key: str):
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Summarize the following meeting notes in 2-3 "
                        "sentences, then list concrete action items as a "
                        "bulleted list."
                    ),
                },
                {"role": "user", "content": notes},
            ],
            max_tokens=250,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None


def _summarize_extractive(notes: str) -> str:
    """Simple frequency-based extractive summarizer, dependency-free."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", notes) if s.strip()]
    if len(sentences) <= 2:
        summary = notes
    else:
        stopwords = {
            "the", "a", "an", "and", "or", "but", "is", "are", "was", "were",
            "to", "of", "in", "on", "for", "with", "that", "this", "it", "as",
            "we", "will", "be", "at", "by", "from", "our",
        }
        words = re.findall(r"[a-zA-Z']+", notes.lower())
        freq = {}
        for w in words:
            if w not in stopwords:
                freq[w] = freq.get(w, 0) + 1

        scored = []
        for sentence in sentences:
            sw = re.findall(r"[a-zA-Z']+", sentence.lower())
            score = sum(freq.get(w, 0) for w in sw) / (len(sw) or 1)
            scored.append((score, sentence))

        top = sorted(scored, key=lambda x: x[0], reverse=True)[:3]
        top_sentences = [s for _, s in sorted(
            [(sentences.index(s), s) for _, s in top]
        )]
        summary = " ".join(top_sentences)

    # naive action-item extraction: lines mentioning imperative-ish cues
    action_cues = ("will ", "need to ", "should ", "must ", "todo", "action:")
    action_lines = [
        s for s in sentences if any(cue in s.lower() for cue in action_cues)
    ]

    result = f"Summary: {summary}"
    if action_lines:
        result += "\n\nAction Items:\n" + "\n".join(f"- {s}" for s in action_lines[:5])
    return result
