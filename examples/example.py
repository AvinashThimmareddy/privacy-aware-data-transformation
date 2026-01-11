#!/usr/bin/env python3
"""
Example script demonstrating the privacy-aware data transformation framework.

This script:
1. Generates sample metadata for customer, patient, and sales tables
2. Generates synthetic sample data (CSV)
3. Classifies sensitive columns
4. Applies privacy transformations for different consumer types
5. Saves transformed data
"""

import sys
from pathlib import Path
import pandas as pd
from faker import Faker

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from privacy_aware_transform.metadata import SyntheticMetadataGenerator
from privacy_aware_transform.classifier import SensitivityClassifier
from privacy_aware_transform.policy import PolicyEngine
from privacy_aware_transform.transforms import TransformationEngine
from privacy_aware_transform.utils import (
    save_csv_data,
    apply_transformations_to_dataframe,
    print_classification_report
)


def generate_sample_customer_data(n_rows: int = 5) -> pd.DataFrame:
    """Generate synthetic customer data."""
    fake = Faker()
    Faker.seed(42)

    data = {
        'customer_id': list(range(1, n_rows + 1)),
        'first_name': [fake.first_name() for _ in range(n_rows)],
        'last_name': [fake.last_name() for _ in range(n_rows)],
        'email': [fake.email() for _ in range(n_rows)],
        'phone': [fake.phone_number() for _ in range(n_rows)],
        'ssn': [fake.ssn() for _ in range(n_rows)],
        'dob': [fake.date_of_birth().isoformat() for _ in range(n_rows)],
        'address': [fake.street_address() for _ in range(n_rows)],
        'city': [fake.city() for _ in range(n_rows)],
        'state': [fake.state_abbr() for _ in range(n_rows)],
        'zip_code': [fake.zipcode() for _ in range(n_rows)],
        'registration_date': [fake.date_between(start_date='-3y').isoformat() for _ in range(n_rows)],
        'status': [fake.random_element(['active', 'inactive']) for _ in range(n_rows)],
    }

    return pd.DataFrame(data)


def generate_sample_patient_data(n_rows: int = 5) -> pd.DataFrame:
    """Generate synthetic patient data."""
    fake = Faker()
    Faker.seed(42)

    data = {
        'patient_id': list(range(1, n_rows + 1)),
        'patient_name': [fake.name() for _ in range(n_rows)],
        'medical_record_number': [f"MRN{fake.random_int(100000, 999999)}" for _ in range(n_rows)],
        'diagnosis': [fake.random_element(['Diabetes Type 2', 'Hypertension', 'Asthma', 'COVID-19']) for _ in range(n_rows)],
        'medication': [fake.random_element(['Metformin', 'Lisinopril', 'Albuterol', 'Remdesivir']) for _ in range(n_rows)],
        'dob': [fake.date_of_birth(minimum_age=30, maximum_age=80).isoformat() for _ in range(n_rows)],
        'visit_date': [fake.date_between(start_date='-1m').isoformat() for _ in range(n_rows)],
        'provider_name': [fake.random_element(['Dr. Smith', 'Dr. Johnson', 'Nurse Brown', 'Nurse Davis']) for _ in range(n_rows)],
        'visit_count': [fake.random_int(1, 10) for _ in range(n_rows)],
    }

    return pd.DataFrame(data)


def generate_sample_sales_data(n_rows: int = 5) -> pd.DataFrame:
    """Generate synthetic sales transaction data."""
    fake = Faker()
    Faker.seed(42)

    data = {
        'transaction_id': list(range(1, n_rows + 1)),
        'customer_id': [fake.random_int(100, 200) for _ in range(n_rows)],
        'product_name': [fake.random_element(['Laptop', 'Mouse', 'Monitor', 'Keyboard', 'USB Cable']) for _ in range(n_rows)],
        'quantity': [fake.random_int(1, 10) for _ in range(n_rows)],
        'amount': [round(fake.random.uniform(10, 5000), 2) for _ in range(n_rows)],
        'payment_method': [fake.random_element(['credit_card', 'debit_card', 'paypal']) for _ in range(n_rows)],
        'transaction_date': [fake.date_between(start_date='-6m').isoformat() for _ in range(n_rows)],
        'order_status': [fake.random_element(['completed', 'pending', 'shipped']) for _ in range(n_rows)],
    }

    return pd.DataFrame(data)


