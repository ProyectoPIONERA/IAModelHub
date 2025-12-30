"""
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
print(f"  Testing: {metadata['model_name']}")
print("=" * 60)

# Show required variables
print("\nRequired input variables:")
for feature in metadata['input_features']:
    print(f"  {feature['position']}. {feature['name']} ({feature['type']})")
    print(f"     Description: {feature['description']}")
    print(f"     Range: [{feature['min']:.2f}, {feature['max']:.2f}]")
    print(f"     Example: {feature['example_value']}")
    print()

# Example 1: Use documented example input
print("\nExample 1: Using documented example input")
example_input = metadata['example_input']
print(f"Input: {example_input}")

prediction = model.predict([example_input])
probabilities = model.predict_proba([example_input])[0]

print(f"\nPrediction: {metadata['classes'][prediction[0]]}")
print("Probabilities:")
for i, class_name in enumerate(metadata['classes']):
    print(f"  {class_name}: {probabilities[i]:.2%}")

# Example 2: Create your own input
print("\n" + "=" * 60)
print("Example 2: Custom input")
print("=" * 60)

# Create input based on documented variables
custom_input = [
    5.1,  # sepal length (cm)
    3.5,  # sepal width (cm)
    1.4,  # petal length (cm)
    0.2   # petal width (cm)
]

print(f"Input: {custom_input}")
prediction = model.predict([custom_input])
probabilities = model.predict_proba([custom_input])[0]

print(f"\nPrediction: {metadata['classes'][prediction[0]]}")
print("Probabilities:")
for i, class_name in enumerate(metadata['classes']):
    print(f"  {class_name}: {probabilities[i]:.2%}")
