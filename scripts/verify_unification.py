#!/usr/bin/env python3
"""
Verify RxNorm Core Database Unification

This script verifies that the unified RxNorm core database has proper
brand-generic unification.

Usage:
    python verify_unification.py
"""

import pandas as pd

def verify_unification():
    """Verify brand-generic unification in the core database"""
    print("=== VERIFYING RXNORM CORE DATABASE UNIFICATION ===\n")
    
    # Load the unified database
    try:
        df = pd.read_csv('data/rxnorm_core_medications.csv', low_memory=False)
        print(f"✅ Loaded database: {len(df):,} entries")
    except FileNotFoundError:
        print("❌ Database file not found: data/rxnorm_core_medications.csv")
        print("Please run create_unified_rxnorm_core.py first")
        return False
    
    # Test key brand-generic pairs
    test_cases = [
        ('Tylenol', 'acetaminophen'),
        ('Advil', 'ibuprofen'),
        ('Motrin', 'ibuprofen'),
        ('Aleve', 'naproxen'),
        ('Nexium', 'esomeprazole'),
        ('Prilosec', 'omeprazole'),
        ('Lipitor', 'atorvastatin'),
        ('Crestor', 'rosuvastatin'),
        ('Prozac', 'fluoxetine'),
        ('Zoloft', 'sertraline'),
        ('Xanax', 'alprazolam'),
        ('Ativan', 'lorazepam'),
        ('Ambien', 'zolpidem'),
        ('Synthroid', 'levothyroxine'),
        ('Glucophage', 'metformin'),
        ('Zyrtec', 'cetirizine'),
        ('Claritin', 'loratadine'),
        ('Plavix', 'clopidogrel'),
        ('Eliquis', 'apixaban'),
        ('Mestinon', 'pyridostigmine')
    ]
    
    print("Verifying key brand-generic unifications:\n")
    
    unified_count = 0
    brands_df = df[df['preferred_term_type'] == 'BN']
    generics_df = df[df['preferred_term_type'].isin(['IN', 'PT'])]
    
    for brand, generic in test_cases:
        brand_matches = brands_df[brands_df['DrugName'].str.contains(brand, case=False, na=False)]
        generic_matches = generics_df[generics_df['DrugName'].str.contains(generic, case=False, na=False)]
        
        if len(brand_matches) > 0 and len(generic_matches) > 0:
            brand_rxcui = str(brand_matches.iloc[0]['primary_RXCUI'])
            generic_rxcui = str(generic_matches.iloc[0]['primary_RXCUI'])
            unified = brand_rxcui == generic_rxcui
            
            if unified:
                unified_count += 1
                status = '✅'
                # Show unified entries
                unified_entries = df[df['primary_RXCUI'] == brand_rxcui]
                entry_count = len(unified_entries)
            else:
                status = '❌'
                entry_count = 0
            
            print(f"  {status} {brand:12} = {generic:15} (RXCUI: {brand_rxcui}) [{entry_count} entries]")
        else:
            print(f"  ❓ {brand:12} = {generic:15} (One or both not found)")
    
    success_rate = (unified_count / len(test_cases)) * 100
    print(f"\nUnification Success Rate: {unified_count}/{len(test_cases)} = {success_rate:.1f}%")
    
    # Database statistics
    rxcui_counts = df['primary_RXCUI'].value_counts()
    unified_groups = len(rxcui_counts[rxcui_counts > 1])
    total_in_unified = rxcui_counts[rxcui_counts > 1].sum()
    
    print(f"\n=== DATABASE STATISTICS ===")
    print(f"Total entries: {len(df):,}")
    print(f"Unique RXCUIs: {len(rxcui_counts):,}")
    print(f"Unified groups: {unified_groups:,}")
    print(f"Entries in unified groups: {total_in_unified:,}")
    print(f"Unification coverage: {(total_in_unified / len(df) * 100):.1f}%")
    
    # Show examples of large unified groups
    print(f"\n=== EXAMPLES OF SUCCESSFUL UNIFICATIONS ===")
    large_groups = rxcui_counts[rxcui_counts >= 5].head(5)
    
    for rxcui, count in large_groups.items():
        entries = df[df['primary_RXCUI'] == rxcui]
        
        brands = entries[entries['preferred_term_type'] == 'BN']['DrugName'].tolist()
        generics = entries[entries['preferred_term_type'].isin(['IN', 'PT'])]['DrugName'].tolist()
        
        print(f"\nRXCUI {rxcui} ({count} entries):")
        if brands:
            print(f"  Brands: {', '.join(brands[:3])}{'...' if len(brands) > 3 else ''}")
        if generics:
            print(f"  Generics: {', '.join(generics[:2])}{'...' if len(generics) > 2 else ''}")
    
    # Overall assessment
    print(f"\n=== VERIFICATION RESULTS ===")
    if success_rate >= 90:
        print(f"🎉 EXCELLENT: {success_rate:.1f}% unification success rate")
        print(f"   Brand-generic unification is working excellently!")
    elif success_rate >= 70:
        print(f"✅ GOOD: {success_rate:.1f}% unification success rate")
        print(f"   Brand-generic unification is working well")
    else:
        print(f"⚠️ NEEDS IMPROVEMENT: {success_rate:.1f}% unification success rate")
        print(f"   Additional mappings may be needed")
    
    return success_rate >= 70

if __name__ == "__main__":
    success = verify_unification()
    exit(0 if success else 1)