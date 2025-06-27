# RxNorm Data Files

This directory contains the RxNorm reference data used for treatment annotation.

## Included Files

### rxnorm_core_medications.csv (124,609 entries)
Enhanced core medications database including both generic and brand names, but excluding:
- Dose-specific formulations (e.g., "aspirin 81 mg")
- Route-specific variations (e.g., "morphine oral")
- Complex combinations
- Brand name products

**Columns:**
- `primary_RXCUI` - Primary RxNorm Concept Unique Identifier
- `DrugName` - Original drug name from RxNorm
- `clean_name` - Cleaned/simplified drug name
- `normalized_name` - Normalized for matching (lowercase, no punctuation)
- `preferred_term_type` - Term type (IN=Ingredient, PT=Preferred Term, etc.)
- `sources` - Data sources (RXNORM, DRUGBANK, etc.)
- `num_sources` - Number of sources containing this entry
- `priority_score` - Priority for duplicate resolution

## Not Included (Too Large for Git)

### rxnorm_clinical_consolidated.csv (283,669 entries)
Full consolidated RxNorm database including:
- All brand names
- All formulations and doses
- All routes of administration
- Complete source attribution

This file is ~90MB and should be obtained separately. See setup instructions for details.

## Data Sources

The RxNorm data comes from the National Library of Medicine's RxNorm database, which aggregates drug information from multiple sources:
- RXNORM - NLM's normalized drug database
- SNOMEDCT_US - SNOMED Clinical Terms US Edition
- DRUGBANK - DrugBank drug database
- MMSL - Multum MediSource Lexicon
- GS - Gold Standard Drug Database