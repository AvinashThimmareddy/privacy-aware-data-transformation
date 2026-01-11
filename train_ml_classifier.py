#!/usr/bin/env python3
"""
Training Script for ML-Based Sensitivity Classifier

This script:
1. Scans table_structure/metadata/ from all YAML files
2. Extracts training data from column metadata
3. Trains a Logistic Regression model with TF-IDF features
4. Saves the trained model to models/sensitivity_classifier.pkl

Usage:
    python train_ml_classifier.py

To add more training data:
    1. Add new YAML files to table_structure/metadata/
    2. Ensure columns have descriptive names and descriptions
    3. Run this script again to retrain on all metadata files
    4. The classifier will automatically use the new model
"""

import sys
from pathlib import Path
import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from privacy_aware_transform.ml_classifier import MLClassifierTrainer
from privacy_aware_transform.metadata import MetadataLoader


def infer_sensitivity_class(column_name: str, description: str) -> str:
    """
    Infer sensitivity class from column metadata.
    
    Uses heuristics based on column name and description.
    These labels are used to train the ML model.

    Args:
        column_name: Column name
        description: Column description

    Returns:
        Sensitivity class: PII, PHI, Sensitive, or Non-Sensitive
    """
    combined_text = f"{column_name} {description}".lower()

    # PII indicators
    pii_keywords = ['first_name', 'last_name', 'name', 'email', 'phone', 'ssn', 
                    'social_security', 'passport', 'driver_license', 'address', 
                    'dob', 'date_of_birth', 'credit_card']
    for keyword in pii_keywords:
        if keyword in combined_text:
            return 'PII'

    # PHI indicators
    phi_keywords = ['diagnosis', 'medication', 'patient', 'health', 'medical_record',
                    'medical', 'clinical', 'laboratory', 'lab_result', 'procedure',
                    'surgery', 'treatment']
    for keyword in phi_keywords:
        if keyword in combined_text:
            return 'PHI'

    # Sensitive indicators
    sensitive_keywords = ['salary', 'income', 'amount', 'price', 'cost', 'revenue',
                         'bank', 'account', 'balance', 'transaction', 'zip_code',
                         'location', 'latitude', 'longitude', 'ip_address', 'device_id',
                         'password', 'token', 'credit', 'financial']
    for keyword in sensitive_keywords:
        if keyword in combined_text:
            return 'Sensitive'

    # Default
    return 'Non-Sensitive'


def extract_training_data_from_metadata(metadata_dir: str) -> list:
    """
    Extract training data from all YAML metadata files.

    Args:
        metadata_dir: Directory containing YAML metadata files

    Returns:
        List of training data dictionaries with 'features' and 'label' keys
    """
    training_data = []
    metadata_path = Path(metadata_dir)

    if not metadata_path.exists():
        print(f"Error: Metadata directory not found: {metadata_dir}")
        return training_data

    yaml_files = list(metadata_path.glob('*.yaml'))
    if not yaml_files:
        print(f"Warning: No YAML files found in {metadata_dir}")
        return training_data

    print(f"Found {len(yaml_files)} metadata files:")
    for yaml_file in sorted(yaml_files):
        print(f"  • {yaml_file.name}")

    # Load all metadata
    loader = MetadataLoader(str(metadata_path))
    all_tables = loader.load_all_tables()

    # Extract training data
    for table_name, table_meta in all_tables.items():
        print(f"\n  Processing table: {table_name}")
        for column in table_meta.columns:
            # Infer label from metadata
            label = infer_sensitivity_class(column.name, column.description)

            # Create training sample
            training_sample = {
                'features': f"{column.name} {column.description} {column.data_type}",
                'label': label,
                'column_name': column.name,
                'table_name': table_name
            }
            training_data.append(training_sample)
            print(f"    {column.name:30} → {label}")

    return training_data


def main():
    """Main training execution."""
    print("\nML Sensitivity Classifier Training Pipeline\n")

    metadata_dir = Path("table_structure/metadata")
    model_output_path = Path("models/sensitivity_classifier.pkl")

    print("Extracting training data from metadata files...")
    training_data = extract_training_data_from_metadata(str(metadata_dir))

    if not training_data:
        print("\nError: No training data extracted. Check metadata files.")
        sys.exit(1)

    print(f"\nExtracted {len(training_data)} training samples\n")
    print("Distribution:")
    from collections import Counter
    label_counts = Counter(item['label'] for item in training_data)
    for label in ['PII', 'PHI', 'Sensitive', 'Non-Sensitive']:
        count = label_counts.get(label, 0)
        if count > 0:
            percentage = (count / len(training_data)) * 100
            print(f"  {label:20} {count:3d} samples ({percentage:5.1f}%)")

    trainer = MLClassifierTrainer()
    feature_texts = [item['features'] for item in training_data]
    labels = [item['label'] for item in training_data]

    print("\nTraining model...\n")

    trainer.train(feature_texts, labels)

    print("\nSaving model...\n")

    trainer.save_model(str(model_output_path))

    print("\nTop 15 important features:\n")

    importances = trainer.get_feature_importances()
    for i, (feature, score) in enumerate(list(importances.items())[:15], 1):
        print(f"  {i:2d}. {feature:30} (importance: {score:.4f})")

    print("\nModel evaluation:\n")

    # Predict on training data to show performance
    predictions = trainer.predict_batch(feature_texts)
    correct = sum(1 for (pred, _), true_label in zip(predictions, labels) if pred == true_label)
    accuracy = (correct / len(labels)) * 100

    print(f"Training accuracy: {accuracy:.1f}% ({correct}/{len(labels)} correct)")

    # Show sample predictions
    print("\nSample predictions:")
    for i, (training_item, (pred, conf)) in enumerate(list(zip(training_data, predictions))[:5], 1):
        true_label = training_item['label']
        match = "✓" if pred == true_label else "✗"
        print(f"  {i}. {training_item['column_name']:30} | True: {true_label:15} | Pred: {pred:15} | Conf: {conf:.2f} {match}")

    print(f"\nModel saved to: {model_output_path}\n")
    print("Next steps:")
    print("  1. The classifier will automatically load this model")
    print("  2. To add more training data:")
    print("     - Add new YAML files to table_structure/metadata/")
    print("     - Run this script again: python train_ml_classifier.py")
    print("  3. To use in code:")
    print("     classifier = SensitivityClassifier(use_ml=True)")
    print()


if __name__ == '__main__':
    main()
