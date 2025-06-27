#!/usr/bin/env python3
"""
Create an enhanced core medications file that includes brand names
but excludes dose-specific variations
"""

import pandas as pd
import re

def is_dose_specific(drug_name):
    """Check if a drug name contains dose-specific information"""
    # Patterns that indicate dose-specific entries
    dose_patterns = [
        r'\b\d+\.?\d*\s*(mg|mcg|g|ml|l|unit|iu|miu|million unit|billion unit)\b',
        r'\b\d+\.?\d*\s*%',
        r'\b\d+/\d+',  # Ratios like 5/500
        r'\b\d+\s*-\s*\d+\s*(mg|mcg|unit)',  # Ranges
        r'\bstrength\s+\d+',
        r'\b(low|high|medium)\s+dose\b',  # Keep these - they're not specific doses
    ]
    
    # Don't exclude "low dose" entries
    if 'low dose' in drug_name.lower():
        return False
    
    for pattern in dose_patterns:
        if re.search(pattern, drug_name.lower()):
            return True
    return False

def is_route_specific(drug_name):
    """Check if a drug name contains route-specific information"""
    route_patterns = [
        r'\b(oral|injection|topical|ophthalmic|otic|nasal|rectal|vaginal|sublingual|buccal|transdermal)\b',
        r'\b(tablet|capsule|solution|suspension|cream|ointment|gel|patch|suppository|drops|spray)\b',
        r'\b(iv|im|sc|subq|subcutaneous|intravenous|intramuscular)\b',
        r'\b(extended release|sustained release|delayed release|immediate release)\b',
        r'\b(er|sr|dr|ir|xl|la)\b(?:\s|$)',  # Common abbreviations
    ]
    
    for pattern in route_patterns:
        if re.search(pattern, drug_name.lower()):
            return True
    return False

def should_include_entry(row):
    """Determine if an entry should be included in enhanced core"""
    drug_name = str(row['DrugName']).lower()
    term_type = str(row['preferred_term_type'])
    
    # Always include ingredients and brand names
    if term_type in ['IN', 'BN']:
        # But still check for dose-specific brand names
        if is_dose_specific(drug_name):
            return False
        return True
    
    # For other term types, be more selective
    if term_type in ['PT', 'SY', 'PIN']:
        # Exclude if dose or route specific
        if is_dose_specific(drug_name) or is_route_specific(drug_name):
            return False
        return True
    
    # Exclude other term types
    return False

def main():
    print("Creating enhanced core medications file...")
    
    # Load the consolidated file
    print("Loading consolidated RxNorm data...")
    df = pd.read_csv('rxnorm_clinical_consolidated.csv')
    print(f"Loaded {len(df)} total entries")
    
    # Filter entries
    print("Filtering entries...")
    print(f"Original consolidated: {len(df)} entries")
    
    # Apply filtering
    mask = df.apply(should_include_entry, axis=1)
    enhanced_df = df[mask].copy()
    
    print(f"After filtering: {len(enhanced_df)} entries")
    
    # Show term type distribution
    print("\nTerm type distribution:")
    term_counts = enhanced_df['preferred_term_type'].value_counts()
    for term_type, count in term_counts.items():
        print(f"  {term_type}: {count}")
    
    # Sort by priority (ingredients first, then brand names, then others)
    term_type_priority = {'IN': 1, 'BN': 2, 'PT': 3, 'SY': 4, 'PIN': 5}
    enhanced_df['type_priority'] = enhanced_df['preferred_term_type'].map(
        lambda x: term_type_priority.get(x, 99)
    )
    enhanced_df = enhanced_df.sort_values(['type_priority', 'num_sources'], ascending=[True, False])
    enhanced_df = enhanced_df.drop('type_priority', axis=1)
    
    # Save the enhanced core file
    output_file = 'rxnorm_enhanced_core_medications.csv'
    enhanced_df.to_csv(output_file, index=False)
    print(f"\nSaved enhanced core medications to {output_file}")
    
    # Show examples of what we kept
    print("\nExamples of included brand names:")
    brand_examples = enhanced_df[enhanced_df['preferred_term_type'] == 'BN'].head(20)
    for _, row in brand_examples.iterrows():
        print(f"  {row['DrugName']}")
    
    # Show what we excluded
    excluded_df = df[~mask]
    print(f"\nExcluded {len(excluded_df)} dose/route-specific entries")
    print("Examples of excluded entries:")
    for _, row in excluded_df.head(10).iterrows():
        print(f"  {row['DrugName']} ({row['preferred_term_type']})")
    
    # Test specific drugs we care about
    print("\nChecking key medications:")
    test_drugs = ['pyridostigmine', 'mestinon', 'lexapro', 'escitalopram', 
                  'immunoglobulin', 'zyrtec', 'cetirizine', 'plavix', 'clopidogrel']
    
    for drug in test_drugs:
        matches = enhanced_df[enhanced_df['normalized_name'].str.contains(drug, na=False)]
        print(f"  {drug}: {len(matches)} matches")
        if len(matches) > 0:
            for _, match in matches.head(2).iterrows():
                print(f"    - {match['DrugName']} ({match['preferred_term_type']})")

if __name__ == "__main__":
    main()