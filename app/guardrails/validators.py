from app.llm.groq_client import get_llm

def validate_report(report: str, context_chunks: list[str]) -> bool:
    """Blocks empty or clearly ungrounded reports from reaching the human."""
    if not report or len(report.strip()) < 20:
        return False
    context_text = " ".join(context_chunks).lower()
    overlap_words = [w for w in report.lower().split() if w in context_text]
    return len(overlap_words) > 3  # some grounding in retrieved context


def enforce_policy_compliance(report: str, context_chunks: list[str]) -> str:
    """
    Checks the report against our actual policies. If anything in the report
    contradicts a policy, it is corrected. Otherwise the report is returned unchanged.
    """
    if not context_chunks:
        return report

    llm = get_llm()
    policies = "\n".join(context_chunks)
    prompt = f"""You are checking a risk report against our company policies below.

If any point in the report contradicts, misstates, or exceeds what our policies say,
correct that point so it matches our policies. Leave everything else exactly as it is.
Do not add any notes, tags, or explanations. Return only the corrected report text.

Our policies:
{policies}

Report:
{report}"""
    return llm.invoke(prompt).content