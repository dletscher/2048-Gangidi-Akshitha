from Game2048 import *
import time

class Player(BasePlayer):
    def __init__(self, timeLimit):
        BasePlayer.__init__(self, timeLimit)
        self._startTime = 0
        self._maxDepth = 3

    def findMove(self, state):
        self._startTime = time.time()
        legalMoves = state.actions()

        bestMove = None
        bestScore = float('-inf')

        for move in legalMoves:
            result = state.move(move)
            if not self.timeRemaining():
                break
            if result is None:
                continue
            score = self.minValue(result, self._maxDepth - 1)
            if score is not None and score > bestScore:
                bestScore = score
                bestMove = move

        # ✅ SAFE fallback in case bestMove is still None
        if bestMove is None and legalMoves:
            print("[MyAgent] Fallback move:", legalMoves[0])
            bestMove = legalMoves[0]

        self.setMove(bestMove)

    def maxValue(self, state, depth):
        if state.gameOver() or depth == 0 or not self.timeRemaining():
            return state.getScore()

        value = float('-inf')
        for move in state.actions():
            result = state.move(move)
            if result is None:
                continue
            val = self.minValue(result, depth - 1)
            if val is None:
                return None
            value = max(value, val)
        return value

    def minValue(self, state, depth):
        if state.gameOver() or depth == 0 or not self.timeRemaining():
            return state.getScore()

        value = float('inf')
        for index, tile in state.possibleTiles():
            result = state.addTile(index, tile)
            val = self.maxValue(result, depth - 1)
            if val is None:
                return None
            value = min(value, val)
        return value


