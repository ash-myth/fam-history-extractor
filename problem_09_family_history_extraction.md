# Problem: Family History Extraction and Relationship Mapping

## Company Context

You are an NLP engineer at a Clinical AI company. Family medical history is a critical component of clinical risk assessment. It is typically documented in narrative form, requiring NLP to extract structured relationships between family members and their medical conditions.

## Problem Statement

**Design and implement a Python solution that extracts structured family history from clinical text using an LLM, including family member identification, their medical conditions, age at onset/death, and the patient's inherited risk factors.**

## Fields to Extract

| Field | Description | Example |
|---|---|---|
| `family_member` | Relationship to the patient | "father", "maternal grandmother" |
| `living_status` | Alive or deceased | "alive", "deceased" |
| `age_at_death` | Age at death if applicable | 62 |
| `cause_of_death` | If applicable | "myocardial infarction" |
| `conditions` | List of medical conditions | ["type 2 diabetes", "hypertension"] |
| `age_at_onset` | Age when condition was diagnosed | 55 |
| `relevance_to_patient` | Clinical relevance/risk implication | "increased cardiovascular risk" |

## Sample Input

```text
FAMILY HISTORY:

Father deceased at age 62 from a massive myocardial infarction. He had a history of
hypertension, hyperlipidemia, and Type 2 diabetes diagnosed in his 50s. He was a heavy
smoker (2 packs/day for 30 years).

Mother is alive at age 84. She has a history of breast cancer (diagnosed at age 67, now
in remission), osteoporosis, and hypertension. She also has mild cognitive impairment
and was recently started on a cholinesterase inhibitor.

Brother (age 58) had a coronary artery bypass graft (CABG) at age 55. He has Type 2
diabetes and hyperlipidemia. No history of cancer.

Sister (age 52) is healthy with no significant medical history.

Maternal grandmother died of stroke at age 75. She had long-standing atrial fibrillation
and hypertension.

Maternal grandfather died at age 80 from complications of Alzheimer's disease.

Paternal grandmother had colon cancer diagnosed at age 60. She lived to age 88.

Paternal grandfather — unknown history; died before the patient was born.

No family history of genetic disorders, sickle cell disease, or hemophilia. There is a
significant family history of cardiovascular disease and diabetes across multiple
first-degree relatives.

Patient has two children: son (age 28) and daughter (age 25), both healthy.
```

## Expected Output (JSON)

```json
{
  "family_members": [
    {
      "family_member": "father",
      "side": "paternal",
      "degree": "first",
      "living_status": "deceased",
      "age_at_death": 62,
      "cause_of_death": "myocardial infarction",
      "conditions": [
        {"condition": "hypertension", "age_at_onset": null},
        {"condition": "hyperlipidemia", "age_at_onset": null},
        {"condition": "type 2 diabetes", "age_at_onset": "in his 50s"},
        {"condition": "tobacco use disorder", "age_at_onset": null}
      ]
    },
    {
      "family_member": "mother",
      "side": "maternal",
      "degree": "first",
      "living_status": "alive",
      "current_age": 84,
      "conditions": [
        {"condition": "breast cancer", "age_at_onset": 67, "status": "in remission"},
        {"condition": "osteoporosis", "age_at_onset": null},
        {"condition": "hypertension", "age_at_onset": null},
        {"condition": "mild cognitive impairment", "age_at_onset": null}
      ]
    },
    {
      "family_member": "brother",
      "side": null,
      "degree": "first",
      "living_status": "alive",
      "current_age": 58,
      "conditions": [
        {"condition": "coronary artery disease", "age_at_onset": null, "procedures": ["CABG at age 55"]},
        {"condition": "type 2 diabetes", "age_at_onset": null},
        {"condition": "hyperlipidemia", "age_at_onset": null}
      ],
      "negated_conditions": ["cancer"]
    }
  ],
  "risk_summary": {
    "cardiovascular_risk": "HIGH — Father died of MI at 62, brother had CABG at 55, maternal grandmother had stroke. Multiple first-degree relatives with HTN and hyperlipidemia.",
    "diabetes_risk": "HIGH — Father and brother both have Type 2 DM.",
    "cancer_risk": "MODERATE — Mother had breast cancer at 67, paternal grandmother had colon cancer at 60.",
    "neurodegenerative_risk": "MODERATE — Maternal grandfather died of Alzheimer's, mother has mild cognitive impairment.",
    "negated_risks": ["genetic disorders", "sickle cell disease", "hemophilia"]
  }
}
```

## Requirements

1. **Use an LLM** for extraction and risk assessment.
2. **Write a Python function** `extract_family_history(clinical_text: str) -> dict` that:
   - Extracts all family members with their relationships.
   - Maps conditions to each family member.
   - Identifies degree of relation (first, second, third degree).
   - Distinguishes maternal vs. paternal lineage.
   - Generates a risk summary based on family history patterns.
3. **Prompt engineering**: Guide the LLM to:
   - Distinguish between patient conditions and family member conditions.
   - Handle negated family history ("no family history of...").
   - Infer relationship degree from terms like "grandmother", "uncle".
4. **Handle edge cases**:
   - Ambiguous references ("my parents both had diabetes").
   - Adopted patients with unknown family history.
   - Incomplete information ("paternal grandfather — unknown history").
   - Children of the patient (relevant for inherited condition counseling).

## Constraints

- Time limit: **30 minutes**
- Focus on relationship extraction accuracy and risk assessment quality.

## Evaluation Criteria

| Criteria | Weight |
|---|---|
| Complete family member extraction | 25% |
| Accurate condition-to-member mapping | 25% |
| Risk summary quality | 20% |
| Handling of negated and unknown history | 15% |
| Code quality and prompt design | 15% |

## Bonus Points

- Build a family tree (pedigree) data structure.
- Map conditions to SNOMED CT or OMIM codes.
- Calculate genetic risk scores based on family history patterns.
- Handle multi-generational patterns (e.g., autosomal dominant inheritance).
