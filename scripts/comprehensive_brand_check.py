#!/usr/bin/env python3
"""
Comprehensive double-check for missed brand-generic pairs
"""
import pandas as pd
import re
from collections import defaultdict

def normalize_name(name):
    """Normalize drug name for better matching"""
    # Remove common suffixes and formulations
    name = re.sub(r'\s+(tablets?|capsules?|er|xl|xr|sr|cr|liquid|syrup|injection|cream|gel|ointment)$', '', name.lower())
    name = re.sub(r'\s+(hydrochloride|hcl|sulfate|sodium|calcium|magnesium|potassium|maleate|tartrate|succinate|citrate)$', '', name)
    name = re.sub(r'\s+(as\s+\w+)$', '', name)  # Remove "as calcium" etc
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def comprehensive_brand_check():
    """Perform comprehensive check for missed brand-generic pairs"""
    print("=== COMPREHENSIVE BRAND-GENERIC DOUBLE CHECK ===\n")
    
    df = pd.read_csv('rxnorm_completely_unified_core.csv', low_memory=False)
    
    # Get brands and potential generics
    brands = df[df['preferred_term_type'] == 'BN'].copy()
    generics = df[df['preferred_term_type'].isin(['IN', 'PT'])].copy()
    
    print(f"Analyzing {len(brands):,} brands against {len(generics):,} generics...")
    
    # Comprehensive list of known brand-generic relationships
    known_relationships = {
        # Pain/Anti-inflammatory
        'advil': ['ibuprofen'], 'motrin': ['ibuprofen'], 'nuprin': ['ibuprofen'],
        'tylenol': ['acetaminophen', 'paracetamol'], 'panadol': ['acetaminophen'],
        'aleve': ['naproxen'], 'anaprox': ['naproxen'],
        'aspirin': ['aspirin', 'acetylsalicylic acid'], 'bufferin': ['aspirin'],
        'excedrin': ['acetaminophen', 'aspirin', 'caffeine'],
        'celebrex': ['celecoxib'], 'voltaren': ['diclofenac'],
        
        # Gastrointestinal
        'nexium': ['esomeprazole'], 'prilosec': ['omeprazole'], 'prevacid': ['lansoprazole'],
        'protonix': ['pantoprazole'], 'aciphex': ['rabeprazole'],
        'zantac': ['ranitidine'], 'pepcid': ['famotidine'], 'tagamet': ['cimetidine'],
        'mylanta': ['aluminum hydroxide', 'magnesium hydroxide'], 'maalox': ['aluminum hydroxide'],
        'tums': ['calcium carbonate'], 'rolaids': ['calcium carbonate'],
        
        # Cardiovascular  
        'lipitor': ['atorvastatin'], 'crestor': ['rosuvastatin'], 'zocor': ['simvastatin'],
        'pravachol': ['pravastatin'], 'livalo': ['pitavastatin'], 'lescol': ['fluvastatin'],
        'norvasc': ['amlodipine'], 'cardizem': ['diltiazem'], 'procardia': ['nifedipine'],
        'altace': ['ramipril'], 'vasotec': ['enalapril'], 'prinivil': ['lisinopril'],
        'diovan': ['valsartan'], 'cozaar': ['losartan'], 'avapro': ['irbesartan'],
        'plavix': ['clopidogrel'], 'effient': ['prasugrel'],
        
        # Diabetes
        'glucophage': ['metformin'], 'januvia': ['sitagliptin'], 'actos': ['pioglitazone'],
        'avandia': ['rosiglitazone'], 'amaryl': ['glimepiride'], 'glucotrol': ['glipizide'],
        
        # Mental Health
        'prozac': ['fluoxetine'], 'zoloft': ['sertraline'], 'paxil': ['paroxetine'],
        'lexapro': ['escitalopram'], 'celexa': ['citalopram'], 'effexor': ['venlafaxine'],
        'cymbalta': ['duloxetine'], 'wellbutrin': ['bupropion'], 'remeron': ['mirtazapine'],
        'xanax': ['alprazolam'], 'ativan': ['lorazepam'], 'valium': ['diazepam'],
        'klonopin': ['clonazepam'], 'ambien': ['zolpidem'], 'lunesta': ['eszopiclone'],
        
        # Allergy/Respiratory
        'zyrtec': ['cetirizine'], 'claritin': ['loratadine'], 'allegra': ['fexofenadine'],
        'benadryl': ['diphenhydramine'], 'sudafed': ['pseudoephedrine'],
        'flonase': ['fluticasone'], 'nasonex': ['mometasone'],
        
        # Thyroid
        'synthroid': ['levothyroxine'], 'levoxyl': ['levothyroxine'], 'cytomel': ['liothyronine'],
        
        # ED/Urology
        'viagra': ['sildenafil'], 'cialis': ['tadalafil'], 'levitra': ['vardenafil'],
        'flomax': ['tamsulosin'], 'avodart': ['dutasteride'], 'proscar': ['finasteride'],
        
        # Blood thinners
        'coumadin': ['warfarin'], 'eliquis': ['apixaban'], 'xarelto': ['rivaroxaban'],
        
        # Antibiotics (some major ones)
        'augmentin': ['amoxicillin', 'clavulanate'], 'cipro': ['ciprofloxacin'],
        'zithromax': ['azithromycin'], 'biaxin': ['clarithromycin'],
        
        # Muscle relaxants
        'mestinon': ['pyridostigmine'], 'robaxin': ['methocarbamol']
    }
    
    missed_pairs = []
    checked_pairs = set()
    
    print("\nChecking known brand-generic relationships...")
    
    for brand_pattern, generic_patterns in known_relationships.items():
        # Find brand entries
        brand_entries = brands[brands['DrugName'].str.contains(brand_pattern, case=False, na=False)]
        
        if len(brand_entries) == 0:
            continue
            
        for _, brand_entry in brand_entries.iterrows():
            brand_rxcui = str(brand_entry['primary_RXCUI'])
            
            # Check each potential generic
            for generic_pattern in generic_patterns:
                # Find matching generics
                generic_matches = generics[generics['DrugName'].str.contains(generic_pattern, case=False, na=False)]
                
                if len(generic_matches) == 0:
                    continue
                
                # Find the best generic match (simplest name, ingredient preferred)
                best_generic = None
                for _, generic_entry in generic_matches.iterrows():
                    if generic_entry['preferred_term_type'] == 'IN':  # Prefer ingredients
                        best_generic = generic_entry
                        break
                
                if best_generic is None:
                    best_generic = generic_matches.iloc[0]  # Fall back to first match
                
                generic_rxcui = str(best_generic['primary_RXCUI'])
                
                # Check if already unified
                pair_key = (brand_rxcui, generic_rxcui)
                if pair_key in checked_pairs:
                    continue
                checked_pairs.add(pair_key)
                
                if brand_rxcui != generic_rxcui:
                    # This pair is not unified - potential miss
                    missed_pairs.append({
                        'brand_name': brand_entry['DrugName'],
                        'brand_rxcui': brand_rxcui,
                        'generic_name': best_generic['DrugName'],
                        'generic_rxcui': generic_rxcui,
                        'generic_type': best_generic['preferred_term_type'],
                        'pattern': f"{brand_pattern} -> {generic_pattern}"
                    })
    
    # Remove duplicates and sort by brand name
    unique_missed = []
    seen_brands = set()
    for pair in missed_pairs:
        if pair['brand_rxcui'] not in seen_brands:
            seen_brands.add(pair['brand_rxcui'])
            unique_missed.append(pair)
    
    unique_missed.sort(key=lambda x: x['brand_name'])
    
    print(f"\nFound {len(unique_missed)} potentially missed brand-generic pairs:")
    
    if len(unique_missed) == 0:
        print("✅ No missed pairs found - unification appears complete!")
        return []
    
    print(f"\n=== MISSED PAIRS ===")
    for i, pair in enumerate(unique_missed[:30]):
        print(f"{i+1:2d}. {pair['brand_name']} ({pair['brand_rxcui']}) → {pair['generic_name']} ({pair['generic_rxcui']})")
        print(f"    Pattern: {pair['pattern']}")
    
    if len(unique_missed) > 30:
        print(f"... and {len(unique_missed) - 30} more")
    
    # Create mapping for the most important missed pairs
    print(f"\n=== ADDITIONAL MAPPINGS NEEDED ===")
    for pair in unique_missed[:20]:
        print(f'        "{pair["brand_rxcui"]}": "{pair["generic_rxcui"]}",  # {pair["brand_name"]} -> {pair["generic_name"]}')
    
    return unique_missed

if __name__ == "__main__":
    missed_pairs = comprehensive_brand_check()
    
    if len(missed_pairs) > 0:
        print(f"\n⚠️  Found {len(missed_pairs)} additional brand-generic pairs that could be unified")
        print(f"   Consider applying these mappings for even more complete unification")
    else:
        print(f"\n🎉 COMPREHENSIVE CHECK COMPLETE - NO MISSED PAIRS FOUND!")
        print(f"   Brand-generic unification appears to be comprehensive")