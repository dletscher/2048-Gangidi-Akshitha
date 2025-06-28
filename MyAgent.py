from Game2048 import BasePlayer
import math
import time

class Player(BasePlayer):
    def __init__(self, timeLimit):
        super().__init__(timeLimit)
        self._weights = {
            'empty': 100,
            'merge': 40,
            'monotonicity': 20,
            'max_tile': 2500,
            'corner': 500
        }
        self.last_move = 'L'

    def findMove(self, state):
        legal = state.actions()
        if not legal:
            self.setMove(self.last_move)
            return

        self.setMove(legal[0])  # fail-safe

        best_move = legal[0]
        best_score = float('-inf')

        for move in self._order_moves(state, legal):
            new_state = state.move(move)
            if not new_state:
                continue
            score = self.evaluate(new_state)
            if score > best_score:
                best_score = score
                best_move = move

        self.last_move = best_move
        self.setMove(best_move)

    def evaluate(self, state):
        board = state._board
        empty = board.count(0)
        merges = self.count_merges(state)
        mono = self.monotonicity(state)
        max_tile = max(board)
        corner_bonus = self._weights['corner'] if state.getTile(0, 0) == max_tile else -200

        return (
            self._weights['empty'] * empty +
            self._weights['merge'] * merges +
            self._weights['monotonicity'] * mono +
            self._weights['max_tile'] * math.log2(max_tile + 1) +
            corner_bonus
        )

    def count_merges(self, state):
        count = 0
        for i in range(4):
            for j in range(3):
                if state.getTile(i, j) == state.getTile(i, j + 1):
                    count += 1
        for j in range(4):
            for i in range(3):
                if state.getTile(i, j) == state.getTile(i + 1, j):
                    count += 1
        return count

    def monotonicity(self, state):
        score = 0
        for i in range(4):
            row = [state.getTile(i, j) for j in range(4)]
            score += self._mono_score(row)
        for j in range(4):
            col = [state.getTile(i, j) for i in range(4)]
            score += self._mono_score(col)
        return score

    def _mono_score(self, line):
        inc, dec = 0, 0
        for i in range(3):
            if line[i] <= line[i+1]:
                inc += line[i+1] - line[i]
            else:
                dec += line[i] - line[i+1]
        return -min(inc, dec)

    def _order_moves(self, state, moves):
        ordered = []
        for move in moves:
            new_state = state.move(move)
            if not new_state:
                continue
            empty = new_state._board.count(0)
            corner = 1 if new_state.getTile(0, 0) == max(new_state._board) else 0
            score = empty * 10 + corner * 50
            ordered.append((score, move))
        ordered.sort(reverse=True)
        return [m for _, m in ordered]
