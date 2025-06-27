#!/usr/bin/env python3
"""
Annotate treatments with RxNorm identifiers using enhanced core medications database
Achieves ~44% match rate with brand names included
"""

import pandas as pd
import re
import os
import sys

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
    
    # Special mappings
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
    
    print("RxNorm Treatment Annotator")
    print("==========================\n")
    
    # File paths
    rxnorm_file = os.path.join(repo_root, "data", "rxnorm_core_medications.csv")
    treatment_file = os.path.join(repo_root, "examples", "sample_treatments.csv")
    output_file = os.path.join(repo_root, "treatment_dictionary_annotated.csv")
    
    # Check for custom treatment file
    if len(sys.argv) > 1:
        treatment_file = sys.argv[1]
        print(f"Using custom treatment file: {treatment_file}")
    
    print("Loading RxNorm data...")
    # Load RxNorm with specific columns
    rxnorm_df = pd.read_csv(rxnorm_file, 
                            usecols=['normalized_name', 'primary_RXCUI', 'DrugName', 
                                     'sources', 'preferred_term_type', 'clean_name'])
    
    # Create lookups
    rxnorm_lookup = {}
    clean_lookup = {}
    
    for _, row in rxnorm_df.iterrows():
        # Normalized name lookup
        key = row['normalized_name']
        if key not in rxnorm_lookup:
            rxnorm_lookup[key] = {
                'RXCUI': row['primary_RXCUI'],
                'name': row['DrugName'],
                'sources': row['sources'],
                'term_type': row['preferred_term_type']
            }
        
        # Clean name lookup (if available)
        if pd.notna(row.get('clean_name')):
            clean_key = row['clean_name']
            if clean_key not in clean_lookup:
                clean_lookup[clean_key] = {
                    'RXCUI': row['primary_RXCUI'],
                    'name': row['DrugName'],
                    'sources': row['sources'],
                    'term_type': row['preferred_term_type']
                }
    
    print(f"Loaded {len(rxnorm_df)} RxNorm entries")
    print(f"Created lookup with {len(rxnorm_lookup)} unique normalized names")
    
    # Load treatment names
    print(f"\nLoading treatments from {treatment_file}...")
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
        if i % 50 == 0 and i > 0:
            print(f"  Processed {i}/{len(unique_treatments)}...")
        
        # Get all possible names to try
        names_to_try = extract_names_from_parentheses(treatment_name)
        
        result = {
            'Treatment Name': treatment_name,
            'matched': False,
            'RXCUI': '',
            'matched_name': '',
            'sources': '',
            'term_type': '',
            'match_method': '',
            'searched_terms': '|'.join(names_to_try)
        }
        
        # Try each possible name
        for search_term in names_to_try:
            # Try normalized lookup first
            if search_term in rxnorm_lookup:
                match = rxnorm_lookup[search_term]
                result['matched'] = True
                result['RXCUI'] = match['RXCUI']
                result['matched_name'] = match['name']
                result['sources'] = match['sources']
                result['term_type'] = match['term_type']
                result['match_method'] = 'normalized'
                break
            # Try clean name lookup
            elif search_term in clean_lookup:
                match = clean_lookup[search_term]
                result['matched'] = True
                result['RXCUI'] = match['RXCUI']
                result['matched_name'] = match['name']
                result['sources'] = match['sources']
                result['term_type'] = match['term_type']
                result['match_method'] = 'clean_name'
                break
        
        results.append(result)
    
    # Create DataFrame and save
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)
    
    # Print summary
    total = len(results_df)
    matched = results_df['matched'].sum()
    match_rate = matched / total * 100
    
    print(f"\n=== ANNOTATION SUMMARY ===")
    print(f"Total treatments: {total}")
    print(f"Matched: {matched} ({match_rate:.1f}%)")
    print(f"Unmatched: {total - matched} ({(total-matched)/total*100:.1f}%)")
    
    # Show match type breakdown
    if matched > 0:
        match_methods = results_df[results_df['matched']]['match_method'].value_counts()
        print(f"\nMatch methods:")
        for method, count in match_methods.items():
            print(f"  {method}: {count}")
        
        # Show term type breakdown
        term_types = results_df[results_df['matched']]['term_type'].value_counts()
        print(f"\nTerm types matched:")
        for term_type, count in term_types.items():
            print(f"  {term_type}: {count}")
    
    # Show examples of matches
    print(f"\nExample matches:")
    matched_samples = results_df[results_df['matched']].head(10)
    for _, row in matched_samples.iterrows():
        print(f"  {row['Treatment Name']} -> {row['matched_name']} (RXCUI: {row['RXCUI']})")
    
    # Show parenthetical successes
    parenthetical_matches = results_df[
        results_df['Treatment Name'].str.contains(r'\(.*\)', regex=True) & 
        results_df['matched']
    ]
    
    if len(parenthetical_matches) > 0:
        print(f"\nParenthetical notation successes ({len(parenthetical_matches)}):")
        for _, row in parenthetical_matches.head(5).iterrows():
            print(f"  {row['Treatment Name']} -> {row['matched_name']}")
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()