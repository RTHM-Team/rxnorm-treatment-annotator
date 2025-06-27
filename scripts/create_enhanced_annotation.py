#!/usr/bin/env python3
"""
Enhanced treatment annotation with better parenthetical brand name handling
"""

import pandas as pd
import re
import os

def normalize_name(name):
    """Normalize drug/treatment names for matching"""
    if pd.isna(name):
        return ""
    normalized = str(name).lower()
    normalized = re.sub(r'[^\w\s-]', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

def extract_names_from_parentheses(treatment_name):
    """Extract both the main name and parenthetical name for separate lookup"""
    names_to_try = []
    
    # Original normalized name
    normalized = normalize_name(treatment_name)
    names_to_try.append(normalized)
    
    # Check if there are parentheses
    paren_match = re.search(r'^(.+?)\s*\(([^)]+)\)', treatment_name)
    if paren_match:
        main_part = normalize_name(paren_match.group(1))
        paren_part = normalize_name(paren_match.group(2))
        
        # Add both parts separately
        if main_part and main_part != normalized:
            names_to_try.append(main_part)
        if paren_part and paren_part != normalized:
            names_to_try.append(paren_part)
    
    # Apply core drug name extraction to the main name (without parentheses)
    main_name = re.sub(r'\s*\([^)]+\)', '', treatment_name)
    core_drug_name = extract_core_drug_name(main_name)
    if core_drug_name and core_drug_name != normalized:
        names_to_try.append(core_drug_name)
    
    return list(dict.fromkeys(names_to_try))  # Remove duplicates while preserving order

def extract_core_drug_name(treatment_name):
    """Extract core drug name from complex treatment descriptions"""
    normalized = normalize_name(treatment_name)
    
    # Special mappings first
    mappings = {
        'low dose naltrexone': 'naltrexone',
        'ldn': 'naltrexone', 
        'n acetyl cysteine': 'acetylcysteine',
        'nac': 'acetylcysteine',
        'coq10': 'coenzyme q10',
        'd ribose': 'ribose',
        'nad+': 'nicotinamide adenine dinucleotide',
        'omega 3': 'omega-3 fatty acids',
        'fish oil': 'omega-3 fatty acids',
        'b complex': 'vitamin b complex',
        'b12': 'cyanocobalamin',
        'vitamin b12': 'cyanocobalamin',
        'vitamin d3': 'cholecalciferol',
        'vitamin d': 'vitamin d',
        'vitamin c': 'vitamin c',
        'magnesium glycinate': 'magnesium',
        'magnesium citrate': 'magnesium',
        'iron bisglycinate': 'iron',
        'ferrous sulfate': 'iron',
        'ivig': 'immunoglobulin',
        'intravenous immunoglobulin': 'immunoglobulin',
    }
    
    if normalized in mappings:
        return mappings[normalized]
    
    # Pattern cleaning
    patterns = [
        (r'\b(low\s+dose|high\s+dose|extended\s+release|immediate\s+release)\s+', ''),
        (r'\b(oral|iv|intravenous|topical|nasal|sublingual)\s+', ''),
        (r'\b(tablet|capsule|injection|spray|cream|gel|solution)\s*', ''),
        (r'\b\d+\s*(mg|mcg|ml|units?)\b', ''),
        (r'\b(twice\s+daily|once\s+daily|bid|tid|qid|prn)\b', ''),
    ]
    
    result = normalized
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    result = re.sub(r'\s+', ' ', result).strip()
    return result

def main():
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    
    print("RxNorm Enhanced Treatment Annotator")
    print("===================================\n")
    
    # File paths
    consolidated_file = os.path.join(repo_root, "rxnorm_clinical_consolidated.csv")
    core_file = os.path.join(repo_root, "data", "rxnorm_core_medications.csv")
    treatment_file = os.path.join(repo_root, "examples", "sample_treatments.csv")
    output_file = os.path.join(repo_root, "treatment_dictionary_enhanced_annotated.csv")
    
    # Check if consolidated file exists
    if not os.path.exists(consolidated_file):
        print(f"WARNING: Consolidated RxNorm file not found at {consolidated_file}")
        print("Please download it according to instructions in docs/setup_instructions.md")
        print("Continuing with core medications only...\n")
        use_consolidated = False
    else:
        use_consolidated = True
    
    # Check for custom treatment file
    import sys
    if len(sys.argv) > 1:
        treatment_file = sys.argv[1]
        print(f"Using custom treatment file: {treatment_file}")
    
    print("Loading data...")
    
    # Load consolidated RxNorm if available
    consolidated_lookup = {}
    if use_consolidated:
        print("Creating consolidated RxNorm lookup...")
        consolidated_df = pd.read_csv(consolidated_file, 
                                      usecols=['normalized_name', 'primary_RXCUI', 'DrugName', 'sources', 'preferred_term_type'])
        for _, row in consolidated_df.iterrows():
            key = row['normalized_name']
            if key not in consolidated_lookup:
                consolidated_lookup[key] = {
                    'RXCUI': row['primary_RXCUI'],
                    'name': row['DrugName'], 
                    'sources': row['sources'],
                    'term_type': row['preferred_term_type']
                }
    
    # Load core medications
    print("Creating core medications lookup...")
    core_df = pd.read_csv(core_file,
                          usecols=['normalized_name', 'clean_name', 'primary_RXCUI', 'DrugName', 'sources', 'preferred_term_type'])
    core_lookup = {}
    core_clean_lookup = {}
    for _, row in core_df.iterrows():
        # Normalized name lookup
        key = row['normalized_name']
        if key not in core_lookup:
            core_lookup[key] = {
                'RXCUI': row['primary_RXCUI'],
                'name': row['DrugName'],
                'sources': row['sources'],
                'term_type': row['preferred_term_type']
            }
        
        # Clean name lookup
        clean_key = row['clean_name']
        if clean_key not in core_clean_lookup:
            core_clean_lookup[clean_key] = {
                'RXCUI': row['primary_RXCUI'],
                'name': row['DrugName'],
                'sources': row['sources'],
                'term_type': row['preferred_term_type']
            }
    
    # Load treatment names
    print(f"Loading treatment names from {treatment_file}...")
    try:
        # Try reading as CSV first
        treatment_df = pd.read_csv(treatment_file)
        treatment_names = treatment_df.iloc[:, 0].tolist()  # Use first column
    except:
        # Fall back to reading as plain text
        with open(treatment_file, 'r') as f:
            lines = f.readlines()
        treatment_names = [line.strip() for line in lines[1:] if line.strip()]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_treatments = []
    for name in treatment_names:
        normalized = name.lower()
        if normalized not in seen:
            seen.add(normalized)
            unique_treatments.append(name)
    
    print(f"Processing {len(unique_treatments)} unique treatments...")
    
    # Process treatments
    results = []
    
    for i, treatment_name in enumerate(unique_treatments):
        if i % 50 == 0:
            print(f"  Processing {i}/{len(unique_treatments)}...")
        
        # Get all possible names to try
        names_to_try = extract_names_from_parentheses(treatment_name)
        
        result = {
            'Treatment Name': treatment_name,
            'names_tried': '|'.join(names_to_try),
            'consolidated_match': False,
            'consolidated_RXCUI': '',
            'consolidated_drug_name': '',
            'consolidated_sources': '',
            'consolidated_term_type': '',
            'consolidated_matched_term': '',
            'core_match': False,
            'core_RXCUI': '',
            'core_drug_name': '',
            'core_sources': '',
            'core_term_type': '',
            'core_matched_term': '',
            'recommended_approach': '',
            'recommended_RXCUI': '',
            'recommended_drug_name': ''
        }
        
        # Try each possible name in consolidated database
        if use_consolidated:
            for search_term in names_to_try:
                if search_term in consolidated_lookup:
                    match = consolidated_lookup[search_term]
                    result['consolidated_match'] = True
                    result['consolidated_RXCUI'] = match['RXCUI']
                    result['consolidated_drug_name'] = match['name']
                    result['consolidated_sources'] = match['sources']
                    result['consolidated_term_type'] = match['term_type']
                    result['consolidated_matched_term'] = search_term
                    break  # Use first match found
        
        # Try each possible name in core database
        for search_term in names_to_try:
            if search_term in core_lookup:
                match = core_lookup[search_term]
                result['core_match'] = True
                result['core_RXCUI'] = match['RXCUI']
                result['core_drug_name'] = match['name']
                result['core_sources'] = match['sources']
                result['core_term_type'] = match['term_type']
                result['core_matched_term'] = search_term
                break
            elif search_term in core_clean_lookup:
                match = core_clean_lookup[search_term]
                result['core_match'] = True
                result['core_RXCUI'] = match['RXCUI']
                result['core_drug_name'] = match['name']
                result['core_sources'] = match['sources']
                result['core_term_type'] = match['term_type']
                result['core_matched_term'] = search_term
                break
        
        # Determine recommendation
        if result['consolidated_match'] and result['core_match']:
            result['recommended_approach'] = 'consolidated'
            result['recommended_RXCUI'] = result['consolidated_RXCUI']
            result['recommended_drug_name'] = result['consolidated_drug_name']
        elif result['consolidated_match']:
            result['recommended_approach'] = 'consolidated'
            result['recommended_RXCUI'] = result['consolidated_RXCUI']
            result['recommended_drug_name'] = result['consolidated_drug_name']
        elif result['core_match']:
            result['recommended_approach'] = 'core'
            result['recommended_RXCUI'] = result['core_RXCUI']
            result['recommended_drug_name'] = result['core_drug_name']
        else:
            result['recommended_approach'] = 'none'
        
        results.append(result)
    
    # Create DataFrame and save
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)
    
    # Print summary
    total = len(results_df)
    consolidated_matches = results_df['consolidated_match'].sum()
    core_matches = results_df['core_match'].sum()
    any_match = (results_df['recommended_approach'] != 'none').sum()
    
    print(f"\n=== ENHANCED ANNOTATION SUMMARY ===")
    print(f"Total treatments: {total}")
    if use_consolidated:
        print(f"Consolidated matches: {consolidated_matches} ({consolidated_matches/total*100:.1f}%)")
    print(f"Core matches: {core_matches} ({core_matches/total*100:.1f}%)")
    print(f"Any match found: {any_match} ({any_match/total*100:.1f}%)")
    
    rec_counts = results_df['recommended_approach'].value_counts()
    print(f"\nRecommendations:")
    for approach, count in rec_counts.items():
        print(f"  {approach}: {count} ({count/total*100:.1f}%)")
    
    # Show examples of parenthetical fixes
    parenthetical_fixes = results_df[
        results_df['Treatment Name'].str.contains(r'\(.*\)', regex=True) & 
        (results_df['recommended_approach'] != 'none')
    ]
    
    if len(parenthetical_fixes) > 0:
        print(f"\nParenthetical notation successes ({len(parenthetical_fixes)}):")
        for _, row in parenthetical_fixes.head(10).iterrows():
            print(f"  {row['Treatment Name']} -> {row['recommended_drug_name']} (matched: {row['consolidated_matched_term'] or row['core_matched_term']})")
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()