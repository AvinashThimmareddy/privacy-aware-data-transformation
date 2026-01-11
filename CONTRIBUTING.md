# Contributing to Privacy-Aware Data Transformation

Welcome! We're excited that you're interested in contributing to this open-source research project. This document provides guidelines and instructions for contributing.

---

## 🎯 What is This Project?

This is a research framework for **automated sensitive data classification** and **adaptive privacy-preserving data transformations**. It uses metadata-driven machine learning techniques to identify PII, PHI, and sensitive data, then dynamically applies privacy transformations based on consumer policies.

---

## 🤝 How to Contribute

### Types of Contributions

We welcome contributions in several forms:

1. **Code Contributions**
   - Bug fixes
   - New features (see "Good First Features" below)
   - Performance improvements
   - Test coverage improvements

2. **Documentation**
   - Typo fixes
   - Clarifications
   - Additional examples
   - Tutorials

3. **Research & Ideas**
   - New classification patterns
   - Privacy-preserving transformation techniques
   - Performance optimizations
   - Novel use cases

4. **Testing**
   - Bug reports
   - Test cases
   - Real-world dataset testing

---

## 📋 Good First Features to Add

These are simple features suitable for first-time contributors:

### 1. **Add More Classification Patterns** (Easy - 30 min)
**Location**: `src/privacy_aware_transform/classifier.py` → `_build_patterns()` method

Add new regex patterns to improve classification accuracy:
```python
# Example: Add patterns for credit card numbers, PAN numbers, etc.
'credit_card': [
    r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Visa/Mastercard format
],
'pan_number': [
    r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',  # Indian PAN format
],
```

**Why useful**: Improves sensitivity classification accuracy for different data types and regions.

### 2. **Add New Consumer Policy** (Easy - 20 min)
**Location**: `src/privacy_aware_transform/policy.py` → `_get_default_policies()` method

Add a new consumer type with custom transformation rules:
```python
# Example: Medical researcher policy (balanced privacy & utility)
'medical_researcher': {
    'PII': 'tokenize',      # Consistent pseudonymization
    'PHI': 'mask',          # Partial masking
    'Sensitive': 'keep',    # Full utility
    'Non-Sensitive': 'keep'
}
```

**Why useful**: Different organizations need different privacy-utility tradeoffs.

### 3. **Add Unit Tests for Transformations** (Medium - 45 min)
**Location**: Create `tests/test_transformations.py`

Add comprehensive tests for each transformation:
```python
def test_masking_transformation():
    """Test that masking obscures first/last characters."""
    transformer = MaskingTransformer()
    result = transformer.transform("john@example.com")
    assert result.startswith("j")
    assert result.endswith("com")
    assert "@" not in result[1:-3]

def test_hashing_transformation():
    """Test that hashing is deterministic and irreversible."""
    transformer = HashingTransformer()
    value1 = transformer.transform("sensitive_data")
    value2 = transformer.transform("sensitive_data")
    assert value1 == value2  # Deterministic
    assert "sensitive_data" not in value1  # Irreversible
```

**Why useful**: Better test coverage ensures reliability.

### 4. **Add Metadata for New Domain** (Medium - 30 min)
**Location**: `table_structure/metadata/` → Create new YAML file

Add metadata for a new business domain:
```yaml
# table_structure/metadata/financial_transactions.yaml
table_name: financial_transactions
description: "Financial transaction records"
columns:
  - name: account_number
    data_type: string
    description: "Bank account number (PII - financial)"
  - name: transaction_amount
    data_type: float
    description: "Transaction amount in USD (Sensitive)"
  # ... more columns
```

**Why useful**: Trains the ML model on more diverse data.

### 5. **Add Data Validation Function** (Medium - 45 min)
**Location**: `src/privacy_aware_transform/utils.py`

Add validation for transformed data:
```python
def validate_transformed_data(original_df: pd.DataFrame, 
                              transformed_df: pd.DataFrame,
                              classifications: List[ClassificationResult]) -> dict:
    """
    Validate that sensitive data has been properly transformed.
    
    Returns:
        dict with keys: 'all_sensitive_transformed', 'stats', 'warnings'
    """
    stats = {
        'original_rows': len(original_df),
        'transformed_rows': len(transformed_df),
        'columns_transformed': 0,
        'issues': []
    }
    
    for col, classification in zip(original_df.columns, classifications):
        if classification.class != 'Non-Sensitive':
            original_values = set(original_df[col].astype(str).unique())
            transformed_values = set(transformed_df[col].astype(str).unique())
            
            if original_values == transformed_values:
                stats['issues'].append(f"Column '{col}' not transformed!")
            else:
                stats['columns_transformed'] += 1
    
    return stats
```

