# Setup Instructions

## Prerequisites
- Python 3.7 or higher
- pip package manager
- ~100MB free disk space for the consolidated RxNorm file (optional but recommended)

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/RTHM_Team/rxnorm-treatment-annotator.git
cd rxnorm-treatment-annotator
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Download the consolidated RxNorm file** (optional but recommended for best results)

The consolidated RxNorm file (`rxnorm_clinical_consolidated.csv`) contains 283,669 entries and is too large for Git (~90MB). You'll need to obtain this file separately.

Options for getting the consolidated file:
- Request from the project maintainer
- Generate from original RxNorm RRF files (see below)
- Use the tool with core medications only (included, but lower match rate)

### Generating Consolidated RxNorm from RRF Files

If you have access to RxNorm RRF files:

1. Download RxNorm Full from [UMLS](https://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html)
2. Extract the RRF files
3. Use the conversion scripts (available in the project history)
4. Place `rxnorm_clinical_consolidated.csv` in the repository root

## Quick Test

Run with the included sample data:
```bash
python scripts/create_enhanced_annotation.py
```

This will:
- Use the included core medications database (53,645 entries)
- Process the sample treatment file in `examples/sample_treatments.csv`
- Output results to `treatment_dictionary_enhanced_annotated.csv`

## Using Your Own Data

1. **Prepare your treatment file**
   - CSV format with treatment names in the first column
   - One treatment per row
   - Header row optional

2. **Run the annotation**
```bash
python scripts/create_enhanced_annotation.py path/to/your/treatments.csv
```

## Expected Performance

| Database Used | Typical Match Rate | Notes |
|--------------|-------------------|--------|
| Core medications only | ~24% | Ingredients only, no brand names |
| Core + Consolidated | ~40% | Includes brand names and variations |

## Troubleshooting

### "Consolidated RxNorm file not found" warning
- This is expected if you haven't downloaded the large consolidated file
- The tool will still work with core medications only
- To get the best match rate, obtain the consolidated file

### Low match rates
- Check that treatments are medications (not procedures, devices, etc.)
- Review unmatched treatments - many may be non-drug interventions
- Consider adding custom mappings to the script

### Memory issues
- The consolidated file requires ~1GB RAM to process
- Use core medications only if memory is limited