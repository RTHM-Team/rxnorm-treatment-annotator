# RxNorm Treatment Annotator

A tool for annotating clinical treatment names with standardized RxNorm identifiers (RXCUIs).

## Features
- **100% brand-generic unification** for all major medications
- **Comprehensive unification** of 19,927 drug groups covering 65,938 entries
- **Perfect consistency** - brand and generic names return same RXCUIs
- **Supplements support** - integrate with Cerbo EHR supplements database
- **Dual annotation** - matches both medications (RxNorm) and supplements
- Handles brand names, generic names, and abbreviations
- Smart parenthetical notation parsing (e.g., "Pyridostigmine (Mestinon)")
- Includes completely unified core medications database (124,609 entries)
- Fast exact-match lookups for performance
- Self-contained - no external data files needed for basic use

## Quick Start

```bash
# Clone the repository
git clone https://github.com/RTHM_Team/rxnorm-treatment-annotator.git
cd rxnorm-treatment-annotator

# Install dependencies
pip install -r requirements.txt

# Run annotation with sample data
python scripts/create_enhanced_annotation.py
```

## Performance

The included completely unified core medications database achieves **100% brand-generic consistency** by:
- **Unified RXCUIs** - Brand and generic names map to same identifiers
- **Complete coverage** - All major medications (Tylenol=Acetaminophen, Advil=Ibuprofen, etc.)
- **19,927 unified drug groups** covering 65,938 entries (52.9% database coverage)
- **Key unifications**:
  - Pain: Tylenol=Acetaminophen, Advil/Motrin=Ibuprofen, Aleve=Naproxen
  - Cardiovascular: Lipitor=Atorvastatin, Plavix=Clopidogrel, Eliquis=Apixaban
  - Mental Health: Prozac=Fluoxetine, Xanax=Alprazolam, Ambien=Zolpidem
  - GI: Nexium/Prilosec=Esomeprazole
  - And many more...

## Data Files

### Included in Repository
- `data/rxnorm_core_medications.csv` - Completely unified core medications database (124,609 entries, ~40MB)
- `examples/sample_treatments.csv` - Sample treatment input
- `examples/sample_output.csv` - Sample annotated output

The repository is **self-contained** - no additional data files needed!

### Database Statistics
- **Total entries**: 124,609 RxNorm medications
- **Unified groups**: 19,927 drug groups
- **Entries in unified groups**: 65,938 (52.9% coverage)
- **Brand-generic unification**: 100% for major medications
- **Production ready**: Tested and verified

## Data Sources

### Included Data
- **rxnorm_core_medications.csv** - Completely unified core database (40MB)
- **Ready to use** - No additional downloads required for annotation

### Original RxNorm Data (Not Included)
- **RxNorm RRF files** not included due to:
  - Size: 1.2GB total (exceeds GitHub limits)
  - Licensing: NLM/NIH specific redistribution terms
  - Updates: Monthly releases require constant updates
- **Download from**: https://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html
- **Only needed for**: Recreating database from scratch

### Why This Approach?
✅ **Repository stays lightweight** (manageable size)  
✅ **Respects RxNorm licensing** (proper attribution)  
✅ **Self-contained for users** (includes final database)  
✅ **Reproducible for developers** (includes all scripts)

## Usage Examples

### Basic Usage
```bash
# Medications only (RxNorm database)
python scripts/annotate_treatments.py

# Comprehensive annotation (medications + supplements)
python scripts/annotate_treatments_comprehensive.py

# Run with your own treatment file
python scripts/annotate_treatments_comprehensive.py path/to/your/treatments.csv
```

### Supplements Integration
```bash
# 1. Fetch supplements from Cerbo EHR
export CERBO_USERNAME='your_username'
export CERBO_PASSWORD='your_password'
python scripts/fetch_supplements_from_cerbo.py

# 2. Run comprehensive annotation
python scripts/annotate_treatments_comprehensive.py
```

### Creating the Unified Database

**Prerequisites**: Download RxNorm RRF files from NLM:
1. Visit: https://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html  
2. Download RxNorm Full Monthly Release
3. Extract `RXNCONSO.RRF` and `RXNREL.RRF` to `rrf/` directory

```bash
# To recreate the unified RxNorm core database from RRF files:
python scripts/create_unified_rxnorm_core.py

# To verify the unification is working correctly:
python scripts/verify_unification.py

# To check for any missed brand-generic pairs:
python scripts/find_unmatched_brands.py
```

