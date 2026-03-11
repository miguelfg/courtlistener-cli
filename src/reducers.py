"""Result reducers for extracting slim subsets of API responses."""

from typing import Any, Dict, List

BASE_URL = "https://www.courtlistener.com"


def _extract_defendant(result: Dict[str, Any]) -> str:
    """Return the defendant/in-rem party name.

    Uses the last entry in ``party`` when available (len > 1),
    otherwise falls back to splitting ``caseName`` on ' v. '.
    """
    parties = result.get("party") or []
    if len(parties) > 1:
        return parties[-1]
    case_name: str = result.get("caseName", "")
    if " v. " in case_name:
        return case_name.split(" v. ", 1)[1]
    return case_name


def _extract_documents(recap_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return available documents with url, label, and date_filed."""
    docs = []
    for doc in recap_docs:
        if not doc.get("is_available"):
            continue
        raw_label: str = doc.get("description") or ""
        # Trim to first sentence or 120 chars
        first_sentence = raw_label.split(".")[0].strip()
        label = first_sentence[:120] if first_sentence else raw_label[:120]
        docs.append({
            "url": BASE_URL + doc["absolute_url"],
            "label": label,
            "date_filed": doc.get("entry_date_filed", ""),
        })
    return docs


def slim_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a single raw API result to the slim export shape."""
    recap_docs = result.get("recap_documents") or []
    return {
        "case_name": result.get("caseName", ""),
        "defendant": _extract_defendant(result),
        "date_filed": result.get("dateFiled", ""),
        "court": result.get("court", ""),
        "court_citation": result.get("court_citation_string", ""),
        "docket_number": result.get("docketNumber", ""),
        "cause": result.get("cause", ""),
        "jurisdiction": result.get("jurisdictionType", ""),
        "top_page_url": BASE_URL + result.get("docket_absolute_url", ""),
        "documents": _extract_documents(recap_docs),
    }


def slim_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply ``slim_result`` to a list of raw API results."""
    return [slim_result(r) for r in results]
