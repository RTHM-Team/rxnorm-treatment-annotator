#!/usr/bin/env python3
"""
Comprehensive Treatment Annotation with RxNorm + Supplements

This script annotates treatments using both:
1. RxNorm medications database (brand-generic unified)
2. Cerbo supplements database

Usage:
    python annotate_treatments_comprehensive.py [input_file.csv]
"""

import pandas as pd
from difflib import SequenceMatcher
import re
import sys
import os

def normalize_name(name):
    """Normalize treatment name for better matching"""
    if pd.isna(name):
        return ""
    
    name = str(name).lower().strip()
    
    # Remove common patterns
    name = re.sub(r'\b(tablet|capsule|injection|cream|gel|ointment|syrup|liquid|suspension)s?\b', '', name)
    name = re.sub(r'\b\d+\s*(mg|mcg|g|ml|cc|units?|iu|meq)\b', '', name)  # Remove dosages
    name = re.sub(r'\bonce\s+daily\b|\bod\b|\bbid\b|\btid\b|\bqid\b', '', name)  # Remove frequency
    name = re.sub(r'\b(oral|topical|iv|im|sc|sublingual|rectal)\b', '', name)  # Remove routes
    name = re.sub(r'[^\w\s]', ' ', name)  # Replace punctuation with spaces
    name = re.sub(r'\s+', ' ', name).strip()  # Normalize whitespace
    
    return name

def find_best_match(treatment_name, database_df, name_column, threshold=0.6):
    """Find best matching entry in a database"""
    if not treatment_name:
        return None, 0, 'no_match'
    
    normalized_treatment = normalize_name(treatment_name)
    if not normalized_treatment:
        return None, 0, 'no_match'
    
    # Try exact match first
    exact_matches = database_df[database_df[name_column].str.lower() == treatment_name.lower()]
    if len(exact_matches) > 0:
        return exact_matches.iloc[0], 1.0, 'exact'
    
    # Try fuzzy matching
    best_match = None
    best_score = 0
    
    for _, row in database_df.iterrows():
        if pd.isna(row[name_column]):
            continue
            
        normalized_db_name = normalize_name(row[name_column])
        if not normalized_db_name:
            continue
        
        # Calculate similarity
        similarity = SequenceMatcher(None, normalized_treatment, normalized_db_name).ratio()
        
        # Boost score for exact substring matches
        if normalized_treatment in normalized_db_name or normalized_db_name in normalized_treatment:
            similarity = max(similarity, 0.8)
        
        # Check individual words
        treatment_words = set(normalized_treatment.split())
        db_words = set(normalized_db_name.split())
        if treatment_words and db_words:
            word_overlap = len(treatment_words.intersection(db_words)) / len(treatment_words.union(db_words))
            similarity = max(similarity, word_overlap * 0.9)
        
        if similarity > best_score and similarity >= threshold:
            best_score = similarity
            best_match = row
    
    if best_match is not None:
        return best_match, best_score, 'fuzzy'
    else:
        return None, 0, 'no_match'

def load_databases():
    """Load RxNorm and supplements databases"""
    databases = {}
    
    # Load RxNorm medications
    try:
        rxnorm_df = pd.read_csv('data/rxnorm_core_medications.csv', low_memory=False)
        databases['rxnorm'] = {
            'df': rxnorm_df,
            'name_column': 'DrugName',
            'id_column': 'primary_RXCUI',
            'type_column': 'preferred_term_type'
        }
        print(f"✅ Loaded RxNorm database: {len(rxnorm_df):,} medications")
    except FileNotFoundError:
        print("⚠️ RxNorm database not found: data/rxnorm_core_medications.csv")
        databases['rxnorm'] = None
    
    # Load supplements
    supplement_files = ['data/cerbo_supplements.csv', 'cerbo_supplements.csv']
    supplements_loaded = False
    
    for file_path in supplement_files:
        try:
            supplements_df = pd.read_csv(file_path, low_memory=False)
            databases['supplements'] = {
                'df': supplements_df,
                'name_column': 'name',
                'id_column': 'supplement_id',
                'type_column': 'class'
            }
            print(f"✅ Loaded supplements database: {len(supplements_df):,} supplements")
            supplements_loaded = True
            break
        except FileNotFoundError:
            continue
    
    if not supplements_loaded:
        print("⚠️ Supplements database not found. Run fetch_supplements_from_cerbo.py first")
        databases['supplements'] = None
    
    return databases

