# 🏥 Family History Extractor

A clinical NLP tool that extracts structured family medical history from unstructured clinical text using an LLM (Groq), with SNOMED CT code mapping and risk summarization.

## What it does

Takes a raw clinical narrative like:

> *"Father deceased at age 62 from myocardial infarction. He had hypertension and Type 2 diabetes diagnosed in his 50s..."*

And returns structured JSON with family members, their conditions, relationship degree, lineage, and a risk summary.

## Features

- Extracts family members with maternal/paternal lineage and degree of relation
- Maps conditions per family member with age at onset
- Handles negated history ("no family history of...")
- Maps conditions to SNOMED CT codes
- Generates a risk summary (cardiovascular, diabetes, cancer, neurodegenerative)
- Handles edge cases: adopted patients, unknown history, ambiguous references

## Tech Stack

- **Python** — core logic
- **Groq API** — LLM inference (fast, free tier available)
- **python-dotenv** — environment variable management

## Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/family-history-extractor.git
cd family-history-extractor

# Install dependencies
pip install groq python-dotenv

# Set up environment variables
cp .env.example .env
# Add your Groq API key to .env
```

**.env.example**
```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free Groq API key at [console.groq.com](https://console.groq.com)

## Usage

```python
from family_history_extractor import extract_family_history

clinical_text = """
Father deceased at age 62 from myocardial infarction. He had hypertension and Type 2 diabetes.
Mother is alive at age 84 with breast cancer (in remission) and osteoporosis.
"""

result = extract_family_history(clinical_text)
print(result)
```

Output is written to `family_history_output.json`.

## Sample Output

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
        { "condition": "hypertension", "age_at_onset": null },
        { "condition": "type 2 diabetes", "age_at_onset": "in his 50s" }
      ]
    }
  ],
  "risk_summary": {
    "cardiovascular_risk": "HIGH — Father died of MI at 62...",
    "diabetes_risk": "HIGH — Father and brother both have Type 2 DM."
  }
}
```

## Project Structure

```
family-history-extractor/
├── family_history_extractor.py   # Main extraction logic
├── family_history_output.json    # Sample output
├── .env.example                  # Environment variable template
├── .gitignore
└── README.md
```

---

*Built as part of a clinical NLP assignment — extraction from narrative text using prompt engineering and LLM structured output.*
