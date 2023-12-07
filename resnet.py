"""ResNet Module"""
from tensorflow.keras.layers import *
from tensorflow.keras.models import Model, Sequential

class ResNetBlock(Layer):
    def __init__(self, hidden_channels):
        super().__init__()

        self.sequence = Sequential([
            Conv2D(hidden_channels, 3, 1, padding='same'),
            BatchNormalization(),
            ReLU(),

            Conv2D(hidden_channels, 3, 1, padding='same'),
            BatchNormalization(),
            ReLU(),
        ])

    def forward(self, x):
        return x + self.sequence(x)


class NeuralNet(Layer):
    def __init__(self, board_size, num_res_blocks, num_hidden):
        super().__init__()

        self.start_block = Sequential([
            Conv2D(num_hidden, 3, 1, padding='same'),
            BatchNormalization(),
            ReLU()
        ])

        self.back_bone = Sequential(
            [ResNetBlock(num_hidden) for i in range(num_res_blocks)]
        )

        self.policy_head = Sequential([
            Conv2D(32, 3, 1, padding='same'),
            BatchNormalization(),
            ReLU(),
            Flatten(),
            Dense(board_size * board_size + 1),
        ])

        self.value_head = Sequential([
            Conv2D(3, 3, 1, padding='same'),
            BatchNormalization(),
            ReLU(),
            Flatten(),
            Dense(1),
            Activation('tanh')
        ])

    def forward(self, x):
        x = self.start_block(x)
        x = self.back_bone(x)
        p = self.policy_head(x)
        v = self.value_head(x)
        return p, v