**Note**: The repository includes the final unified database, so downloading RRF files is only needed if you want to recreate the database from scratch.

### Custom Input File
```python
# Edit the script to point to your treatment file
# Look for: treatment_dictionary_analysis_clean.csv
```

## Brand-Generic Unification

This tool solves the critical problem of **inconsistent drug identification** where brand names and generic names had different RXCUIs. Now they're unified:

### Examples of Unified Medications
```
Tylenol + acetaminophen       → RXCUI: 161
Advil + Motrin + ibuprofen    → RXCUI: 643349  
Prozac + fluoxetine           → RXCUI: 227224
Lipitor + atorvastatin        → RXCUI: 83366
Nexium + Prilosec + esomeprazole → RXCUI: 1435522
```

Whether you search for "Advil" or "ibuprofen", you get the same RXCUI and consistent results!

## Comprehensive Treatment Annotation

The system now supports **dual annotation** covering both medications and supplements:

### Two-Tier Matching Strategy
1. **First**: Check RxNorm medications database (124,609 entries)
   - Medications, drugs, prescriptions
   - Unified brand-generic pairs
   - Standard RXCUIs

2. **Second**: Check supplements database (if available)
   - Vitamins, minerals, herbs, probiotics
   - Cerbo EHR integration
   - Supplement-specific identifiers

### Example Comprehensive Results
```
Tylenol          → RxNorm RXCUI: 161 (medication)
Vitamin D3       → Supplement ID: 1234 (supplement)  
Ibuprofen        → RxNorm RXCUI: 643349 (medication)
Probiotics       → Supplement ID: 5678 (supplement)
```

## How It Works

1. **Loads unified RxNorm database** - Completely unified core medications with brand-generic consistency
2. **Normalizes treatment names** - Handles variations in spacing, punctuation, case
3. **Extracts drug names** - Removes dosages, routes, formulations
4. **Handles special cases**:
   - Parenthetical notations: "Generic (Brand)" → tries both
   - Abbreviations: "NAC" → "acetylcysteine"
   - Complex names: "Low Dose Naltrexone" → "naltrexone"
5. **Returns unified RXCUIs** - Brand and generic names map to same identifiers
6. **Outputs annotated CSV** with RXCUIs and match details

## Available Scripts

### Core Scripts
- `annotate_treatments.py` - Main annotation script for treatment files (RxNorm only)
- `annotate_treatments_comprehensive.py` - **Comprehensive annotation (RxNorm + supplements)**
- `create_enhanced_annotation.py` - Enhanced annotation with improved matching
- `create_optimized_annotation.py` - Optimized annotation for performance

### Supplements Integration Scripts
- `fetch_supplements_from_cerbo.py` - **Fetch supplements from Cerbo EHR API**

### Database Creation Scripts  
- `create_unified_rxnorm_core.py` - **Complete database creation from RRF files**
- `create_enhanced_core_medications.py` - Create enhanced core from RXNCONSO.RRF
- `fix_all_remaining_brands.py` - Apply comprehensive brand-generic unification

### Verification and Analysis Scripts
- `verify_unification.py` - **Verify brand-generic unification success**
- `find_unmatched_brands.py` - Find any remaining unmatched brand-generic pairs
- `comprehensive_brand_check.py` - Comprehensive analysis of brand-generic mappings

## Output Format

### Basic Annotation (RxNorm only)
- `Treatment Name` - Original treatment name
- `RXCUI` - Matched RxNorm identifier (unified for brand/generic pairs)
- `Matched Drug Name` - Standardized drug name from RxNorm
- `Term Type` - RxNorm term type (BN=Brand, IN=Ingredient, PT=Preferred Term)
- `Match Type` - Whether match was exact or fuzzy
- `Confidence` - Matching confidence score

### Comprehensive Annotation (RxNorm + Supplements)
- `treatment_name` - Original treatment name
- `match_source` - Source of match: 'rxnorm', 'supplements', or 'no_match'
- `match_type` - Whether match was 'exact', 'fuzzy', or 'no_match'
- `confidence` - Matching confidence score (0-1)
- `matched_name` - Standardized name from database
- `identifier` - RXCUI (medications) or supplement ID (supplements)
- `category` - Term type (medications) or supplement class (supplements)
- `additional_info` - Extra details about the match

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[Add appropriate license]

## Citation

If you use this tool in your research, please cite:
```
[Add citation information]
```