**Why useful**: Helps verify transformations are working correctly.

### 6. **Add CLI Command for Model Evaluation** (Medium - 45 min)
**Location**: `src/privacy_aware_transform/cli.py`

Add a command to evaluate classifier performance:
```bash
python -m privacy_aware_transform.cli evaluate-classifier \
  --metadata-dir table_structure/metadata \
  --output evaluation_report.json
```

**Why useful**: Makes it easy to assess classification accuracy.

### 7. **Add Configuration File Support** (Medium - 1 hour)
**Location**: Create `src/privacy_aware_transform/config.py`

Support YAML/JSON configuration files:
```yaml
# config.yaml
classifier:
  use_ml: true
  ml_model_path: models/sensitivity_classifier.pkl
  confidence_threshold: 0.8

transformations:
  masking_character: "*"
  hash_algorithm: "sha256"

policies:
  default_consumer: "internal_analyst"
```

**Why useful**: Makes configuration management easier for large deployments.

### 8. **Add Batch Processing Progress Bar** (Easy - 20 min)
**Location**: `src/privacy_aware_transform/transforms.py` → `TransformationEngine.transform_batch()`

Add tqdm progress bar for better UX:
```python
from tqdm import tqdm

def transform_batch(self, df: pd.DataFrame, ...) -> pd.DataFrame:
    """Transform all rows with progress indication."""
    rows_list = []
    for idx in tqdm(range(len(df)), desc="Transforming rows"):
        row = df.iloc[idx]
        transformed_row = {
            col: self.transform_value(row[col], col, ...) 
            for col in df.columns
        }
        rows_list.append(transformed_row)
    return pd.DataFrame(rows_list)
```

**Why useful**: Better user experience for large datasets.

### 9. **Add CSV Export with Metadata** (Medium - 30 min)
**Location**: `src/privacy_aware_transform/utils.py`

Add function to save data with transformation report:
```python
def save_csv_with_report(transformed_df: pd.DataFrame, 
                         filepath: str,
                         transformations_applied: dict):
    """Save CSV and create accompanying metadata file."""
    # Save CSV
    transformed_df.to_csv(filepath, index=False)
    
    # Save transformation report (JSON)
    report_path = filepath.replace('.csv', '_transformation_report.json')
    with open(report_path, 'w') as f:
        json.dump(transformations_applied, f, indent=2)
```

**Why useful**: Helps track what transformations were applied.

### 10. **Add Unit Tests for Classifier** (Medium - 1 hour)
**Location**: Create `tests/test_classifier.py`

Add tests for rule-based and ML classification:
```python
def test_pii_classification():
    """Test that PII patterns are correctly identified."""
    classifier = SensitivityClassifier(use_ml=False)
    
    pii_columns = [
        'first_name', 'email', 'phone_number', 'ssn'
    ]
    
    for col_name in pii_columns:
        result = classifier.classify_column(
            ColumnMetadata(name=col_name, data_type='string', description='')
        )
        assert result.class == 'PII', f"Failed for {col_name}"

def test_ml_fallback():
    """Test that classifier falls back to rules if ML unavailable."""
    classifier = SensitivityClassifier(use_ml=True)
    # Temporarily move model
    # Verify it still classifies correctly with rules
```

**Why useful**: Ensures classifier accuracy.

---

## 🏗️ Development Setup

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/privacy-aware-data-transformation.git
cd privacy-aware-data-transformation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install pytest pytest-cov black flake8
```

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b bugfix/issue-description
```

### 3. Make Your Changes

- Follow coding standards (see below)
- Write tests for new features
- Update documentation if needed

### 4. Run Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/

# Run specific test file
python -m pytest tests/test_classifier.py -v

# Run quick validation
python test_quick.py
```

### 5. Format Code

```bash
# Format with black
black src/ examples/ tests/