def annotate_comprehensive(treatment_df, databases):
    """Annotate treatments using both RxNorm and supplements databases"""
    
    print(f"\nAnnotating {len(treatment_df)} treatments...")
    
    annotations = []
    stats = {
        'rxnorm_exact': 0,
        'rxnorm_fuzzy': 0, 
        'supplements_exact': 0,
        'supplements_fuzzy': 0,
        'no_match': 0
    }
    
    for idx, row in treatment_df.iterrows():
        if 'Treatment Name' in row:
            treatment_name = row['Treatment Name']
        elif 'treatment' in row:
            treatment_name = row['treatment']
        else:
            treatment_name = row.iloc[0]  # Use first column
        
        annotation = {
            'treatment_name': treatment_name,
            'match_source': 'no_match',
            'match_type': 'no_match',
            'confidence': 0,
            'matched_name': '',
            'identifier': '',
            'category': '',
            'additional_info': ''
        }
        
        # Try RxNorm first (require higher confidence for fuzzy matches)
        if databases['rxnorm']:
            rxnorm_match, confidence, match_type = find_best_match(
                treatment_name, 
                databases['rxnorm']['df'], 
                databases['rxnorm']['name_column']
            )
            
            # Only accept RxNorm matches with high confidence (exact or fuzzy >= 0.85)
            if rxnorm_match is not None and (match_type == 'exact' or confidence >= 0.85):
                annotation.update({
                    'match_source': 'rxnorm',
                    'match_type': match_type,
                    'confidence': confidence,
                    'matched_name': rxnorm_match[databases['rxnorm']['name_column']],
                    'identifier': rxnorm_match[databases['rxnorm']['id_column']],
                    'category': rxnorm_match.get(databases['rxnorm']['type_column'], ''),
                    'additional_info': f"RxNorm {databases['rxnorm']['type_column']}: {rxnorm_match.get(databases['rxnorm']['type_column'], '')}"
                })
                
                if match_type == 'exact':
                    stats['rxnorm_exact'] += 1
                else:
                    stats['rxnorm_fuzzy'] += 1
                
                annotations.append(annotation)
                continue
        
        # Try supplements if no RxNorm match
        if databases['supplements']:
            supplement_match, confidence, match_type = find_best_match(
                treatment_name,
                databases['supplements']['df'],
                databases['supplements']['name_column']
            )
            
            if supplement_match is not None:
                annotation.update({
                    'match_source': 'supplements',
                    'match_type': match_type,
                    'confidence': confidence,
                    'matched_name': supplement_match[databases['supplements']['name_column']],
                    'identifier': supplement_match[databases['supplements']['id_column']],
                    'category': supplement_match.get(databases['supplements']['type_column'], ''),
                    'additional_info': f"Supplement class: {supplement_match.get(databases['supplements']['type_column'], '')}"
                })
                
                if match_type == 'exact':
                    stats['supplements_exact'] += 1
                else:
                    stats['supplements_fuzzy'] += 1
                
                annotations.append(annotation)
                continue
        
        # No match found
        stats['no_match'] += 1
        annotations.append(annotation)
        
        # Progress indicator
        if (idx + 1) % 100 == 0:
            print(f"  Processed {idx + 1:,} treatments...")
    
    return pd.DataFrame(annotations), stats

