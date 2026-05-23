import json
import os
import re
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a clinical NLP assistant. Extract structured family history from the clinical text below.
Rules:
- Extract family members only, not the patient themselves
- Include the patient's children (relevant for inherited condition counseling)
- Use maternal/paternal side where you can tell
- Degree: first = parent/sibling/child, second = grandparent/aunt/uncle, third = great-grandparent/cousin
- If a condition is explicitly absent, put it in negated_conditions
- If history is unknown for someone, set history_unknown to true
- Split ambiguous references into individual members:
e.g. "both parents had diabetes" → father gets diabetes, mother gets diabetes
Never use "parents" or "siblings" as a family_member value
- If patient is adopted, set adopted=true and mark biological relatives as history_unknown
- Write short risk summaries with a level (HIGH/MODERATE/LOW/MINIMAL) and brief reason
- Return only valid JSON, no explanation, no markdown

Schema:
{
  "adopted": false,
  "family_members": [
    {
      "family_member": "father",
      "side": "paternal",
      "degree": "first",
      "living_status": "alive|deceased|unknown",
      "current_age": null,
      "age_at_death": null,
      "cause_of_death": null,
      "conditions": [
        { "condition": "hypertension", "age_at_onset": null }
      ],
      "negated_conditions": [],
      "history_unknown": false
    }
  ],
  "risk_summary": {
    "cardiovascular_risk": "HIGH - father died of MI at 62",
    "diabetes_risk": "MODERATE - father had T2DM",
    "cancer_risk": "LOW",
    "neurodegenerative_risk": "MINIMAL",
    "negated_risks": []
  }
}"""


def extract_family_history(clinical_text):
    prompt = f"Extract the complete family history from this clinical note:\n\n{clinical_text}"

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=4096,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )

    raw = resp.choices[0].message.content.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    result = json.loads(raw)

    for m in result.get("family_members", []):
        if m.get("side") == "null":
            m["side"] = None

    return result


GENERATION = {
    "son": 1, "daughter": 1,
    "father": -1, "mother": -1,
    "brother": 0, "sister": 0,
    "paternal grandfather": -2, "paternal grandmother": -2,
    "maternal grandfather": -2, "maternal grandmother": -2,
    "paternal great-grandfather": -3, "paternal great-grandmother": -3,
    "maternal great-grandfather": -3, "maternal great-grandmother": -3,
}


def build_pedigree(data):
    pedigree = {
        "patient": {"generation": 0, "role": "proband", "parents": [], "children": [], "siblings": []},
        "members": {}
    }

    for m in data.get("family_members", []):
        name = m["family_member"]
        node = {
            "generation": GENERATION.get(name),
            "side": m.get("side"),
            "degree": m.get("degree"),
            "living_status": m.get("living_status"),
            "age_at_death": m.get("age_at_death"),
            "conditions": [c["condition"] for c in m.get("conditions", [])],
            "negated_conditions": m.get("negated_conditions", []),
            "history_unknown": m.get("history_unknown", False),
            "parents": [], "children": [], "siblings": [],
        }

        if name in ("father", "mother"):
            node["children"].append("patient")
            pedigree["patient"]["parents"].append(name)
        elif name in ("son", "daughter"):
            node["parents"].append("patient")
            pedigree["patient"]["children"].append(name)
        elif name in ("brother", "sister"):
            node["siblings"].append("patient")
            pedigree["patient"]["siblings"].append(name)
        elif name == "paternal grandfather":
            node["children"].append("father")
        elif name == "paternal grandmother":
            node["children"].append("father")
        elif name == "maternal grandfather":
            node["children"].append("mother")
        elif name == "maternal grandmother":
            node["children"].append("mother")

        pedigree["members"][name] = node

    return pedigree


SNOMED = {
    "hypertension":{"code": "38341003",  "display": "Hypertensive disorder"},
    "hyperlipidemia":{"code": "55822004",  "display": "Hyperlipidemia"},
    "myocardial infarction":{"code": "22298006",  "display": "Myocardial infarction"},
    "coronary artery disease":{"code": "53741008",  "display": "Coronary arteriosclerosis"},
    "atrial fibrillation":{"code": "49436004",  "display": "Atrial fibrillation"},
    "stroke":{"code": "230690007", "display": "Cerebrovascular accident"},
    "heart failure":{"code": "84114007",  "display": "Heart failure"},
    "type 2 diabetes":{"code": "44054006",  "display": "Type 2 diabetes mellitus"},
    "type 1 diabetes":{"code": "46635009",  "display": "Type 1 diabetes mellitus"},
    "obesity":{"code": "414916001", "display": "Obesity"},
    "breast cancer":{"code": "254837009", "display": "Malignant neoplasm of breast"},
    "colon cancer":{"code": "363406005", "display": "Malignant neoplasm of colon"},
    "lung cancer":{"code": "363358000", "display": "Malignant neoplasm of lung"},
    "prostate cancer":{"code": "399068003", "display": "Malignant neoplasm of prostate"},
    "ovarian cancer":{"code": "363443007", "display": "Malignant neoplasm of ovary"},
    "colorectal cancer":{"code": "363414004", "display": "Malignant neoplasm of colorectum"},
    "alzheimer's disease":{"code": "26929004",  "display": "Alzheimer's disease"},
    "mild cognitive impairment":{"code": "386806002", "display": "Mild cognitive disorder"},
    "parkinson's disease": {"code": "49049000",  "display": "Parkinson's disease"},
    "depression":{"code": "35489007",  "display": "Depressive disorder"},
    "schizophrenia":{"code": "58214004",  "display": "Schizophrenia"},
    "osteoporosis":{"code": "64859006",  "display": "Osteoporosis"},
    "rheumatoid arthritis":{"code": "69896004",  "display": "Rheumatoid arthritis"},
    "sickle cell disease":{"code": "417357006", "display": "Sickling disorder"},
    "hemophilia":{"code": "90935002",  "display": "Hemophilia"},
    "cystic fibrosis":{"code": "190905008", "display": "Cystic fibrosis"},
    "tobacco use disorder":{"code": "56294008",  "display": "Tobacco use disorder"},
}


def snomed_lookup(condition):
    key = condition.lower().strip()
    if key in SNOMED:
        return {**SNOMED[key], "matched": "exact", "input": condition}
    for k, v in SNOMED.items():
        if k in key or key in k:
            return {**v, "matched": "partial", "input": condition}
    return {"code": None, "display": condition, "matched": "none", "input": condition}


def annotate_snomed(data):
    for m in data.get("family_members", []):
        for c in m.get("conditions", []):
            c["snomed"] = snomed_lookup(c["condition"])
    return data
SAMPLE_STANDARD = """
FAMILY HISTORY:

