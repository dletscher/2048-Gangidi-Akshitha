from Game2048 import BasePlayer
import time
import math

class Player(BasePlayer):
    def __init__(self, timeLimit):
        super().__init__(timeLimit)
        self.max_depth = 5
        self.last_move = 'L'

    def findMove(self, state):
        legal = state.actions()
        if not legal:
            self.setMove(self.last_move)
            return
        self.setMove(legal[0])  # initial default move

        start = time.time()
        time_limit = start + self._timeLimit - 0.15
        best_move = legal[0]
        best_score = float('-inf')

        for move in legal:
            next_state = state.move(move)
            if not next_state:
                continue
            score = self.minValue(next_state, 1, float('-inf'), float('inf'), time_limit)
            if score is None:
                break
            if score > best_score:
                best_score = score
                best_move = move

        self.last_move = best_move
        self.setMove(best_move)

    def maxValue(self, state, depth, alpha, beta, deadline):
        if time.time() >= deadline or depth == self.max_depth or state.gameOver():
            return self.evaluate(state)
        value = float('-inf')
        for move in state.actions():
            result = state.move(move)
            if not result:
                continue
            val = self.minValue(result, depth + 1, alpha, beta, deadline)
            if val is None:
                return None
            value = max(value, val)
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value

    def minValue(self, state, depth, alpha, beta, deadline):
        if time.time() >= deadline:
            return None
        total = 0
        count = 0
        for pos, val in state.possibleTiles():
            prob = 0.9 if val == 1 else 0.1
            next_state = state.addTile(pos, val)
            score = self.maxValue(next_state, depth, alpha, beta, deadline)
            if score is None:
                return None
            total += prob * score
            count += 1
        return total / count if count > 0 else self.evaluate(state)

    def evaluate(self, state):
        board = state._board
        empty = board.count(0)
        max_tile = max(board)
        smoothness = self.calc_smoothness(state)
        mono = self.calc_monotonicity(state)
        merges = self.merge_count(state)
        corner_val = state.getTile(0, 0)
        bonus = 100 if corner_val == max_tile else -100
        islands = self.islands(state)

        return (
            32 * empty +
            -4 * smoothness +
            12 * mono +
            25 * merges +
            2200 * math.log2(max_tile + 1) +
            bonus -
            18 * islands
        )

    def calc_smoothness(self, state):
        penalty = 0
        for i in range(4):
            for j in range(3):
                penalty += abs(state.getTile(i, j) - state.getTile(i, j+1))
        for j in range(4):
            for i in range(3):
                penalty += abs(state.getTile(i, j) - state.getTile(i+1, j))
        return penalty

    def calc_monotonicity(self, state):
        total = 0
        for i in range(4):
            row = [state.getTile(i, j) for j in range(4)]
            total += self.check_mono(row)
        for j in range(4):
            col = [state.getTile(i, j) for i in range(4)]
            total += self.check_mono(col)
        return total

    def check_mono(self, line):
        incr = decr = 0
        for i in range(3):
            if line[i] <= line[i+1]:
                incr += line[i+1] - line[i]
            else:
                decr += line[i] - line[i+1]
        return -min(incr, decr)

    def merge_count(self, state):
        count = 0
        for i in range(4):
            for j in range(3):
                if state.getTile(i, j) == state.getTile(i, j+1):
                    count += 1
        for j in range(4):
            for i in range(3):
                if state.getTile(i, j) == state.getTile(i+1, j):
                    count += 1
        return count

    def islands(self, state):
        isolated = 0
        for i in range(4):
            for j in range(4):
                val = state.getTile(i, j)
                if val == 0:
                    continue
                neighbors = 0
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < 4 and 0 <= nj < 4 and state.getTile(ni, nj) != 0:
                        neighbors += 1
                if neighbors == 0:
                    isolated += 1
        return isolated
