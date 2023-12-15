from agents.grave import GRaveMctsAgent
from bridge_state import BridgeState
from game import GameMeta
from random import choice

class BridgetMctsAgent(GRaveMctsAgent):
    def roll_out(self, state):
        state = BridgeState(state)
        moves = state.moves()

        while state.bridge_winner() == GameMeta.PLAYERS["none"]:
            move = choice(moves)
            bridge_move = state.get_bridge(move,  3 - state.to_play)
            state.play(move)
            moves.remove(move)

            while bridge_move is not None:
                move = bridge_move
                bridge_move = state.get_bridge(move,  3 - state.to_play)
                state.play(move)
                moves.remove(move)

        rave_pts = {
            GameMeta.PLAYERS['white']: [],
            GameMeta.PLAYERS['black']: [],
        }


        for x in range(state.size):
            for y in range(state.size):
                if state.board[x, y]:
                    rave_pts[state.board[x, y]].append((x,y))

        return state.bridge_winner(), rave_pts