Father deceased at age 62 from a massive myocardial infarction. He had a history of
hypertension, hyperlipidemia, and Type 2 diabetes diagnosed in his 50s.

Mother is alive at age 84. She has a history of breast cancer (diagnosed at age 67, now
in remission), osteoporosis, and hypertension. She also has mild cognitive impairment.

Brother (age 58) had a coronary artery bypass graft (CABG) at age 55. He has Type 2
diabetes and hyperlipidemia. No history of cancer.

Sister (age 52) is healthy with no significant medical history.

Maternal grandmother died of stroke at age 75. She had long-standing atrial fibrillation
and hypertension.

Maternal grandfather died at age 80 from complications of Alzheimer's disease.

Paternal grandmother had colon cancer diagnosed at age 60. She lived to age 88.

Paternal grandfather — unknown history; died before the patient was born.

No family history of genetic disorders, sickle cell disease, or hemophilia.

Patient has two children: son (age 28) and daughter (age 25), both healthy.
"""

SAMPLE_AMBIGUOUS = """
FAMILY HISTORY:
Both parents had Type 2 diabetes. Both maternal grandparents had hypertension.
No history of cancer in any first-degree relatives.
"""

SAMPLE_ADOPTED = """
FAMILY HISTORY:
Patient is adopted. Biological family history is unknown.
Adoptive father has hypertension and hyperlipidemia, age 70, alive.
Adoptive mother is healthy, age 68, alive.
"""


if __name__ == "__main__":
    for label, text in [
        ("STANDARD", SAMPLE_STANDARD),
        ("AMBIGUOUS", SAMPLE_AMBIGUOUS),
        ("ADOPTED", SAMPLE_ADOPTED),
    ]:
        print(f"\n\nTEST: {label}\n")
        result = extract_family_history(text)
        print(json.dumps(result, indent=2))

    print(f"\n\nBONUS FEATURES\n")
    result = extract_family_history(SAMPLE_STANDARD)

    print("\n-- Pedigree --")
    print(json.dumps(build_pedigree(result), indent=2))

    print("\n-- SNOMED Annotations --")
    annotated = annotate_snomed(result)
    for m in annotated["family_members"]:
        for c in m["conditions"]:
            s = c["snomed"]
            print(f"  {c['condition']:35s} -> {s['code']} | {s['display']} [{s['matched']}]")
