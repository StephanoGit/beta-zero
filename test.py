from game import Hex
from resnet import NeuralNet
import numpy as np

game = Hex()
state = game.get_initial_state()
state = game.get_next_state(state, 0, 1)
state = game.get_next_state(state, 13, -1)
encoded = game.get_encoded_state(state, 1)
encoded = np.array([encoded])

model = NeuralNet(state.size, 4, 64)
p, v = model.forward(encoded)
print(p, v)
