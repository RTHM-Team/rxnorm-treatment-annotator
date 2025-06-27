#!/usr/bin/env python3
"""
Find brand medications that still don't match their generic equivalents
"""
import pandas as pd
import re

def find_unmatched_brands():
    """Find brand medications that still don't have same RXCUI as generics"""
    print("=== FINDING UNMATCHED BRAND MEDICATIONS ===\n")
    
    df = pd.read_csv('rxnorm_completely_unified_final.csv', low_memory=False)
    
    # Get brands and generics separately
    brands = df[df['preferred_term_type'] == 'BN'].copy()
    generics = df[df['preferred_term_type'].isin(['IN', 'PT'])].copy()
    
    print(f"Analyzing {len(brands):,} brands against {len(generics):,} generics...")
    
    # Known brand-generic relationships that should be unified
    known_pairs = {
        # OTC Pain/Anti-inflammatory
        'tylenol': 'acetaminophen',
        'advil': 'ibuprofen',
        'motrin': 'ibuprofen', 
        'aleve': 'naproxen',
        'aspirin': 'aspirin',
        'excedrin': 'acetaminophen',  # Multi-ingredient, but acetaminophen is primary
        'bufferin': 'aspirin',
        'anacin': 'aspirin',
        'goody': 'aspirin',
        
        # Gastrointestinal
        'nexium': 'esomeprazole',
        'prilosec': 'omeprazole',
        'prevacid': 'lansoprazole', 
        'protonix': 'pantoprazole',
        'aciphex': 'rabeprazole',
        'zantac': 'ranitidine',
        'pepcid': 'famotidine',
        'tagamet': 'cimetidine',
        'mylanta': 'aluminum hydroxide',
        'maalox': 'aluminum hydroxide',
        'tums': 'calcium carbonate',
        'rolaids': 'calcium carbonate',
        
        # Cardiovascular - Statins
        'lipitor': 'atorvastatin',
        'crestor': 'rosuvastatin',
        'zocor': 'simvastatin',
        'pravachol': 'pravastatin',
        'livalo': 'pitavastatin',
        'lescol': 'fluvastatin',
        
        # Cardiovascular - Blood Pressure
        'norvasc': 'amlodipine',
        'cardizem': 'diltiazem',
        'procardia': 'nifedipine',
        'altace': 'ramipril',
        'vasotec': 'enalapril',
        'prinivil': 'lisinopril',
        'zestril': 'lisinopril',
        'diovan': 'valsartan',
        'cozaar': 'losartan',
        'avapro': 'irbesartan',
        'benicar': 'olmesartan',
        
        # Cardiovascular - Blood Thinners
        'plavix': 'clopidogrel',
        'effient': 'prasugrel',
        'coumadin': 'warfarin',
        'eliquis': 'apixaban',
        'xarelto': 'rivaroxaban',
        'pradaxa': 'dabigatran',
        
        # Diabetes
        'glucophage': 'metformin',
        'januvia': 'sitagliptin',
        'actos': 'pioglitazone',
        'amaryl': 'glimepiride',
        'glucotrol': 'glipizide',
        'diabeta': 'glyburide',
        'micronase': 'glyburide',
        
        # Mental Health - Antidepressants
        'prozac': 'fluoxetine',
        'zoloft': 'sertraline',
        'paxil': 'paroxetine',
        'lexapro': 'escitalopram',
        'celexa': 'citalopram',
        'effexor': 'venlafaxine',
        'cymbalta': 'duloxetine',
        'wellbutrin': 'bupropion',
        'remeron': 'mirtazapine',
        'trazodone': 'trazodone',
        
        # Mental Health - Anxiolytics/Sleep
        'xanax': 'alprazolam',
        'ativan': 'lorazepam',
        'valium': 'diazepam',
        'klonopin': 'clonazepam',
        'ambien': 'zolpidem',
        'lunesta': 'eszopiclone',
        'sonata': 'zaleplon',
        
        # Allergy/Respiratory
        'zyrtec': 'cetirizine',
        'claritin': 'loratadine',
        'allegra': 'fexofenadine',
        'benadryl': 'diphenhydramine',
        'sudafed': 'pseudoephedrine',
        'flonase': 'fluticasone',
        'nasonex': 'mometasone',
        'rhinocort': 'budesonide',
        
        # Thyroid
        'synthroid': 'levothyroxine',
        'levoxyl': 'levothyroxine',
        'cytomel': 'liothyronine',
        'armour': 'thyroid',
        
        # ED/Urology
        'viagra': 'sildenafil',
        'cialis': 'tadalafil',
        'levitra': 'vardenafil',
        'flomax': 'tamsulosin',
        'avodart': 'dutasteride',
        'proscar': 'finasteride',
        'propecia': 'finasteride',
        
        # Antibiotics
        'amoxil': 'amoxicillin',
        'augmentin': 'amoxicillin',  # Combination, but amoxicillin is primary
        'cipro': 'ciprofloxacin',
        'levaquin': 'levofloxacin',
        'zithromax': 'azithromycin',
        'biaxin': 'clarithromycin',
        'keflex': 'cephalexin',
        
        # Muscle/Neurological
        'mestinon': 'pyridostigmine',
        'robaxin': 'methocarbamol',
        'skelaxin': 'metaxalone',
        'soma': 'carisoprodol',
        'flexeril': 'cyclobenzaprine',
    }
    
    unmatched_brands = []
    
    print("Checking known brand-generic pairs for unification status...\n")
    
    for brand_pattern, generic_pattern in known_pairs.items():
        # Find brand entries
        brand_matches = brands[brands['DrugName'].str.contains(brand_pattern, case=False, na=False)]
        
        if len(brand_matches) == 0:
            continue
            
        # Find generic entries
        generic_matches = generics[generics['DrugName'].str.contains(generic_pattern, case=False, na=False)]
        
        if len(generic_matches) == 0:
            continue
        
        # Check first brand against first generic
        brand_entry = brand_matches.iloc[0]
        generic_entry = generic_matches.iloc[0]
        
        brand_rxcui = str(brand_entry['primary_RXCUI'])
        generic_rxcui = str(generic_entry['primary_RXCUI'])
        
        if brand_rxcui != generic_rxcui:
            unmatched_brands.append({
                'brand_name': brand_entry['DrugName'],
                'brand_rxcui': brand_rxcui,
                'generic_name': generic_entry['DrugName'],
                'generic_rxcui': generic_rxcui,
                'pattern': f"{brand_pattern} -> {generic_pattern}",
                'category': get_category(brand_pattern)
            })
    
    # Sort by category and brand name
    unmatched_brands.sort(key=lambda x: (x['category'], x['brand_name']))
    
    print(f"Found {len(unmatched_brands)} unmatched brand-generic pairs:\n")
    
    if len(unmatched_brands) == 0:
        print("✅ All known brand-generic pairs are successfully unified!")
        return []
    
    # Group by category
    by_category = {}
    for item in unmatched_brands:
        category = item['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(item)
    
    for category, items in by_category.items():
        print(f"=== {category.upper()} ===")
        for i, item in enumerate(items):
            print(f"{i+1:2d}. {item['brand_name']} ({item['brand_rxcui']}) ≠ {item['generic_name']} ({item['generic_rxcui']})")
        print()
    
    # Create mapping suggestions
    print("=== SUGGESTED ADDITIONAL MAPPINGS ===")
    for item in unmatched_brands[:20]:
        print(f'        "{item["brand_rxcui"]}": "{item["generic_rxcui"]}",  # {item["brand_name"]} -> {item["generic_name"]}')
    
    if len(unmatched_brands) > 20:
        print(f"... and {len(unmatched_brands) - 20} more")
    
    return unmatched_brands

def get_category(brand_pattern):
    """Categorize brand by therapeutic area"""
    pain_meds = ['tylenol', 'advil', 'motrin', 'aleve', 'aspirin', 'excedrin', 'bufferin', 'anacin', 'goody']
    gi_meds = ['nexium', 'prilosec', 'prevacid', 'protonix', 'aciphex', 'zantac', 'pepcid', 'tagamet', 'mylanta', 'maalox', 'tums', 'rolaids']
    cardio_meds = ['lipitor', 'crestor', 'zocor', 'pravachol', 'livalo', 'lescol', 'norvasc', 'cardizem', 'procardia', 
                   'altace', 'vasotec', 'prinivil', 'zestril', 'diovan', 'cozaar', 'avapro', 'benicar',
                   'plavix', 'effient', 'coumadin', 'eliquis', 'xarelto', 'pradaxa']
    diabetes_meds = ['glucophage', 'januvia', 'actos', 'amaryl', 'glucotrol', 'diabeta', 'micronase']
    mental_health = ['prozac', 'zoloft', 'paxil', 'lexapro', 'celexa', 'effexor', 'cymbalta', 'wellbutrin', 'remeron', 'trazodone',
                    'xanax', 'ativan', 'valium', 'klonopin', 'ambien', 'lunesta', 'sonata']
    allergy_meds = ['zyrtec', 'claritin', 'allegra', 'benadryl', 'sudafed', 'flonase', 'nasonex', 'rhinocort']
    
    if brand_pattern in pain_meds:
        return "Pain/Anti-inflammatory"
    elif brand_pattern in gi_meds:
        return "Gastrointestinal"
    elif brand_pattern in cardio_meds:
        return "Cardiovascular"
    elif brand_pattern in diabetes_meds:
        return "Diabetes"
    elif brand_pattern in mental_health:
        return "Mental Health"
    elif brand_pattern in allergy_meds:
        return "Allergy/Respiratory"
    else:
        return "Other"

if __name__ == "__main__":
    unmatched_brands = find_unmatched_brands()
    
    if len(unmatched_brands) > 0:
        print(f"\n⚠️  {len(unmatched_brands)} brand medications still need unification with their generics")
        print(f"   These represent opportunities for further improvement")
    else:
        print(f"\n🎉 ALL MAJOR BRAND-GENERIC PAIRS ARE UNIFIED!")
        print(f"   No additional unification needed")