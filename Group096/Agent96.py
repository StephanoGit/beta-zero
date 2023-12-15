import socket
from random import choice
from time import sleep
from agents.grave import GRaveMctsAgent
from agents.bridget import BridgetMctsAgent
from game import GameMeta

class Agent():
    HOST = "127.0.0.1"
    PORT = 1234

    def run(self, verbose=False, save_file=None, time_per_move=4):
        """A finite-state machine that cycles through waiting for input
        and sending moves.
        """

        self._board_size = 0
        self._board = []
        self._colour = ""
        self._turn_count = 0
        self._choices = []
        self.agent = BridgetMctsAgent()
        self.player = GameMeta.PLAYERS["white"]
        self.dt = time_per_move
        self.opponent_move = ""


        self.f = None
        if save_file:
            with open(save_file, "w") as _:
                pass
            self.f = open(save_file, "a")

        self.bench = {
            "rollouts": [],
            "nodes": [],
            "moves": [],
        }

        self.verbose = verbose

        states = {
            1: Agent._connect,
            2: Agent._wait_start,
            3: Agent._make_move,
            4: Agent._wait_message,
            5: Agent._close
        }

        res = states[1](self)
        while (res != 0):
            res = states[res](self)

    def _connect(self):
        """Connects to the socket and jumps to waiting for the start
        message.
        """

        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((Agent.HOST, Agent.PORT))

        return 2

    def _wait_start(self):
        """Initialises itself when receiving the start message, then
        answers if it is Red or waits if it is Blue.
        """

        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        if (data[0] == "START"):
            self._board_size = int(data[1])
            for i in range(self._board_size):
                for j in range(self._board_size):
                    self._choices.append((i, j))
            self._colour = data[2]

            if (self._colour == "R"):
                return 3
            else:
                return 4

        else:
            print("ERROR: No START message received.")
            return 0

    def _make_move(self):
        """Makes a random valid move. It will choose to swap with
        a coinflip.
        """
        if self._turn_count == 1 and self._colour == "B":
            move = self.agent.root_state.str_to_action(self.opponent_move)
            if GameMeta.SWAP_MATRIX[move]:
                self._s.sendall(bytes("SWAP", "utf-8"))
                self.bench["rollouts"].append(None)
                self.bench["nodes"].append(None)
                self.bench["moves"].append([self.opponent_move, "swap"])

                return 4

        if 8 < self._turn_count < 20:
            self.agent.search(self.dt * 2)
        else:
            self.agent.search(self.dt)

        move = self.agent.best_move()

        rollouts, nodes, _ = self.agent.statistics()
        move_str = self.agent.root_state.action_to_str(move)
        both_moves = [move_str, self.opponent_move] if self.player == 1 else [self.opponent_move, move_str]

        self.bench["rollouts"].append(rollouts)
        self.bench["nodes"].append(nodes)
        self.bench["moves"].append(both_moves)

        self.agent.move(move)

        if self.verbose:
            print("rollouts / nodes: ", self.agent.statistics())
            print(self.agent.root_state)


        if self.f:
            self.f.write(f"{move_str}\n")

        r, c = move
        msg = f"{r},{c}\n"

        self._s.sendall(bytes(msg, "utf-8"))

        return 4

    def _wait_message(self):
        """Waits for a new change message when it is not its turn."""

        self._turn_count += 1

        data = self._s.recv(1024).decode("utf-8").strip().split(";")

        if (data[0] == "END" or data[-1] == "END"):
            return 5

        if (data[1] == "SWAP"):
            if self._colour == "R":
                self._colour = "B"
                self.opponent_move = "swap"
                return 3

            self._colour = "R"
            if self.f:
                self.f.write("swap\n")

            return 4


        if data[-1] == self._colour:
            move = tuple(map(int, data[1].split(",")))
            self.agent.move(move)


            self.opponent_move = self.agent.root_state.action_to_str(move)
            if self.f:
                self.f.write(f"{self.agent.root_state.action_to_str(move)}\n")

            if (data[-1] == self._colour):
                return 3

        return 4

    def _close(self):
        """Closes the socket."""
        self._s.close()
        if self.f:
            self.f.close()

        return 0

    def opp_colour(self):
        """Returns the char representation of the colour opposite to the
        current one.
        """

        if self._colour == "R":
            return "B"
        elif self._colour == "B":
            return "R"
        else:
            return "None"


if (__name__ == "__main__"):
    agent = Agent()
    agent.run()
