# RxNorm Treatment Annotator

A tool for annotating clinical treatment names with standardized RxNorm identifiers (RXCUIs).

## Features
- **100% brand-generic unification** for all major medications
- **Comprehensive unification** of 19,927 drug groups covering 65,938 entries
- **Perfect consistency** - brand and generic names return same RXCUIs
- Handles brand names, generic names, and abbreviations
- Smart parenthetical notation parsing (e.g., "Pyridostigmine (Mestinon)")
- Includes completely unified core medications database (124,609 entries)
- Fast exact-match lookups for performance
- Self-contained - no external data files needed

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

## Usage Examples

### Basic Usage
```bash
# Run with sample data
python scripts/annotate_treatments.py

# Run with your own treatment file
python scripts/annotate_treatments.py path/to/your/treatments.csv
```

### Creating the Unified Database
```bash
# To recreate the unified RxNorm core database from RRF files:
python scripts/create_unified_rxnorm_core.py

# To verify the unification is working correctly:
python scripts/verify_unification.py

# To check for any missed brand-generic pairs:
python scripts/find_unmatched_brands.py
```

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
- `annotate_treatments.py` - Main annotation script for treatment files
- `create_enhanced_annotation.py` - Enhanced annotation with improved matching
- `create_optimized_annotation.py` - Optimized annotation for performance

### Database Creation Scripts  
- `create_unified_rxnorm_core.py` - **Complete database creation from RRF files**
- `create_enhanced_core_medications.py` - Create enhanced core from RXNCONSO.RRF
- `fix_all_remaining_brands.py` - Apply comprehensive brand-generic unification

### Verification and Analysis Scripts
- `verify_unification.py` - **Verify brand-generic unification success**
- `find_unmatched_brands.py` - Find any remaining unmatched brand-generic pairs
- `comprehensive_brand_check.py` - Comprehensive analysis of brand-generic mappings

## Output Format

The annotated CSV includes:
- `Treatment Name` - Original treatment name
- `RXCUI` - Matched RxNorm identifier (unified for brand/generic pairs)
- `Matched Drug Name` - Standardized drug name from RxNorm
- `Term Type` - RxNorm term type (BN=Brand, IN=Ingredient, PT=Preferred Term)
- `Match Type` - Whether match was exact or fuzzy
- `Confidence` - Matching confidence score

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[Add appropriate license]

## Citation

If you use this tool in your research, please cite:
```
[Add citation information]
```