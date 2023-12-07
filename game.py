"""Hex Game State."""
import numpy as np

class Hex:
    def __init__(self):
        self.size = 11
        self.action_size = self.size ** 2 + 1
        self.turn = 1

    def __repr__(self):
        return "Hex"

    def get_initial_state(self):
        return np.zeros((self.size, self.size))

    def get_next_state(self, state, action, player):
        self.turn += 1
        if action == self.action_size - 1:
            assert player == -1
            return self._swap(state)

        r = action // self.size
        c = action % self.size
        print(r, c)
        state[r, c] = (action + 1) * player

        neighbours = self._neighbours(action)
        for nr, nc in neighbours:
            if nr < 0:
                continue
            if np.sign(state[nr, nc]) != player:
                continue

            state = np.where(state == state[nr, nc], action + 1, state)

        return state


    def check_win(self, state, action):
        if action is None:
            return False

        ## Maybe change this
        r = action // self.size
        c = action % self.size
        player = np.sign(state[r, c])

        if player == 1:
            start = state[0, :]
            end = state[-1, :]
        else:
            start = state[:, 0]
            end = state[:, -1]

        return np.any((start == end) == (np.sign(start) == player))

    def get_value_and_terminated(self, state, action):
        if self.check_win(state, action):
            return 1, True
        return 0, False

    def get_opponent(self, player):
        return -player

    def get_opponent_value(self, value):
        return -value

    def change_perspective(self, state):
        # Why should we care what player
        return state.T * -1

    def get_encoded_state(self, state, player):
        if player == -1:
            state = self.change_perspective(state)

        my_board = state > 0
        op_board = state < 0
        no_board = state == 0
        can_swap = np.ones_like(my_board) * self.turn == 2

        encoded_state = np.stack(my_board, op_board, no_board, can_swap).astype(np.float32)

        if len(encoded_state.shape) == 3:
            encoded_state = np.swapaxes(encoded_state, 0, 1)

        return encoded_state

    def get_valid_moves(self, state, player):
        return np.append((state.reshape(-1) == 0).astype(np.uint8), [self.turn == 2])


    def _swap(self, state):
        return state * -1


    def _neighbours(self, rc):
        """
            (r-1,c)   (r-1,c+1)
        (r,c-1)    (r,c)    (r,c+1)
            (r+1,c-1)   (r+1,c)
        """
        r = rc // self.size
        c = rc % self.size

        rs = np.array([r-1, r-1, r, r+1, r+1, r])
        cs = np.array([c, c+1, c+1, c, c-1, c-1])

        on_board = (0 <= rs) & (rs < self.size) & (0 <= cs) & (cs < self.size)
        return np.swapaxes(np.where(on_board, (rs, cs), -1), 0, 1)


    def pretty_please_state(self, state):
        """Display the current state (nicely)."""
        no_to_symbol = {
                -1: "O",
                0: ".",
                1: "#"
        }
        state = np.sign(state)
        mid_sum = (self.size + self.size - 2) // 2
        print("            1 A")
        for sum in range(self.size + self.size - 1):
            space_no = abs(mid_sum - sum)
            print(" " * space_no, end="")
            if sum < self.size - 1:
                if len(str(sum+2)) < 2:
                    print(" ", end="")
                print(f"{sum+2} ", end="")
            else:
                print(f" {no_to_symbol[1]} ", end="")

            for i in range(sum + 1):
                if i >= self.size:
                    break
                j = sum - i
                if j >= self.size:
                    continue
                print(no_to_symbol[state[j, i]], end=" ")
            if sum < self.size - 1:
                print(f"{chr(sum + 66)}")
            else:
                print(no_to_symbol[-1])
        print("            # 0")



if __name__ == "__main__":
    hex = Hex()
    state = hex.get_initial_state()
    state = hex.get_next_state(state, 13, 1)
    state = hex.get_next_state(state, 2, 1)
    hex.pretty_please_state(state)
    state = hex.change_perspective(state)
    hex.pretty_please_state(state)
