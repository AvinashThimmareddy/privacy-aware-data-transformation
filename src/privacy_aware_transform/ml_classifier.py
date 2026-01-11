"""
Machine Learning Classifier Training Module

Provides ML model training pipeline for sensitivity classification.
Trains on metadata from YAML files and creates a reusable model.
"""

import os
import pickle
from pathlib import Path
from typing import List, Tuple, Dict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


class MLClassifierTrainer:
    """
    Trains ML models for sensitivity classification.
    
    Processes metadata from YAML files and creates a trained classifier.
    Supports incremental training by scanning all metadata files.
    """

    def __init__(self, random_state: int = 42):
        """
        Initialize trainer.

        Args:
            random_state: Random seed for reproducibility
        """
        self.random_state = random_state
        self.model = None
        self.classes = ['PII', 'PHI', 'Sensitive', 'Non-Sensitive']
        self.feature_names = []

    def extract_features(self, column_name: str, description: str, data_type: str = "") -> str:
        """
        Extract and combine features from column metadata.

        Args:
            column_name: Column name
            description: Column description
            data_type: Column data type

        Returns:
            Combined feature string for TF-IDF
        """
        # Combine all metadata into single feature string
        features = f"{column_name} {description} {data_type}"
        return features.lower()

    def prepare_training_data(self, metadata_list: List[Dict]) -> Tuple[List[str], List[str]]:
        """
        Prepare training data from metadata list.

        Args:
            metadata_list: List of metadata dictionaries with keys:
                - 'features': Combined feature string
                - 'label': Sensitivity class (PII, PHI, Sensitive, Non-Sensitive)

        Returns:
            Tuple of (feature_texts, labels)
        """
        features = []
        labels = []

        for item in metadata_list:
            features.append(item['features'])
            labels.append(item['label'])

        return features, labels

    def train(self, feature_texts: List[str], labels: List[str]) -> None:
        """
        Train the ML model on provided data.

        Args:
            feature_texts: List of feature strings
            labels: List of corresponding labels
        """
        if not feature_texts or not labels:
            print("Warning: No training data provided")
            return

        if len(feature_texts) != len(labels):
            raise ValueError("Feature texts and labels must have same length")

        print(f"Training ML classifier on {len(feature_texts)} samples...")

        # Create pipeline: TF-IDF → Logistic Regression
        self.model = Pipeline([
            (
                'tfidf', TfidfVectorizer(
                max_features=100,
                lowercase=True,
                ngram_range=(1, 2),  # Unigrams and bigrams
                min_df=1,
                max_df=0.9
            )),
            ('classifier', LogisticRegression(
                max_iter=200,
                random_state=self.random_state,
                class_weight='balanced',  # Handle imbalanced classes
                C=1.0  # Regularization strength
            ))
        ])

        # Train the model
        self.model.fit(feature_texts, labels)

        # Print training info
        classes_in_training = set(labels)
        print(f"Training complete")
        print(f"Classes: {', '.join(sorted(classes_in_training))}")
        print(f"Samples per class:")
        for cls in sorted(self.classes):
            count = labels.count(cls)
            if count > 0:
                print(f"{cls}: {count}")

    def predict(self, feature_text: str) -> Tuple[str, float]:
        """
        Make prediction on a single feature text.

        Args:
            feature_text: Feature string

        Returns:
            Tuple of (predicted_class, confidence)
        """
        if not self.model:
            raise RuntimeError("Model not trained. Call train() first.")

        prediction = self.model.predict([feature_text])[0]
        probabilities = self.model.predict_proba([feature_text])[0]
        confidence = float(max(probabilities))

        return prediction, confidence

    def predict_batch(self, feature_texts: List[str]) -> List[Tuple[str, float]]:
        """
        Make predictions on multiple feature texts.

        Args:
            feature_texts: List of feature strings

        Returns:
            List of (predicted_class, confidence) tuples
        """
        if not self.model:
            raise RuntimeError("Model not trained. Call train() first.")

        predictions = self.model.predict(feature_texts)
        probabilities = self.model.predict_proba(feature_texts)

        results = []
        for pred, probs in zip(predictions, probabilities):
            confidence = float(max(probs))
            results.append((pred, confidence))

        return results

    def save_model(self, filepath: str) -> None:
        """
        Save trained model to pickle file.

        Args:
            filepath: Path to save model file
        """
        if not self.model:
            raise RuntimeError("No model to save. Train first.")

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(self.model, f)
        print(f"Model saved to {filepath}")

    @staticmethod
    def load_model(filepath: str) -> Pipeline:
        """
        Load trained model from pickle file.

        Args:
            filepath: Path to model file

        Returns:
            Loaded sklearn Pipeline model
        """
        if not Path(filepath).exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")

        with open(filepath, 'rb') as f:
            model = pickle.load(f)
        return model

    def get_feature_importances(self) -> Dict[str, float]:
        """
        Get feature importances from the trained model.

        Returns:
            Dictionary of feature names and their importance scores
        """
        if not self.model:
            raise RuntimeError("Model not trained")

        # Get TF-IDF vectorizer and classifier
        tfidf = self.model.named_steps['tfidf']
        classifier = self.model.named_steps['classifier']

        # Get feature names from TF-IDF
        feature_names = tfidf.get_feature_names_out()

        # Get coefficients from Logistic Regression
        # Average absolute coefficients across all classes
        coef_importance = np.abs(classifier.coef_).mean(axis=0)

        # Create dictionary
        importances = dict(zip(feature_names, coef_importance))

        # Sort by importance
        sorted_importances = dict(sorted(
            importances.items(),
            key=lambda x: x[1],
            reverse=True
        ))

        return sorted_importances
