import socket
from random import choice
from time import sleep
from agents.uct import UctMctsAgent
from agents.grave import GRaveMctsAgent

class Agent():
    HOST = "127.0.0.1"
    PORT = 1234

    def run(self):
        """A finite-state machine that cycles through waiting for input
        and sending moves.
        """

        self._board_size = 0
        self._board = []
        self._colour = ""
        self._turn_count = 1
        self._choices = []
        self.agent = GRaveMctsAgent()
        self.player = 0
        with open("moves.txt", "w") as _:
            pass
        self.f = open("moves.txt", "a")

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
                self.player = 1
                return 3
            else:
                self.player = -1
                return 4

        else:
            print("ERROR: No START message received.")
            return 0

    def _make_move(self):
        """Makes a random valid move. It will choose to swap with
        a coinflip.
        """
        self.agent.search(3)
        move = self.agent.best_move()
        self.agent.move(move)
        self.f.write(f"{self.agent.root_state.action_to_str(move)}\n")
        print("Tree size", self.agent.tree_size())
        print("rollouts / nodes: ", self.agent.statistics())

        if move == 121:
            msg = "SWAP\n"
        else:
            r, c = move // 11, move % 11
            msg = f"{r},{c}\n"

        self._s.sendall(bytes(msg, "utf-8"))

        return 4

    def _wait_message(self):
        """Waits for a new change message when it is not its turn."""

        self._turn_count += 1

        data = self._s.recv(1024).decode("utf-8").strip().split(";")

        if (data[0] == "END" or data[-1] == "END"):
            return 5
        elif data[-1] == self._colour:
            if (data[1] == "SWAP"):
                self.agent.move(121)
                self.f.write("swap\n")
            else:
                r, c = [*map(int, data[1].split(","))]
                move = r * 11 + c
                self.agent.move(move)
                self.f.write(f"{self.agent.root_state.action_to_str(move)}\n")

            if (data[-1] == self._colour):
                return 3

        return 4

    def _close(self):
        """Closes the socket."""

        self._s.close()
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
