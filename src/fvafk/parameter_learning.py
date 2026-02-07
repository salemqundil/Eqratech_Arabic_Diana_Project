"""
Parameter Learning Framework

This module implements structured learning for parameters (w, μ)
without changing the function form. The function remains:

F_w(x) = argmin_{y ∈ G(x)} Σ_i w_i φ_i(y; x)

Only the weights w are learned from training data.
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Callable, Dict
from abc import ABC, abstractmethod


@dataclass
class TrainingExample:
    """A single training example (input, correct output)"""
    x: any  # Input (e.g., root, word)
    y_gold: any  # Gold standard output
    features: Dict[str, float] = None  # Precomputed features (optional)


class FeatureFunction:
    """
    A feature function φ_i(y; x) that computes a real value
    for a candidate y given input x
    """
    
    def __init__(self, name: str, fn: Callable):
        self.name = name
        self.fn = fn
    
    def __call__(self, y, x):
        return self.fn(y, x)


class StructuredLearner:
    """
    Learns weights w for structured prediction
    
    Minimizes: L = Σ_j loss(F_w(x_j), y_j) + μ||w||²
    
    where:
    - F_w(x) = argmin_{y ∈ G(x)} Σ_i w_i φ_i(y; x)
    - loss is structured loss (e.g., Hamming, edit distance)
    - μ is regularization parameter
    """
    
    def __init__(
        self,
        features: List[FeatureFunction],
        mu: float = 0.01,
        learning_rate: float = 0.01
    ):
        """
        Initialize learner
        
        Args:
            features: List of feature functions
            mu: Regularization parameter (μ)
            learning_rate: Learning rate for gradient descent
        """
        self.features = features
        self.mu = mu
        self.learning_rate = learning_rate
        self.weights = np.zeros(len(features))
    
    def compute_features(self, y, x) -> np.ndarray:
        """
        Compute feature vector φ(y; x)
        """
        return np.array([f(y, x) for f in self.features])
    
    def score(self, y, x) -> float:
        """
        Compute score: s(y; x) = w^T φ(y; x)
        """
        phi = self.compute_features(y, x)
        return np.dot(self.weights, phi)
    
    def predict(self, x, candidates: List[any]) -> any:
        """
        Predict best candidate: F_w(x) = argmin_{y ∈ G(x)} w^T φ(y; x)
        
        Note: We minimize (negative score = maximize score)
        """
        best_y = None
        best_score = float('inf')
        
        for y in candidates:
            score = self.score(y, x)
            if score < best_score:
                best_score = score
                best_y = y
        
        return best_y
    
    def structured_loss(self, y_pred, y_gold) -> float:
        """
        Compute structured loss between prediction and gold
        
        Default: 0-1 loss (can be overridden for edit distance, etc.)
        """
        return 0.0 if y_pred == y_gold else 1.0
    
    def compute_gradient(
        self,
        example: TrainingExample,
        candidates: List[any]
    ) -> np.ndarray:
        """
        Compute gradient of loss w.r.t. weights
        
        Uses structured perceptron-style update:
        ∇w = φ(y_pred; x) - φ(y_gold; x) + 2μw
        """
        # Get prediction
        y_pred = self.predict(example.x, candidates)
        
        # Feature difference
        phi_pred = self.compute_features(y_pred, example.x)
        phi_gold = self.compute_features(example.y_gold, example.x)
        
        # Gradient: (predicted - gold) + regularization
        grad = phi_pred - phi_gold + 2 * self.mu * self.weights
        
        return grad
    
    def train(
        self,
        training_data: List[TrainingExample],
        candidate_generator: Callable,
        epochs: int = 10,
        verbose: bool = True
    ):
        """
        Train weights using structured perceptron
        
        Args:
            training_data: List of (x, y_gold) examples
            candidate_generator: Function that generates candidates for x
            epochs: Number of training epochs
            verbose: Print progress
        """
        n = len(training_data)
        
        for epoch in range(epochs):
            total_loss = 0.0
            
            for example in training_data:
                # Generate candidates
                candidates = candidate_generator(example.x)
                
                # Compute gradient
                grad = self.compute_gradient(example, candidates)
                
                # Update weights
                self.weights -= self.learning_rate * grad
                
                # Compute loss for tracking
                y_pred = self.predict(example.x, candidates)
                loss = self.structured_loss(y_pred, example.y_gold)
                total_loss += loss
            
            # Add regularization to loss
            reg_term = self.mu * np.sum(self.weights ** 2)
            total_loss += reg_term
            
            if verbose:
                avg_loss = total_loss / n
                print(f"Epoch {epoch+1}/{epochs}: Avg Loss = {avg_loss:.4f}")
    
    def get_weights(self) -> Dict[str, float]:
        """Get learned weights as dictionary"""
        return {f.name: w for f, w in zip(self.features, self.weights)}


def demonstrate_parameter_learning():
    """
    Demonstrate parameter learning with toy example
    """
    print("=" * 70)
    print("PARAMETER LEARNING FRAMEWORK")
    print("=" * 70)
    print("\nThe function form is FIXED:")
    print("  F_w(x) = argmin_{y ∈ G(x)} Σ_i w_i φ_i(y; x)")
    print()
    print("We learn weights w from data by minimizing:")
    print("  L(w) = Σ_j loss(F_w(x_j), y_j) + μ||w||²")
    print()
    print("μ is the REGULARIZATION parameter (prevents overfitting)")
    print("=" * 70)
    print()
    
    # Define toy feature functions
    features = [
        FeatureFunction("length", lambda y, x: len(y)),
        FeatureFunction("vowels", lambda y, x: sum(1 for c in y if c in 'aiu')),
        FeatureFunction("consonants", lambda y, x: sum(1 for c in y if c not in 'aiu')),
    ]
    
    # Create learner with regularization
    learner = StructuredLearner(
        features=features,
        mu=0.01,  # Small regularization
        learning_rate=0.1
    )
    
    print("Feature functions:")
    for i, f in enumerate(features):
        print(f"  φ_{i+1}: {f.name}")
    
    print(f"\nRegularization: μ = {learner.mu}")
    print(f"Initial weights: w = {learner.weights}")
    
    # Toy training data (simplified)
    training_data = [
        TrainingExample(x="ktb", y_gold="kutub"),   # كتب → كتب
        TrainingExample(x="qlm", y_gold="aqlaam"),  # قلم → أقلام
    ]
    
    def toy_candidate_generator(x):
        """Generate toy candidates"""
        return [x + "a", x + "u", "a" + x + "aa"]
    
    print("\nTraining...")
    print()
    
    learner.train(
        training_data=training_data,
        candidate_generator=toy_candidate_generator,
        epochs=5,
        verbose=True
    )
    
    print("\nLearned weights:")
    weights_dict = learner.get_weights()
    for name, w in weights_dict.items():
        print(f"  w_{name:12s} = {w:8.4f}")
    
    print("\n" + "=" * 70)
    print("KEY INSIGHT:")
    print("=" * 70)
    print("The FUNCTION FORM never changes - it's always the same argmin.")
    print("Only the PARAMETERS (weights w) are learned from data.")
    print("Regularization μ prevents overfitting but doesn't change the form.")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_parameter_learning()
