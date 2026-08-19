# LGS AI Workflow Copilot

A proof-of-concept tool I built to explore how AI could help extract, classify and validate technical requirements from Light Gauge Steel (LGS) construction specifications.

The idea started from a simple observation: estimators and engineers spend a lot of time reading through construction specs looking for the same handful of things - fire ratings, acoustic performance, steel thickness, stud spacing, wall heights - and a lot of that reading is repetitive. This project looks at whether document processing, NLP and a fine-tuned Transformer model could speed that up, while still keeping a human in charge of the final decision.

**Note:** this is an independent portfolio project built on synthetic data. It's not affiliated with or built from any real DryWall Steel Sections Ltd (DWSS) or University of Wolverhampton system, and it hasn't been validated for real engineering use. Any resemblance to a real spec is coincidental - I made up the example numbers myself.

---

## Why I built this

Construction specs are full of information that matters but isn't always easy to find quickly - fire resistance, acoustic requirements, material thickness, spacing, height constraints, and so on. Some of it is also just missing or vague, which is its own problem.

I wanted to see what an AI-assisted workflow for this would actually look like end to end - not just "run an LLM over the PDF and hope for the best", but something with actual traceability, so a domain expert can see where a value came from and decide whether to trust it.

This isn't meant to replace an engineer's judgement. It's meant to take the boring part of the job (finding and organising the information) off their plate, while leaving the actual decision-making with them.

---

## How it works

Roughly, a spec goes through this pipeline:

1. Upload a construction spec as a PDF.
2. Pull the text out of it.
3. Extract the LGS requirements that show up.
4. Keep track of exactly where each value came from (page + sentence).
5. Run a fine-tuned DistilBERT model over the requirement sentences to classify them.
6. Let a human reviewer approve, edit or reject each one.
7. Save every review decision.
8. Show it all on a dashboard so you can see how much the AI is actually being trusted vs corrected.

```
Spec PDF
   |
Text extraction (PyMuPDF)
   |
Requirement extraction
   |
Evidence / page tracking
   |
DistilBERT classification
   |
Human review (approve / edit / reject)
   |
SQLite storage
   |
Review dashboard
```

---

## What it actually does

### Reading the document

PDFs go through PyMuPDF, which keeps page-level text so I can later point back to where a value was found. Nothing fancy here, just reliable extraction.

### Pulling out the requirements

Right now the extractor looks for a specific set of things:

| Requirement     | Example       |
| --------------- | ------------- |
| System type     | LGS Partition |
| Fire rating     | 60 minutes    |
| Acoustic rating | 45 dB         |
| Steel thickness | 0.7 mm        |
| Stud spacing    | 600 mm        |
| Wall height     | 3.2 m         |

This part is rule-based on purpose - I wanted a deterministic baseline before adding anything more complex like an LLM-based extractor later.

### Flagging what's missing

If the spec doesn't mention something (say, steel thickness), the app just says so:

```
Missing or unclear: Steel Thickness, Stud Spacing
```

Small thing, but it's useful - it tells the reviewer exactly what still needs checking manually instead of assuming the AI covered everything.

### Evidence tracing

Every value the app pulls out is linked back to the sentence it came from, e.g.:

```
Fire Rating: 60 minutes
Page: 1
"The completed partition shall achieve a minimum 60 minute fire resistance."
```

This was the part I cared about most, honestly - an AI tool that just spits out numbers with no way to check them isn't that useful for anything with real engineering consequences.

---

## The Transformer classifier

On top of the rule-based extractor, I trained a `distilbert-base-uncased` model to classify requirement sentences into six categories:

- FIRE_REQUIREMENT
- ACOUSTIC_REQUIREMENT
- DIMENSION
- MATERIAL
- DESIGN_CONSTRAINT
- GENERAL

For example, feeding it _"The partition shall achieve 60 minutes fire resistance"_ gets classified as `FIRE_REQUIREMENT`. Once trained, the model is saved locally and loaded by the app for inference.

**Training pipeline:** synthetic labelled dataset → train/val split → tokenisation → fine-tuning → evaluation → save model → use it in the app.

Code for this lives in `training/train_classifier.py`, and the dataset it's trained on is `training/dataset.csv`.

### How well does it perform?

