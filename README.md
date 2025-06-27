# RxNorm Treatment Annotator

A tool for annotating clinical treatment names with standardized RxNorm identifiers (RXCUIs).

## Features
- **44% match rate** on real-world treatment data
- Handles brand names, generic names, and abbreviations
- Smart parenthetical notation parsing (e.g., "Pyridostigmine (Mestinon)")
- Includes enhanced core medications database (124,609 entries) with brand names but no dose variations
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

The included enhanced core medications database achieves **44% match rate** by including:
- Generic drug names (ingredients)
- Brand names (Lexapro, Zyrtec, Plavix, etc.)
- Common synonyms and variations
- NO dose-specific entries (keeps file size manageable)

## Data Files

### Included in Repository
- `data/rxnorm_core_medications.csv` - Enhanced core medications with brand names (124,609 entries, ~40MB)
- `examples/sample_treatments.csv` - Sample treatment input
- `examples/sample_output.csv` - Sample annotated output

The repository is **self-contained** - no additional data files needed!

## Usage Examples

### Basic Usage
```bash
# Run with sample data
python scripts/annotate_treatments.py

# Run with your own treatment file
python scripts/annotate_treatments.py path/to/your/treatments.csv
```

### Custom Input File
```python
# Edit the script to point to your treatment file
# Look for: treatment_dictionary_analysis_clean.csv
```

## How It Works

1. **Loads RxNorm databases** - Core medications (included) and consolidated (download separately)
2. **Normalizes treatment names** - Handles variations in spacing, punctuation, case
3. **Extracts drug names** - Removes dosages, routes, formulations
4. **Handles special cases**:
   - Parenthetical notations: "Generic (Brand)" → tries both
   - Abbreviations: "NAC" → "acetylcysteine"
   - Complex names: "Low Dose Naltrexone" → "naltrexone"
5. **Outputs annotated CSV** with RXCUIs and match details

## Output Format

The annotated CSV includes:
- `Treatment Name` - Original treatment name
- `recommended_RXCUI` - Best matched RxNorm identifier
- `recommended_drug_name` - Standardized drug name
- `recommended_approach` - Whether match came from consolidated or core database
- Additional columns with match details

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[Add appropriate license]

## Citation

If you use this tool in your research, please cite:
```
[Add citation information]
```