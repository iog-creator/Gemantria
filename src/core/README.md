# Core Processing Logic

This module contains the fundamental algorithms and business logic for Hebrew text processing, gematria calculations, and data validation. These are the core computational components that form the foundation of the Gemantria pipeline.

## 📋 Purpose

The core module implements the essential algorithms that:
- Process Hebrew text according to traditional linguistic rules
- Calculate gematria values using established mathematical methods
- Validate data integrity and consistency
- Provide the mathematical foundation for semantic analysis

## 🔧 Key Components

### Text Processing (`extraction.py`)
- **Hebrew Text Analysis**: Extract nouns and linguistic features from biblical text
- **Normalization**: Apply Unicode normalization and Hebrew-specific text cleaning
- **Tokenization**: Break text into meaningful linguistic units
- **Morphological Analysis**: Identify word forms and grammatical features

### Gematria Calculation (`gematria.py`)
- **Traditional Methods**: Implement Mispar Hechrachi (standard gematria)
- **Finals Handling**: Correctly process final letter forms (ך, ם, נ, פ, ץ)
- **Value Computation**: Calculate numerical values for Hebrew words
- **Verification**: Cross-check calculations for accuracy

### Validation (`validation.py`)
- **Schema Validation**: Ensure data conforms to expected formats
- **Consistency Checks**: Verify relationships between data elements
- **Duplicate Detection**: Identify and handle duplicate entries
- **Integrity Verification**: Confirm mathematical correctness

## 🧮 Gematria Implementation

### Calculation Rules

The gematria calculation follows traditional Hebrew numerology:

```
א = 1    ב = 2    ג = 3    ד = 4    ה = 5
ו = 6    ז = 7    ח = 8    ט = 9    י = 10
כ = 20   ל = 30   מ = 40   נ = 50   ס = 60
ע = 70   פ = 80   צ = 90   ק = 100  ר = 200
ש = 300  ת = 400
```

**Final Forms**: ך=500, ם=600, נ=700, פ=800, ץ=900

### Processing Pipeline

1. **Input**: Normalized Hebrew text
2. **Tokenization**: Split into words and analyze morphology
3. **Filtering**: Extract nouns and significant terms
4. **Calculation**: Compute gematria values for each term
5. **Validation**: Verify calculations and check for errors
6. **Output**: Structured data with values and metadata

## 🔍 Validation Logic

### Data Quality Checks

- **Format Validation**: Ensure Hebrew text is properly encoded
- **Range Checking**: Verify gematria values are within expected bounds
- **Consistency**: Check that related calculations agree
- **Completeness**: Ensure all required fields are present

### Error Handling

- **Graceful Degradation**: Continue processing despite minor issues
- **Detailed Logging**: Record validation failures for debugging
- **Recovery Mechanisms**: Attempt to correct common data issues
- **Failure Reporting**: Clear indication of validation failures

## 📊 Performance Characteristics

### Computational Complexity

- **Text Processing**: O(n) where n is text length
- **Gematria Calculation**: O(m) where m is number of words
- **Validation**: O(k) where k is number of validation rules

### Memory Usage

- **Streaming Processing**: Minimal memory footprint
- **Batch Processing**: Scales with batch size
- **Efficient Storage**: Compact representation of results

## 🧪 Testing & Verification

### Test Coverage

- **Unit Tests**: Individual function and method testing
- **Integration Tests**: End-to-end processing verification
- **Edge Cases**: Special Hebrew characters and forms
- **Performance Tests**: Benchmarking for large text volumes

### Validation Test Cases

- **Known Values**: Verify calculations against established references
- **Edge Cases**: Test with unusual Hebrew text patterns
- **Error Conditions**: Ensure proper handling of invalid input
- **Boundary Conditions**: Test with minimum/maximum valid inputs

## 🔧 Usage Examples

### Basic Gematria Calculation

```python
from src.core.gematria import calculate_gematria

# Calculate value for a Hebrew word
word = "אלהים"  # Elohim (God)
value = calculate_gematria(word)
# Returns: 86 (1+30+5+10+40)

# Calculate for a phrase
phrase = "בראשית ברא אלהים"
values = [calculate_gematria(word) for word in phrase.split()]
# Returns: [913, 203, 1, 86] (Bereshit, bara, et, Elohim)
```

### Text Processing Pipeline

```python
from src.core.extraction import extract_nouns

# Extract nouns from Hebrew text
text = "בראשית ברא אלהים את השמים ואת הארץ"
nouns = extract_nouns(text)
# Returns: ["ראשית", "אלהים", "שמים", "ארץ"]
```

## 📚 Documentation

- **[AGENTS.md](AGENTS.md)**: AI assistant guide for development
- **[Parent](../README.md)**: Core pipeline overview
- **ADR-002**: Gematria calculation rules and validation

## 🤝 Development Guidelines

### Code Style

- **Type Hints**: Full type annotation for all functions
- **Documentation**: Comprehensive docstrings for public APIs
- **Testing**: 98%+ test coverage required
- **Performance**: Optimize for both accuracy and speed

### Adding New Features

1. **Design**: Document approach in relevant ADR
2. **Implement**: Follow established patterns and interfaces
3. **Test**: Add comprehensive test cases
4. **Document**: Update AGENTS.md and this README
5. **Validate**: Ensure all quality gates pass

### Algorithm Changes

Any changes to gematria calculation algorithms require:
- Updated test cases with known reference values
- Documentation of the change rationale
- Validation against existing processed data
- ADR documenting the algorithmic decision
