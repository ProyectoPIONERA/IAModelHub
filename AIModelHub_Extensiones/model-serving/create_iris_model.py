"""
Create example model using the Iris Dataset.
This script builds a simple model to test the HTTP assets system.
"""
import pickle
import json
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import os

# Output directory
OUTPUT_DIR = '/home/edmundo/AIModelHub/AIModelHub_Extensiones/model-server/models'
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("  Creating Example Model - Iris Dataset")
print("=" * 60)

# Load Iris dataset
print("\n1. Loading Iris Dataset...")
iris = datasets.load_iris()
X = iris.data
y = iris.target

print(f"   - Total samples: {len(X)}")
print(f"   - Number of features: {X.shape[1]}")
print(f"   - Clases: {iris.target_names.tolist()}")
print(f"   - Features: {iris.feature_names}")

# Split train/test
print("\n2. Splitting dataset (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"   - Train samples: {len(X_train)}")
print(f"   - Test samples: {len(X_test)}")

# Train model
print("\n3. Training Random Forest Classifier...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
print("   ✓ Model trained")

# Evaluate
print("\n4. Evaluating model...")
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"   - Accuracy: {accuracy:.2%}")

print("\n   Classification Report:")
print(classification_report(y_test, y_pred, target_names=iris.target_names))

# Save model
model_path = os.path.join(OUTPUT_DIR, 'iris_classifier.pkl')
print(f"\n5. Saving model to: {model_path}")
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
print(f"   ✓ Model saved ({os.path.getsize(model_path):,} bytes)")

# Create model metadata (includes variable info)
metadata = {
    "model_name": "Iris Random Forest Classifier",
    "model_type": "RandomForestClassifier",
    "version": "1.0",
    "algorithm": "Random Forest",
    "library": "scikit-learn",
    "framework": "scikit-learn",
    "task": "Classification",
    "subtask": "Multi-class Classification",
    "programming_language": "Python",
    "accuracy": float(accuracy),
    "num_classes": len(iris.target_names),
    "classes": iris.target_names.tolist(),
    
    # IMPORTANT: Document required input features/variables
    "input_features": [
        {
            "name": "sepal length (cm)",
            "position": 0,
            "type": "float",
            "description": "Sepal length in centimeters",
            "example_value": 5.1,
            "min": float(X[:, 0].min()),
            "max": float(X[:, 0].max()),
            "mean": float(X[:, 0].mean())
        },
        {
            "name": "sepal width (cm)",
            "position": 1,
            "type": "float",
            "description": "Sepal width in centimeters",
            "example_value": 3.5,
            "min": float(X[:, 1].min()),
            "max": float(X[:, 1].max()),
            "mean": float(X[:, 1].mean())
        },
        {
            "name": "petal length (cm)",
            "position": 2,
            "type": "float",
            "description": "Petal length in centimeters",
            "example_value": 1.4,
            "min": float(X[:, 2].min()),
            "max": float(X[:, 2].max()),
            "mean": float(X[:, 2].mean())
        },
        {
            "name": "petal width (cm)",
            "position": 3,
            "type": "float",
            "description": "Petal width in centimeters",
            "example_value": 0.2,
            "min": float(X[:, 3].min()),
            "max": float(X[:, 3].max()),
            "mean": float(X[:, 3].mean())
        }
    ],
    
    # Example input/output for testing
    "example_input": X_test[0].tolist(),
    "example_output": {
        "predicted_class": iris.target_names[y_pred[0]],
        "predicted_class_index": int(y_pred[0]),
        "probabilities": model.predict_proba([X_test[0]])[0].tolist()
    },
    
    "training_info": {
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "random_state": 42
    }
}

# Save metadata
metadata_path = os.path.join(OUTPUT_DIR, 'iris_classifier_metadata.json')
print(f"\n6. Saving metadata to: {metadata_path}")
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"   ✓ Metadata saved")

# Create test script
test_script_path = os.path.join(OUTPUT_DIR, 'test_iris_model.py')
print(f"\n7. Creating test script: {test_script_path}")

test_script_content = f'''"""
Test script for the Iris Classifier model
Shows how to use the model with documented variables
"""
import pickle
import json
import numpy as np

# Load model
with open('iris_classifier.pkl', 'rb') as f:
    model = pickle.load(f)

# Load metadata
with open('iris_classifier_metadata.json', 'r') as f:
    metadata = json.load(f)

print("=" * 60)
print(f"  Testing: {{metadata['model_name']}}")
print("=" * 60)

# Show required variables
print("\\nRequired input variables:")
for feature in metadata['input_features']:
    print(f"  {{feature['position']}}. {{feature['name']}} ({{feature['type']}})")
    print(f"     Description: {{feature['description']}}")
    print(f"     Range: [{{feature['min']:.2f}}, {{feature['max']:.2f}}]")
    print(f"     Example: {{feature['example_value']}}")
    print()

# Example 1: Use documented example input
print("\\nExample 1: Using documented example input")
example_input = metadata['example_input']
print(f"Input: {{example_input}}")

prediction = model.predict([example_input])
probabilities = model.predict_proba([example_input])[0]

print(f"\\nPrediction: {{metadata['classes'][prediction[0]]}}")
print("Probabilities:")
for i, class_name in enumerate(metadata['classes']):
    print(f"  {{class_name}}: {{probabilities[i]:.2%}}")

# Example 2: Create your own input
print("\\n" + "=" * 60)
print("Example 2: Custom input")
print("=" * 60)

# Create input based on documented variables
custom_input = [
    5.1,  # sepal length (cm)
    3.5,  # sepal width (cm)
    1.4,  # petal length (cm)
    0.2   # petal width (cm)
]

print(f"Input: {{custom_input}}")
prediction = model.predict([custom_input])
probabilities = model.predict_proba([custom_input])[0]

print(f"\\nPrediction: {{metadata['classes'][prediction[0]]}}")
print("Probabilities:")
for i, class_name in enumerate(metadata['classes']):
    print(f"  {{class_name}}: {{probabilities[i]:.2%}}")
'''

with open(test_script_path, 'w') as f:
    f.write(test_script_content)
print(f"   ✓ Test script created")

print("\n" + "=" * 60)
print("  ✅ Model created successfully")
print("=" * 60)
print(f"\nGenerated files:")
print(f"  1. Model:    {model_path}")
print(f"  2. Metadata: {metadata_path}")
print(f"  3. Test:     {test_script_path}")
print(f"\nTo test the model:")
print(f"  cd {OUTPUT_DIR}")
print(f"  python3 test_iris_model.py")
print()
