def validate_report(report: str, context_chunks: list[str]) -> bool:
    """Blocks empty or clearly ungrounded reports from reaching the human."""
    if not report or len(report.strip()) < 20:
        return False
    context_text = " ".join(context_chunks).lower()
    overlap_words = [w for w in report.lower().split() if w in context_text]
    return len(overlap_words) > 3  # some grounding in retrieved context