Weighted F1 on the held-out validation split: **~0.66**

I want to be upfront about this - it's not a great score, and it shouldn't be treated as a benchmark for anything real. The dataset is small and I made it up myself for the purpose of demonstrating the training/eval/deployment pipeline, not to build a state-of-the-art classifier. A real version of this would need a lot more data, ideally labelled by someone who actually knows construction specs, plus proper error analysis, cross-project testing and ongoing monitoring.

---

## Keeping a human in the loop

I didn't want this to be a black box that just hands over numbers as fact. So there's a review screen where someone can approve, edit or reject each extracted requirement:

```
AI predicted:   Fire Rating = 60 minutes
Reviewer set:   Fire Rating = 90 minutes
Decision:       EDITED
```

Both the original AI value and whatever the reviewer changed it to get stored, so there's a record of what the model got right and what it didn't.

---

## Review dashboard

All review decisions get saved to SQLite and shown on a Streamlit dashboard, which tracks:

- total reviews
- how many were approved / edited / rejected
- a "human intervention rate"
- review history

The intervention rate is just:

```
(Edited + Rejected) / Total Reviews x 100
```

It's a rough way of measuring how much the model is actually being trusted vs corrected, rather than only looking at F1 scores in isolation.

---

## Tech stack

- Python
- Streamlit (UI)
- PyMuPDF (PDF parsing)
- Hugging Face Transformers + Datasets
- DistilBERT
- PyTorch
- scikit-learn (evaluation)
- pandas / NumPy
- SQLite (review storage)

---

## Project layout

```
LGS-AI-Workflow-Copilot/
├── app.py
├── requirements.txt
├── README.md
├── backend/
│   ├── classifier.py
│   ├── evidence.py
│   ├── extractor.py
│   ├── pdf_parser.py
│   └── review.py
├── training/
│   ├── dataset.csv
│   └── train_classifier.py
├── database/
├── data/
├── docs/
├── models/
└── tests/
```

(Model files, local DBs, venvs and training checkpoints are gitignored.)

---

## Running it locally

Clone it:

```bash
git clone <repository-url>
cd LGS-AI-Workflow-Copilot
```

Set up a venv (Windows shown here):

```bash
py -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Train the classifier - this generates the model locally under `models/lgs-requirement-classifier/`:

```bash
python training/train_classifier.py
```

Then start the app:

```bash
streamlit run app.py
```

Open the local URL Streamlit prints in the terminal and you're in.

---

## Quick example

Feed it a spec with lines like:

```
The proposed partition system shall use 0.7 mm steel studs.
Studs shall be installed at 600 mm centres.
The partition shall achieve 60 minute fire resistance.
The minimum acoustic performance shall be 45 dB.
Maximum wall height: 3.2 m.
```

and the app extracts the structured values, ties each one to its source sentence, runs it through the classifier, and puts it in front of a reviewer.

---

## What's not here (yet)

This is a proof-of-concept, not a finished product. Some honest limitations:

- training data is synthetic and small
- extraction is rule-based, not LLM-driven
- the requirement taxonomy is limited (six categories)
- evidence matching is fairly basic
- no auth or role-based access
- SQLite only - no real database backend
- nothing here has been tested against real DWSS data or workflows

I see these less as flaws and more as the obvious next steps.

## Where I'd take this next

- Swap the rule-based extractor for a schema-constrained LLM extractor
- Add RAG over specs, guidance documents and past approved projects
- Retrain the classifier on a larger, properly labelled dataset with real error analysis
- Route low-confidence predictions straight to a human instead of showing everything
- Feed approved/corrected outputs back into future training runs
- Wrap the extraction/classification pieces in an API for other tools to call
- Containerise and deploy properly (Azure/AWS/GCP) with monitoring
- Track more operational metrics - processing time, review time, AI acceptance rate, extraction coverage, correction frequency

---

## The principle behind it

AI proposes. Evidence supports. Humans validate.

That's really the whole point of this project - for anything technical like construction specs, automation on its own isn't enough. You need traceability and a human who can actually check the work.

---

## Status

Proof of concept / portfolio project. Built to demonstrate the full loop - document processing, requirement extraction, evidence tracing, Transformer fine-tuning, model evaluation, human review, and reporting on that review - rather than to be production-ready engineering software.
