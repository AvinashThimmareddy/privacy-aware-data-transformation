#!/usr/bin/env python3
"""
Test script to verify ML-based classification.

Compares rule-based vs ML-based vs blended classification.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from privacy_aware_transform.metadata import MetadataLoader
from privacy_aware_transform.classifier import SensitivityClassifier


def main():
    """Main test execution."""
    print("\n" + "="*80)
    print("ML Classifier Comparison Test")
    print("="*80 + "\n")

    # Load metadata
    metadata_dir = Path('table_structure/metadata')
    loader = MetadataLoader(str(metadata_dir))
    table_meta = loader.load_table_metadata('customers.yaml')

    # Test 1: Rule-based only
    print("Test 1: Rule-Based Classification Only")
    print("-" * 80)
    classifier_rules = SensitivityClassifier(use_ml=False)
    results_rules = classifier_rules.classify_table(table_meta.columns)

    print(f"{'Column':<30} {'Class':<20} {'Confidence':<12} {'Method':<15}")
    print("-" * 80)
    for col_name, result in sorted(results_rules.items()):
        print(f"{col_name:<30} {result.sensitivity_class:<20} {result.confidence:<12.2f} {result.method:<15}")

    # Test 2: ML-based
    print("\n\nTest 2: ML-Based Classification (with trained model)")
    print("-" * 80)
    classifier_ml = SensitivityClassifier(use_ml=True)
    if classifier_ml.ml_pipeline:
        results_ml = classifier_ml.classify_table(table_meta.columns)
        
        print(f"{'Column':<30} {'Class':<20} {'Confidence':<12} {'Method':<15}")
        print("-" * 80)
        for col_name, result in sorted(results_ml.items()):
            print(f"{col_name:<30} {result.sensitivity_class:<20} {result.confidence:<12.2f} {result.method:<15}")
        
        # Compare results
        print("\n\nComparison: Rules vs ML")
        print("-" * 80)
        print(f"{'Column':<30} {'Rules':<20} {'ML':<20} {'Agree?':<10}")
        print("-" * 80)
        
        matches = 0
        for col_name in sorted(results_rules.keys()):
            rule_class = results_rules[col_name].sensitivity_class
            ml_class = results_ml[col_name].sensitivity_class
            agree = "✓" if rule_class == ml_class else "✗"
            if rule_class == ml_class:
                matches += 1
            print(f"{col_name:<30} {rule_class:<20} {ml_class:<20} {agree:<10}")
        
        print("-" * 80)
        agreement = (matches / len(results_rules)) * 100
        print(f"Agreement rate: {agreement:.1f}% ({matches}/{len(results_rules)} columns)")
        
        # Analyze differences
        print("\n\nDetailed Analysis of Differences")
        print("-" * 80)
        differences = []
        for col_name in sorted(results_rules.keys()):
            rule_result = results_rules[col_name]
            ml_result = results_ml[col_name]
            
            if rule_result.sensitivity_class != ml_result.sensitivity_class:
                differences.append({
                    'column': col_name,
                    'rule': rule_result,
                    'ml': ml_result
                })
        
        if differences:
            for diff in differences:
                print(f"\n{diff['column']}:")
                print(f"  Rule-based: {diff['rule'].sensitivity_class} (confidence {diff['rule'].confidence:.2f})")
                print(f"    Reasoning: {diff['rule'].reasoning}")
                print(f"  ML-based:   {diff['ml'].sensitivity_class} (confidence {diff['ml'].confidence:.2f})")
                print(f"    Reasoning: {diff['ml'].reasoning}")
        else:
            print("All classifications agree! ✓")
        
        # Test blending
        print("\n\nTest 3: Blended Classification (Rules + ML)")
        print("-" * 80)
        print("When rule confidence is low (< 0.8), ML predictions are considered")
        print("\nLow-confidence rule predictions that could be blended:")
        print("-" * 80)
        low_conf_cols = [
            (col_name, result) for col_name, result in results_rules.items()
            if result.confidence < 0.8
        ]
        
        if low_conf_cols:
            for col_name, result in sorted(low_conf_cols, key=lambda x: x[1].confidence):
                ml_result = results_ml[col_name]
                print(f"\n{col_name}:")
                print(f"  Rule confidence: {result.confidence:.2f} (low)")
                print(f"  ML confidence:   {ml_result.confidence:.2f}")
                if result.sensitivity_class == ml_result.sensitivity_class:
                    blended_conf = (result.confidence + ml_result.confidence) / 2
                    print(f"  Blended confidence: {blended_conf:.2f} (agreement, averaged)")
                else:
                    print(f"  Would use ML (higher confidence)" if ml_result.confidence > result.confidence else f"  Would keep rule (higher confidence)")
        else:
            print("No low-confidence rule predictions found (all >= 0.8)")
    else:
        print("ML model not loaded. Train the model first:")
        print("  python train_ml_classifier.py")

    print("\n" + "="*80)
    print("ML Classification Test Complete")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
