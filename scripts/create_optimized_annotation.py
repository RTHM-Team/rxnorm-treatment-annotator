#!/usr/bin/env python3
"""
Optimized comprehensive treatment annotation with faster matching
"""

import pandas as pd
import re
from difflib import SequenceMatcher

def normalize_name(name):
    """Normalize drug/treatment names for matching"""
    if pd.isna(name):
        return ""
    normalized = str(name).lower()
    normalized = re.sub(r'[^\w\s-]', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

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
    }
    
    if normalized in mappings:
        return mappings[normalized]
    
    # Pattern cleaning
    patterns = [
        (r'\b(low\s+dose|high\s+dose|extended\s+release|immediate\s+release)\s+', ''),
        (r'\b(oral|iv|intravenous|topical|nasal|sublingual)\s+', ''),
        (r'\b(tablet|capsule|injection|spray|cream|gel|solution)\s*', ''),
        (r'^(.+?)\s*\([^)]+\).*$', r'\1'),
        (r'\b\d+\s*(mg|mcg|ml|units?)\b', ''),
        (r'\b(twice\s+daily|once\s+daily|bid|tid|qid|prn)\b', ''),
    ]
    
    result = normalized
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    result = re.sub(r'\s+', ' ', result).strip()
    return result

def main():
    print("Loading data...")
    
    # Load consolidated RxNorm with specific columns and create lookup
    print("Creating consolidated RxNorm lookup...")
    consolidated_df = pd.read_csv("rxnorm_clinical_consolidated.csv", 
                                  usecols=['normalized_name', 'primary_RXCUI', 'DrugName', 'sources', 'preferred_term_type'])
    consolidated_lookup = {}
    for _, row in consolidated_df.iterrows():
        key = row['normalized_name']
        if key not in consolidated_lookup:
            consolidated_lookup[key] = {
                'RXCUI': row['primary_RXCUI'],
                'name': row['DrugName'], 
                'sources': row['sources'],
                'term_type': row['preferred_term_type']
            }
    
    # Load core medications with specific columns and create lookup
    print("Creating core medications lookup...")
    core_df = pd.read_csv("rxnorm_core_medications.csv",
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
    print("Loading treatment names...")
    with open("treatment_dictionary_analysis_clean.csv", 'r') as f:
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
        
        normalized_treatment = normalize_name(treatment_name)
        core_drug_name = extract_core_drug_name(treatment_name)
        
        result = {
            'Treatment Name': treatment_name,
            'normalized_name': normalized_treatment,
            'core_drug_name': core_drug_name,
            'consolidated_match': False,
            'consolidated_RXCUI': '',
            'consolidated_drug_name': '',
            'consolidated_sources': '',
            'consolidated_term_type': '',
            'core_match': False,
            'core_RXCUI': '',
            'core_drug_name': '',
            'core_sources': '',
            'core_term_type': '',
            'recommended_approach': '',
            'recommended_RXCUI': '',
            'recommended_drug_name': ''
        }
        
        # Check consolidated matches
        if normalized_treatment in consolidated_lookup:
            match = consolidated_lookup[normalized_treatment]
            result['consolidated_match'] = True
            result['consolidated_RXCUI'] = match['RXCUI']
            result['consolidated_drug_name'] = match['name']
            result['consolidated_sources'] = match['sources']
            result['consolidated_term_type'] = match['term_type']
        elif core_drug_name != normalized_treatment and core_drug_name in consolidated_lookup:
            match = consolidated_lookup[core_drug_name]
            result['consolidated_match'] = True
            result['consolidated_RXCUI'] = match['RXCUI']
            result['consolidated_drug_name'] = match['name']
            result['consolidated_sources'] = match['sources']
            result['consolidated_term_type'] = match['term_type']
        
        # Check core matches
        if normalized_treatment in core_lookup:
            match = core_lookup[normalized_treatment]
            result['core_match'] = True
            result['core_RXCUI'] = match['RXCUI']
            result['core_drug_name'] = match['name']
            result['core_sources'] = match['sources']
            result['core_term_type'] = match['term_type']
        elif core_drug_name != normalized_treatment and core_drug_name in core_lookup:
            match = core_lookup[core_drug_name]
            result['core_match'] = True
            result['core_RXCUI'] = match['RXCUI']
            result['core_drug_name'] = match['name']
            result['core_sources'] = match['sources']
            result['core_term_type'] = match['term_type']
        elif normalized_treatment in core_clean_lookup:
            match = core_clean_lookup[normalized_treatment]
            result['core_match'] = True
            result['core_RXCUI'] = match['RXCUI']
            result['core_drug_name'] = match['name']
            result['core_sources'] = match['sources']
            result['core_term_type'] = match['term_type']
        elif core_drug_name != normalized_treatment and core_drug_name in core_clean_lookup:
            match = core_clean_lookup[core_drug_name]
            result['core_match'] = True
            result['core_RXCUI'] = match['RXCUI']
            result['core_drug_name'] = match['name']
            result['core_sources'] = match['sources']
            result['core_term_type'] = match['term_type']
        
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
    output_file = "treatment_dictionary_optimized_annotated.csv"
    results_df.to_csv(output_file, index=False)
    
    # Print summary
    total = len(results_df)
    consolidated_matches = results_df['consolidated_match'].sum()
    core_matches = results_df['core_match'].sum()
    any_match = (results_df['recommended_approach'] != 'none').sum()
    
    print(f"\n=== OPTIMIZED ANNOTATION SUMMARY ===")
    print(f"Total treatments: {total}")
    print(f"Consolidated matches: {consolidated_matches} ({consolidated_matches/total*100:.1f}%)")
    print(f"Core matches: {core_matches} ({core_matches/total*100:.1f}%)")
    print(f"Any match found: {any_match} ({any_match/total*100:.1f}%)")
    
    rec_counts = results_df['recommended_approach'].value_counts()
    print(f"\nRecommendations:")
    for approach, count in rec_counts.items():
        print(f"  {approach}: {count} ({count/total*100:.1f}%)")
    
    print(f"\nSample matches:")
    matched_samples = results_df[results_df['recommended_approach'] != 'none'].head(10)
    for _, row in matched_samples.iterrows():
        print(f"  {row['Treatment Name']} -> {row['recommended_drug_name']} (RXCUI: {row['recommended_RXCUI']}, {row['recommended_approach']})")
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()