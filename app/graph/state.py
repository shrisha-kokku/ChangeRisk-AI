from typing import TypedDict, List, Optional, Dict

class ChangeRiskState(TypedDict):
    change_request: str                     # what the developer typed in
    retrieved_context: List[str]            # relevant chunks pulled from codebase/docs/security policy (RAG)
    next_agent: str                         # which agent the supervisor decided to call next
    security_findings: Optional[str]        # output from the security agent, if it ran
    test_impact_findings: Optional[str]     # output from the test-impact agent, if it ran
    code_findings: Optional[str]            # output from the code-search agent, if it ran
    risk_report: Optional[str]              # the final combined report shown to the developer
    approved: Optional[bool]                # human's decision at the HITL gate
    execution_log: List[Dict[str, str]]     # records every step that ran