def main():
    """Main example execution."""
    print("\nPrivacy-Aware Data Transformation Framework - Example Script\n")

    print("Generating sample metadata files...")
    metadata_gen = SyntheticMetadataGenerator()
    metadata_dir = Path('table_structure/metadata')
    metadata_dir.mkdir(parents=True, exist_ok=True)

    for table_meta in [
        metadata_gen.generate_customer_metadata(),
        metadata_gen.generate_health_metadata(),
        metadata_gen.generate_sales_metadata()
    ]:
        filepath = metadata_gen.save_metadata_yaml(table_meta, str(metadata_dir))
        print(f"Generated: {filepath}")

    print("\nGenerating sample data files...")
    data_dir = Path('data/synthetic')
    data_dir.mkdir(parents=True, exist_ok=True)

    # Customer data
    customers_df = generate_sample_customer_data(n_rows=5)
    customers_file = data_dir / 'customers.csv'
    save_csv_data(customers_df, str(customers_file))
    print(f"Generated: {customers_file}")

    # Patient data
    patients_df = generate_sample_patient_data(n_rows=5)
    patients_file = data_dir / 'patient_records.csv'
    save_csv_data(patients_df, str(patients_file))
    print(f" Generated: {patients_file}")

    # Sales data
    sales_df = generate_sample_sales_data(n_rows=5)
    sales_file = data_dir / 'sales_transactions.csv'
    save_csv_data(sales_df, str(sales_file))
    print(f"Generated: {sales_file}")

    print("\nClassifying sensitive columns...")
    classifier = SensitivityClassifier(use_ml=True)

    # Process each table
    tables_to_process = [
        ('customers', customers_df, customers_file),
        ('patient_records', patients_df, patients_file),
        ('sales_transactions', sales_df, sales_file),
    ]

    results = {}
    for table_name, df, csv_file in tables_to_process:
        print(f"\n  Processing: {table_name}")
        metadata_file = metadata_dir / f"{table_name}.yaml"

        from privacy_aware_transform.metadata import MetadataLoader
        loader = MetadataLoader(str(metadata_dir))
        table_meta = loader.load_table_metadata(metadata_file.name)

        classifications = classifier.classify_table(table_meta.columns)
        print_classification_report(classifications, table_name)

        results[table_name] = (df, table_meta, classifications)

    print("\nApplying privacy transformations for different consumers...")

    policy_engine = PolicyEngine()
    transformation_engine = TransformationEngine()

    consumer_types = ['internal_analyst', 'external_partner', 'reporting', 'public']

    for consumer_type in consumer_types:
        print(f"\n  Transforming for consumer: {consumer_type}")
        output_subdir = data_dir / consumer_type
        output_subdir.mkdir(parents=True, exist_ok=True)

        for table_name, (df, table_meta, classifications) in results.items():
            transformed_df = apply_transformations_to_dataframe(
                df, table_meta, classifications,
                consumer_type, transformation_engine, policy_engine
            )

            output_file = output_subdir / f"{table_name}_transformed.csv"
            save_csv_data(transformed_df, str(output_file))
            print(f"    ✓ {table_name} -> {output_file}")

    print("\nDone!\n")
    print("Generated files:")
    print(f"  Metadata:     {metadata_dir}/")
    print(f"  Original data: {data_dir}/")
    print(f"  Transformed:  {data_dir}/<consumer_type>/")


if __name__ == '__main__':
    main()