def main():
    """Main annotation function"""
    
    print("Comprehensive Treatment Annotation (RxNorm + Supplements)")
    print("=" * 60)
    
    # Load databases
    databases = load_databases()
    
    if not databases['rxnorm'] and not databases['supplements']:
        print("❌ No databases available for annotation")
        return 1
    
    # Load treatment data
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        # Default to sample treatments
        input_file = 'examples/sample_treatments.csv'
    
    try:
        treatment_df = pd.read_csv(input_file)
        print(f"✅ Loaded treatments from: {input_file}")
    except FileNotFoundError:
        print(f"❌ Treatment file not found: {input_file}")
        return 1
    
    # Remove duplicates
    original_count = len(treatment_df)
    if 'Treatment Name' in treatment_df.columns:
        treatment_df = treatment_df.drop_duplicates(subset=['Treatment Name'])
    elif 'treatment' in treatment_df.columns:
        treatment_df = treatment_df.drop_duplicates(subset=['treatment'])
    else:
        treatment_df = treatment_df.drop_duplicates()
    
    print(f"Processing {len(treatment_df)} unique treatments (removed {original_count - len(treatment_df)} duplicates)")
    
    # Perform comprehensive annotation
    results_df, stats = annotate_comprehensive(treatment_df, databases)
    
    # Calculate statistics
    total = len(results_df)
    rxnorm_matches = stats['rxnorm_exact'] + stats['rxnorm_fuzzy']
    supplement_matches = stats['supplements_exact'] + stats['supplements_fuzzy']
    total_matches = rxnorm_matches + supplement_matches
    
    print(f"\n=== COMPREHENSIVE ANNOTATION RESULTS ===")
    print(f"Total treatments: {total:,}")
    print(f"\nRxNorm Medications:")
    print(f"  Exact matches: {stats['rxnorm_exact']:,} ({(stats['rxnorm_exact']/total)*100:.1f}%)")
    print(f"  Fuzzy matches: {stats['rxnorm_fuzzy']:,} ({(stats['rxnorm_fuzzy']/total)*100:.1f}%)")
    print(f"  Total RxNorm: {rxnorm_matches:,} ({(rxnorm_matches/total)*100:.1f}%)")
    
    print(f"\nSupplements:")
    print(f"  Exact matches: {stats['supplements_exact']:,} ({(stats['supplements_exact']/total)*100:.1f}%)")
    print(f"  Fuzzy matches: {stats['supplements_fuzzy']:,} ({(stats['supplements_fuzzy']/total)*100:.1f}%)")
    print(f"  Total supplements: {supplement_matches:,} ({(supplement_matches/total)*100:.1f}%)")
    
    print(f"\nOverall:")
    print(f"  Total matched: {total_matches:,} ({(total_matches/total)*100:.1f}%)")
    print(f"  No matches: {stats['no_match']:,} ({(stats['no_match']/total)*100:.1f}%)")
    
    # Save results
    output_file = input_file.replace('.csv', '_comprehensive_annotated.csv')
    results_df.to_csv(output_file, index=False)
    print(f"\n✅ Saved comprehensive annotations to: {output_file}")
    
    # Show examples
    print(f"\n=== EXAMPLES OF ANNOTATIONS ===")
    
    # Show RxNorm matches
    rxnorm_examples = results_df[results_df['match_source'] == 'rxnorm'].head(5)
    if len(rxnorm_examples) > 0:
        print(f"\nRxNorm Medication Matches:")
        for _, row in rxnorm_examples.iterrows():
            print(f"  ✅ {row['treatment_name']:25} → {row['matched_name']:30} (RXCUI: {row['identifier']})")
    
    # Show supplement matches
    supplement_examples = results_df[results_df['match_source'] == 'supplements'].head(5)
    if len(supplement_examples) > 0:
        print(f"\nSupplement Matches:")
        for _, row in supplement_examples.iterrows():
            print(f"  ✅ {row['treatment_name']:25} → {row['matched_name']:30} (ID: {row['identifier']})")
    
    # Show unmatched
    unmatched_examples = results_df[results_df['match_source'] == 'no_match'].head(5)
    if len(unmatched_examples) > 0:
        print(f"\nUnmatched Treatments:")
        for _, row in unmatched_examples.iterrows():
            print(f"  ❌ {row['treatment_name']}")
    
    return 0

if __name__ == "__main__":
    exit(main())