# ✅ UPDATED Game2048.py (with correct __init__ syntax)
import time
import random
import copy

class Game2048:
    def __init__(self, b=None, s=None):
        if b:
            self._board = b
        else:
            self._board = [0] * 16

        if s:
            self._score = s
        else:
            self._score = 0

    def randomize(self):
        self._board = []
        for i in range(16):
            self._board.append(random.choice([0]*16 + [1]*4 + [2]*2 + [3]))

    def actions(self):
        return ''.join([a for a in 'UDLR' if self.move(a)._board != self._board])

    def result(self, a):
        s = self._score
        g = self.move(a)
        if g is None:
            return self, 0
        zeros = [i for i in range(16) if g._board[i] == 0]
        if not zeros:
            return g, g._score - s
        i = random.choice(zeros)
        g._board[i] = 2 if random.randint(0, 3) == 3 else 1
        return g, g._score - s

    def getScore(self):
        return self._score

    def getTile(self, r, c):
        return self._board[4*r+c]

    def possibleResults(self, a):
        s = self._score
        possible = []
        g = self.move(a)
        if g is None:
            return []
        zeros = [i for i in range(16) if g._board[i] == 0]
        for i in zeros:
            for t in [1, 2]:
                new_g = copy.deepcopy(g)
                new_g._board[i] = t
                prob = 0.75/len(zeros) if t == 1 else 0.25/len(zeros)
                possible.append((new_g, prob))
        return possible

    def possibleTiles(self):
        possible = []
        zeros = [i for i in range(16) if self._board[i] == 0]
        for i in zeros:
            for t in [1, 2]:
                possible.append((i, t))
        return possible

    def addTile(self, t, v):
        g = copy.deepcopy(self)
        g._board[t] = v
        return g

    def move(self, action):
        board = []
        s = self._score
        if action == 'R':
            for i in range(0, 16, 4):
                compressed = [t for t in self._board[i:i+4] if t != 0]
                j = len(compressed) - 1
                r = []
                while j >= 0:
                    if j > 0 and compressed[j] == compressed[j-1]:
                        s += 2*(2**compressed[j])
                        r.insert(0, compressed[j]+1)
                        j -= 2
                    else:
                        r.insert(0, compressed[j])
                        j -= 1
                r = [0] * (4-len(r)) + r
                board.extend(r)
            return Game2048(board, s)

        elif action == 'L':
            for i in range(0, 16, 4):
                compressed = [t for t in self._board[i:i+4] if t != 0]
                j = 0
                r = []
                while j < len(compressed):
                    if j < len(compressed)-1 and compressed[j] == compressed[j+1]:
                        s += 2*(2**compressed[j])
                        r.append(compressed[j]+1)
                        j += 2
                    else:
                        r.append(compressed[j])
                        j += 1
                r = r + [0] * (4-len(r))
                board.extend(r)
            return Game2048(board, s)

        elif action == 'D':
            return self._flip().move('R')._flip()

        elif action == 'U':
            return self._flip().move('L')._flip()

        else:
            print('ERROR move =', action)
            return None

    def _flip(self):
        r = []
        for i in range(4):
            r.extend(self._board[i:16:4])
        return Game2048(r, self._score)

    def rotate(self, numRotations):
        numRotations = numRotations % 4
        b = [0] * 16
        for r in range(4):
            for c in range(4):
                if numRotations == 0:
                    b[4*r + c] = self._board[4*r + c]
                elif numRotations == 1:
                    b[4*c + 3 - r] = self._board[4*r + c]
                elif numRotations == 2:
                    b[4*(3 - r) + (3 - c)] = self._board[4*r + c]
                elif numRotations == 3:
                    b[4*(3 - c) + r] = self._board[4*r + c]
        return Game2048(b, self._score)

    def gameOver(self):
        return self.actions() == '' or 16 in self._board

    def __str__(self):
        s = ''
        for r in range(0, 16, 4):
            s += ' '.join(f'{2**x}'.rjust(5) if x > 0 else '    .' for x in self._board[r:r+4]) + '\n'
        s += f'Score = {self._score}'
        return s


class BasePlayer:
    def __init__(self, timeLimit):
        self._timeLimit = timeLimit
        self._startTime = 0
        self._move = None

    def timeRemaining(self):
        return time.time() < self._startTime + self._timeLimit

    def setMove(self, move):
        if self.timeRemaining():
            self._move = move

    def getMove(self):
        return self._move

    def stats(self):
        pass

    def saveData(self, filename):
        pass

    def loadData(self, filename):
        pass
