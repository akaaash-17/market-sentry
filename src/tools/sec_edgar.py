"""
SEC EDGAR tool using edgartools for extracting official 10-K/10-Q risk disclosures.
Zero-cost, direct institutional filing access.
"""
import json
import re
import warnings
from edgar import set_identity, Company
from langchain_core.tools import tool
from config.settings import settings

set_identity(settings.SEC_IDENTITY)


def _clean_filing_text(raw_text: str) -> str:
    """Removes HTML entities, excess line breaks, and whitespace."""
    cleaned = re.sub(r'<[^>]+>', ' ', raw_text)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()


@tool
def fetch_sec_risk_disclosures(ticker: str) -> str:
    """
    Extracts Item 1A (Risk Factors) narrative from the latest official
    SEC Form 10-K filing.
    """
    try:
        company = Company(ticker.strip().upper())
        filings = company.get_filings(form="10-K")
        
        if not filings or len(filings) == 0:
            return json.dumps({
                "ticker": ticker.upper(),
                "status": "No 10-K filings found for this ticker."
            })
            
        latest_10k = filings.latest()
        filing_date = str(getattr(latest_10k, "filing_date", "Unknown"))
        
        extracted_text = ""

        # Strategy 1: Safe extraction without raising edgartools FutureWarning
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            try:
                obj = latest_10k.obj()
                if obj and hasattr(obj, "items") and "Item 1A" in obj.items:
                    item_1a_chunk = obj["Item 1A"]
                    if item_1a_chunk:
                        extracted_text = str(item_1a_chunk)
            except Exception:
                extracted_text = ""

        # Strategy 2: Text regex scanning for Item 1A body
        if len(extracted_text.strip()) < 100:
            full_text = latest_10k.text() or ""
            matches = list(re.finditer(r'(Item\s+1A[\.\:\s\-\–]+Risk\s+Factors)', full_text, re.IGNORECASE))
            
            if len(matches) > 1:
                start_pos = matches[1].start()
                body_chunk = full_text[start_pos:start_pos + 6000]
            elif len(matches) == 1:
                start_pos = matches[0].start()
                body_chunk = full_text[start_pos:start_pos + 6000]
            else:
                body_chunk = full_text[:4000]

            extracted_text = body_chunk

        cleaned = _clean_filing_text(extracted_text)
        trimmed_excerpt = cleaned[:2500]

        payload = {
            "ticker": ticker.upper(),
            "form": "10-K",
            "filing_date": filing_date,
            "risk_factors_excerpt": trimmed_excerpt if trimmed_excerpt else "Risk factor section could not be extracted."
        }

        return json.dumps(payload, indent=2)

    except Exception as e:
        return json.dumps({
            "ticker": ticker.upper(),
            "error": f"Failed to retrieve SEC disclosures: {str(e)}"
        })