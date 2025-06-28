from Game2048 import BasePlayer
import time
import math
import random

class Player(BasePlayer):
    def __init__(self, timeLimit):
        BasePlayer.__init__(self, timeLimit)
        self._weights = {
            'empty': 35.0,
            'smoothness': 6.0,
            'monotonicity': 12.0,
            'max_tile': 2500.0,
            'corner': 150.0,
            'merge_potential': 25.0,
            'island_penalty': 15.0
        }
        self._last_valid_move = 'L'
        self._search_depth = 7

    def findMove(self, state):
        self.setMove(state.actions()[0]) 
        start_time = time.time()
        deadline = start_time + self._timeLimit - 0.15

        valid_moves = state.actions()
        if not valid_moves:
            self.setMove('L')
            return

        best_move = self._get_best_fallback_move(state, valid_moves)
        best_score = -float('inf')
        depth = 1

        while time.time() < deadline and depth <= self._search_depth:
            current_best = None
            current_score = -float('inf')

            for move in self._order_moves(state, valid_moves):
                if time.time() >= deadline:
                    break

                new_state = state.move(move)
                if not new_state:
                    continue

                score = self._expectimax(new_state, depth-1, False, deadline)
                if score is None:
                    continue

                if score > current_score:
                    current_score = score
                    current_best = move

            if current_best is not None:
                best_move = current_best
                best_score = current_score
                self._last_valid_move = best_move
                depth += 1
            else:
                break

        if best_move not in valid_moves:
            best_move = self._last_valid_move if self._last_valid_move in valid_moves else valid_moves[0]

        self.setMove(best_move)

    def _expectimax(self, state, depth, isMax, deadline):
        if time.time() >= deadline:
            return None

        if state.gameOver():
            return -1000000

        if depth == 0:
            return self._evaluate(state)

        if isMax:
            value = -float('inf')
            for move in state.actions():
                new_state = state.move(move)
                if not new_state:
                    continue
                result = self._expectimax(new_state, depth-1, False, deadline)
                if result is None:
                    return None
                value = max(value, result)
            return value
        else:
            possible_tiles = state.possibleTiles()
            if not possible_tiles:
                return self._evaluate(state)

            total = 0.0
            count = 0
            for pos, val in possible_tiles:
                if time.time() >= deadline:
                    return None
                new_state = state.addTile(pos, val)
                prob = 0.9 if val == 1 else 0.1
                result = self._expectimax(new_state, depth-1, True, deadline)
                if result is None:
                    return None
                total += prob * result
                count += 1

            return total / count if count > 0 else 0

    def _evaluate(self, state):
        if state.gameOver():
            return -1000000

        empty = sum(1 for i in range(16) if state._board[i] == 0)
        max_tile = max(state._board)

        smoothness = 0
        for i in range(4):
            for j in range(3):
                smoothness -= abs(state.getTile(i, j) - state.getTile(i, j+1))
        for j in range(4):
            for i in range(3):
                smoothness -= abs(state.getTile(i, j) - state.getTile(i+1, j))

        mono = 0
        for i in range(4):
            row = [state.getTile(i, j) for j in range(4)]
            mono += self._monotonicity(row)
        for j in range(4):
            col = [state.getTile(i, j) for i in range(4)]
            mono += self._monotonicity(col)

        corner = state.getTile(0, 0)
        corner_bonus = self._weights['corner'] * math.log2(corner + 1) if corner == max_tile else -100.0

        merge_pot = sum(
            1 for i in range(4)
            for j in range(3)
            if state.getTile(i, j) == state.getTile(i, j+1))
        merge_pot += sum(
            1 for j in range(4)
            for i in range(3)
            if state.getTile(i, j) == state.getTile(i+1, j))

        islands = self._count_islands(state)

        return (
            empty * self._weights['empty'] +
            smoothness * self._weights['smoothness'] +
            mono * self._weights['monotonicity'] +
            math.log2(max_tile + 1) * self._weights['max_tile'] +
            corner_bonus +
            merge_pot * self._weights['merge_potential'] -
            islands * self._weights['island_penalty']
        )

    def _order_moves(self, state, moves):
        scored = []
        for move in moves:
            new_state = state.move(move)
            if not new_state:
                continue

            empty = sum(1 for i in range(16) if new_state._board[i] == 0)
            merges = sum(
                1 for i in range(4)
                for j in range(3)
                if new_state.getTile(i, j) == new_state.getTile(i, j+1))
            merges += sum(
                1 for j in range(4)
                for i in range(3)
                if new_state.getTile(i, j) == new_state.getTile(i+1, j))

            corner_bonus = 50 if new_state.getTile(0, 0) == max(new_state._board) else 0

            scored.append((empty * 5 + merges * 20 + corner_bonus, move))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [move for (score, move) in scored]

    def _monotonicity(self, sequence):
        if len(sequence) < 2:
            return 0

        inc = dec = 0
        for i in range(len(sequence) - 1):
            diff = sequence[i] - sequence[i + 1]
            if diff > 0:
                dec += diff
            else:
                inc -= diff

        return max(inc, dec) - min(inc, dec)

    def _count_islands(self, state):
        islands = 0
        for i in range(4):
            for j in range(4):
                if state.getTile(i, j) == 0:
                    continue
                neighbors = 0
                if i > 0 and state.getTile(i - 1, j) != 0:
                    neighbors += 1
                if i < 3 and state.getTile(i + 1, j) != 0:
                    neighbors += 1
                if j > 0 and state.getTile(i, j - 1) != 0:
                    neighbors += 1
                if j < 3 and state.getTile(i, j + 1) != 0:
                    neighbors += 1
                if neighbors == 0:
                    islands += 1
        return islands

    def _get_best_fallback_move(self, state, moves):
        best_merge = moves[0]
        max_merge = -1
        for move in moves:
            new_state = state.move(move)
            if new_state:
                merges = sum(
                    1 for i in range(4)
                    for j in range(3)
                    if new_state.getTile(i, j) == new_state.getTile(i, j + 1))
                merges += sum(
                    1 for j in range(4)
                    for i in range(3)
                    if new_state.getTile(i, j) == new_state.getTile(i + 1, j))
                if merges > max_merge:
                    max_merge = merges
                    best_merge = move

        best_corner = moves[0]
        for move in moves:
            new_state = state.move(move)
            if new_state and new_state.getTile(0, 0) == max(new_state._board):
                best_corner = move
                break

        return best_merge if max_merge > 0 else best_corner
