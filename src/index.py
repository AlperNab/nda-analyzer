#!/usr/bin/env python3
"""
nda-analyzer — upload any NDA → risk score, one-sided clauses flagged,
plain-English summary, suggested redlines, negotiation talking points
"""
import anthropic, base64, json, re, sys
from pathlib import Path

SYSTEM = """You are a senior IP and contracts attorney who reviews NDAs daily.
Analyze this NDA and return a complete risk assessment.

Return ONLY valid JSON — no markdown, no explanation.

{
  "nda_type": "mutual|one-way|unknown",
  "disclosing_party": "name or 'Party A'",
  "receiving_party": "name or 'Party B'",
  "effective_date": "YYYY-MM-DD or null",
  "term_years": number_or_null,
  "governing_law": "jurisdiction or null",
  "risk_score": number_0_to_100,
  "risk_level": "low|medium|high|critical",
  "summary": "3 sentence plain-English summary of what you're agreeing to",
  "issues": [
    {
      "clause": "quoted text under 60 words",
      "issue": "what's wrong with this",
      "severity": "critical|high|medium|low",
      "one_sided": true,
      "favors": "disclosing|receiving|neither",
      "redline_suggestion": "suggested replacement language",
      "negotiation_point": "how to raise this in negotiation"
    }
  ],
  "scope_of_confidential_info": "what counts as confidential under this NDA",
  "exceptions": ["public domain","already known","independently developed","required by law"],
  "permitted_disclosures": ["employees on need-to-know","..."],
  "residuals_clause": true_or_false,
  "residuals_explanation": "string or null",
  "injunctive_relief": true_or_false,
  "non_solicitation": true_or_false,
  "non_compete_embedded": true_or_false,
  "return_destroy_obligations": true_or_false,
  "survival_period": "string or null",
  "missing_protections": ["list of clauses you should push for"],
  "overall_verdict": "sign|negotiate|reject",
  "verdict_reason": "one sentence why",
  "confidence": 0.0
}"""

def analyze(source: str) -> dict:
    client = anthropic.Anthropic()
    path = Path(source)
    if path.exists():
        if source.endswith(".pdf"):
            data = base64.standard_b64encode(path.read_bytes()).decode("ascii")
            content = [
                {"type":"document","source":{"type":"base64","media_type":"application/pdf","data":data}},
                {"type":"text","text":"Analyze this NDA completely."}
            ]
        else:
            text = path.read_text(encoding="utf-8", errors="replace")[:50000]
            content = [{"type":"text","text":f"Analyze this NDA:\n\n{text}"}]
    else:
        content = [{"type":"text","text":f"Analyze this NDA:\n\n{source[:50000]}"}]

    resp = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=3000, system=SYSTEM,
        messages=[{"role":"user","content":content}]
    )
    raw = re.sub(r'^```(?:json)?\s*','',resp.content[0].text.strip(),flags=re.MULTILINE)
    raw = re.sub(r'\s*```$','',raw,flags=re.MULTILINE)
    return json.loads(raw)

VERDICT_ICON = {"sign":"✅","negotiate":"🤝","reject":"❌"}
RISK_ICON = {"low":"🟢","medium":"🟡","high":"🔴","critical":"💀"}
SEV_ICON = {"critical":"🚨","high":"🔴","medium":"🟠","low":"🔵"}

def print_report(r: dict):
    print(f"\n{'═'*60}")
    print(f"  NDA ANALYZER — {r.get('nda_type','?').upper()} NDA")
    print(f"  Risk: {RISK_ICON.get(r.get('risk_level','medium'),'')} {r.get('risk_score',0)}/100")
    print(f"  Verdict: {VERDICT_ICON.get(r.get('overall_verdict','negotiate'),'')} {r.get('overall_verdict','?').upper()} — {r.get('verdict_reason','')}")
    print(f"{'═'*60}")
    print(f"\n  {r.get('summary','')}")
    if r.get('governing_law'): print(f"\n  Governing law: {r['governing_law']}")
    if r.get('term_years'): print(f"  Term: {r['term_years']} years")
    print(f"  Scope: {r.get('scope_of_confidential_info','?')}")
    flags = []
    if r.get('residuals_clause'): flags.append("⚠ Residuals clause")
    if r.get('non_compete_embedded'): flags.append("⚠ Non-compete embedded")
    if r.get('non_solicitation'): flags.append("⚠ Non-solicitation")
    if flags: print(f"\n  Flags: {' | '.join(flags)}")

    issues = r.get("issues", [])
    if issues:
        print(f"\n{'─'*60}\n  ISSUES ({len(issues)})")
        for i in sorted(issues, key=lambda x: ["critical","high","medium","low"].index(x.get("severity","low"))):
            print(f"\n  {SEV_ICON.get(i.get('severity','medium'),'')} {i.get('issue','')}")
            print(f"     \"{i.get('clause','')[:80]}{'...' if len(i.get('clause',''))>80 else ''}\"")
            if i.get('redline_suggestion'): print(f"     Redline: {i['redline_suggestion'][:100]}")
            if i.get('negotiation_point'): print(f"     Negotiate: {i['negotiation_point'][:100]}")

    missing = r.get("missing_protections", [])
    if missing:
        print(f"\n{'─'*60}\n  PUSH FOR THESE")
        for m in missing: print(f"  + {m}")
    print(f"\n  Confidence: {int(r.get('confidence',0)*100)}%")
    print(f"{'═'*60}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2: print("Usage: python -m nda_analyzer <nda.txt|.pdf> [--json]"); sys.exit(0)
    r = analyze(sys.argv[1] if sys.argv[1] != "-" else sys.stdin.read())
    if "--json" in sys.argv: print(json.dumps(r, indent=2, ensure_ascii=False))
    else: print_report(r)