# Check with flake8
flake8 src/ examples/ tests/
```

### 6. Submit Pull Request

```bash
git push origin feature/your-feature-name
# Then create PR on GitHub with description of changes
```

---

## 📝 Coding Standards

### Python Style
- Follow PEP 8 conventions
- Use type hints for function arguments and returns
- Maximum line length: 100 characters
- Use docstrings for all functions and classes

### Example:
```python
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Result:
    """Result of a classification operation."""
    class_name: str
    confidence: float
    method: str

def classify_columns(
    columns: List[ColumnMetadata],
    use_ml: bool = True
) -> List[Result]:
    """
    Classify multiple columns for sensitivity.
    
    Args:
        columns: List of column metadata to classify
        use_ml: Whether to use ML-based classification
        
    Returns:
        List of classification results
        
    Raises:
        ValueError: If columns list is empty
    """
    if not columns:
        raise ValueError("Columns list cannot be empty")
    
    results = []
    for col in columns:
        result = classify_column(col, use_ml)
        results.append(result)
    
    return results
```

### Testing Standards
- Write tests for all new features
- Use pytest framework
- Aim for >80% code coverage
- Test both happy path and error cases

---

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Description**: What's the bug?
2. **Steps to Reproduce**: How to trigger it?
3. **Expected Behavior**: What should happen?
4. **Actual Behavior**: What actually happened?
5. **Environment**: Python version, OS, dependencies

### Example Issue Template:
```
**Title**: Classifier fails on empty column descriptions

**Description**:
The classifier throws an error when processing columns with empty descriptions.

**Steps to Reproduce**:
1. Create metadata with empty description: `description: ""`
2. Run: `classifier.classify_column(column)`
3. Error occurs

**Expected Behavior**:
Should classify using column name only

**Actual Behavior**:
TypeError: expected string or bytes-like object

**Environment**:
- Python 3.9
- privacy-aware-data-transformation 1.0.0
```

---

## 📚 Documentation Guidelines

### For Code Comments
- Use docstrings for all public functions/classes
- Explain the "why", not just the "what"
- Include type hints in docstrings

### For Guides
- Use clear, simple language
- Include code examples
- Add diagrams for complex concepts
- Keep sections short (max 10 minutes read)

### Files to Update When Adding Features
- **Code**: Corresponding module in `src/privacy_aware_transform/`
- **Tests**: `tests/` directory
- **Examples**: `examples/example.py` if public-facing
- **Docs**: `README.md` if it's a major feature, or appropriate guide

---

## 🔄 Pull Request Process

### Before Submitting
1. ✅ Tests pass: `python test_quick.py && python -m pytest`
2. ✅ Code formatted: `black src/`
3. ✅ No linting issues: `flake8 src/`
4. ✅ Documentation updated
5. ✅ Commit messages are clear

### PR Description Template
```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Related Issue
Fixes #(issue number)

## How to Test
Steps to verify the changes work.

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes
```

### Review Process
1. Maintainers will review your PR
2. Request changes if needed
3. Approve and merge once ready
4. Your contribution is celebrated! 🎉

---

## 📦 Release Process

We follow semantic versioning (MAJOR.MINOR.PATCH):

- **PATCH** (1.0.1): Bug fixes
- **MINOR** (1.1.0): New features, backward compatible
- **MAJOR** (2.0.0): Breaking changes

---

## ✨ Recognition

Contributors will be recognized in:
- README.md contributors section
- CONTRIBUTORS.md file
- GitHub automatically tracks contributions

---

## 📞 Questions or Discussions?

- **Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Emails**: Contact maintainers if needed

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

## 🎓 Learning Resources

To understand the codebase better:

1. **Start Here**: Read [README.md](README.md)
2. **Architecture**: See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
3. **ML Details**: Check [ML_TRAINING_GUIDE.md](ML_TRAINING_GUIDE.md)
4. **Code Examples**: Look at [examples/example.py](examples/example.py)
5. **Tests**: Review test files to understand how to use modules

---

## 🚀 Thank You!

Thank you for contributing to privacy-preserving data engineering! Your work helps advance the field and makes this framework better for everyone.

**Happy coding! 💻**

---

**Last Updated**: January 4, 2026  
**Maintainers**: [Your Name/Organization]  
**License**: Apache 2.0
