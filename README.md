# nda-analyzer

> **Any NDA → risk score, one-sided clauses flagged, suggested redlines, negotiation talking points.** Sign, negotiate, or reject in seconds. Works on mutual and one-way NDAs.

[![PyPI](https://img.shields.io/pypi/v/nda-analyzer?style=flat)](https://pypi.org/project/nda-analyzer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Quickstart

```bash
pip install nda-analyzer
python -m nda_analyzer nda.pdf
python -m nda_analyzer contract.txt --json
```

## Example output

```
  NDA ANALYZER — ONE-WAY NDA
  Risk: 🔴 78/100
  Verdict: 🤝 NEGOTIATE — Residuals clause lets them use your ideas

  You're agreeing to keep their information confidential for 3 years,
  cannot work with direct competitors for 12 months after, and all IP
  created during the engagement becomes their property.

  🚨 RESIDUALS CLAUSE
     "The receiving party may use residual information retained in
      unaided memory of authorized persons..."
     Redline: Remove residuals clause entirely or limit to general skills

  PUSH FOR THESE
  + Mutual confidentiality (currently one-way)
  + Cap on injunctive relief
  + Explicit carve-out for pre-existing IP
```

## License
MIT © [Alper Nabil Gabra Zakher](https://github.com/AlperNab)
