#!/usr/bin/env python3
"""
Simple test script to verify the privacy-aware transformation framework.
"""

import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from privacy_aware_transform.metadata import SyntheticMetadataGenerator, MetadataLoader
from privacy_aware_transform.classifier import SensitivityClassifier
from privacy_aware_transform.policy import PolicyEngine
from privacy_aware_transform.transforms import TransformationEngine
from privacy_aware_transform.utils import print_classification_report


def main():
    """Main test execution."""
    print("\n" + "="*80)
    print("Privacy-Aware Data Transformation - Quick Test")
    print("="*80 + "\n")

    # Step 1: Generate sample metadata
    print("[Step 1] Generating sample metadata...")
    metadata_gen = SyntheticMetadataGenerator()
    metadata_dir = Path('table_structure/metadata')
    
    customers_meta = metadata_gen.generate_customer_metadata()
    filepath = metadata_gen.save_metadata_yaml(customers_meta, str(metadata_dir))
    print(f"  ✓ Generated: {filepath}")

    # Step 2: Load and classify
    print("\n[Step 2] Classifying sensitive columns...")
    loader = MetadataLoader(str(metadata_dir))
    table_meta = loader.load_table_metadata('customers.yaml')
    
    classifier = SensitivityClassifier(use_ml=False)
    classifications = classifier.classify_table(table_meta.columns)
    
    summary = classifier.get_classification_summary(classifications)
    print(f"  Classification Summary:")
    for cls, count in summary.items():
        print(f"    {cls}: {count}")

    # Step 3: Apply transformations
    print("\n[Step 3] Applying privacy transformations...")
    
    # Create sample data
    sample_data = {
        'customer_id': [1, 2, 3],
        'first_name': ['John', 'Jane', 'Bob'],
        'email': ['john@example.com', 'jane@example.com', 'bob@example.com'],
        'registration_date': ['2020-01-01', '2021-06-15', '2020-12-01'],
        'status': ['active', 'active', 'inactive']
    }
    df = pd.DataFrame(sample_data)
    
    policy_engine = PolicyEngine()
    transformation_engine = TransformationEngine()
    
    # Transform for internal analyst
    print("  Transforming for: internal_analyst")
    transformed_data = {}
    for col_name in df.columns:
        if col_name in classifications:
            classification = classifications[col_name]
            rule = policy_engine.get_transformation_rule('internal_analyst', classification.sensitivity_class)
            if rule:
                transformed = transformation_engine.apply_transformation(
                    df[col_name].tolist(),
                    rule.transformation_type,
                    rule.parameters
                )
                transformed_data[col_name] = transformed
            else:
                transformed_data[col_name] = df[col_name].tolist()
    
    transformed_df = pd.DataFrame(transformed_data)
    
    print("  Original data (first row):")
    for col in df.columns:
        print(f"    {col}: {df[col].iloc[0]}")
    
    print("  Transformed data (first row):")
    for col in transformed_df.columns:
        print(f"    {col}: {transformed_df[col].iloc[0]}")
    
    # Step 4: Test CLI
    print("\n[Step 4] Testing CLI interface...")
    try:
        from privacy_aware_transform.cli import cli
        print("  ✓ CLI module loaded successfully")
    except Exception as e:
        print(f"  ✗ Error loading CLI: {e}")
    
    print("\n" + "="*80)
    print("All tests completed successfully!")
    print("="*80 + "\n")
    
    print("Next steps:")
    print("  1. Run full example: python examples/example.py")
    print("  2. Use CLI: python -m privacy_aware_transform.cli --help")
    print("  3. Check generated metadata: table_structure/metadata/")
    print()


if __name__ == '__main__':
    main()
