import numpy as np

class NeuralNetwork:
  def __init__(self, learning_rate):
    self.weights = np.array([np.random.randn(), np.random.randn()])
    self.bias = np.random.randn()
    self.learning_rate = learning_rate
  
  # greater dot product betweem vectors = more similar (loosely)