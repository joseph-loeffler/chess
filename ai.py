import random
from board import Board

class ChessAI:

    def __init__(self, max_depth):
        self.max_depth = max_depth

    def choose_move(self, gameState: Board) -> tuple:
        """Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction. Prunes states using alpha-beta pruning."""
        def maxVal(gameState: Board, alpha: float, beta: float, depth: int) -> float:
            if depth >= self.max_depth:
                return self.state_eval(gameState)
            
            moves = gameState.get_all_legal_moves()
            first_move = next(moves, None)

            if first_move is None:
                # Terminal node: checkmate or draw
                return self.state_eval(gameState)

            maxV = float("-inf")
            for action in [first_move, *moves]:
                nextState = gameState.generate_successor_state(*action)
                maxV = max(maxV, minVal(nextState, alpha, beta, depth))

                if maxV >= beta:
                    return maxV

                alpha = max(alpha, maxV)

            return maxV

        def minVal(gameState: Board, alpha: float, beta: float, depth: int) -> float:
            moves = gameState.get_all_legal_moves()
            first_move = next(moves, None)

            if first_move is None:
                # Terminal node: checkmate or draw
                return self.state_eval(gameState)

            minV = float("inf")
            for action in [first_move, *moves]:
                nextState = gameState.generate_successor_state(*action)
                minV = min(minV, maxVal(nextState, alpha, beta, depth + 1))

                if minV <= alpha:
                    return minV

                beta = min(beta, minV)

            return minV
        
        bestVal = float("-inf")
        bestAct = None
        alpha, beta = float("-inf"), float("inf")
        for move in gameState.get_all_legal_moves():
            nextState = gameState.generate_successor_state(*move)
            val = minVal(nextState, alpha, beta, depth=1)
            if val > bestVal:
                bestVal = val
                bestAct = move
            alpha = max(alpha, bestVal)
        return bestAct


    def state_eval(self, gameState: Board) -> float:
        """Evaluates the current state based on a heuristic"""
        curr_color = "white" if gameState.ply % 2 == 0 else "black"
        opp_color =  "black" if gameState.ply % 2 == 0 else "white"
        if gameState.in_checkmate(curr_color):
            return float("-inf")
        if gameState.is_draw():
            return 0
        
        material = 0
        for piece in gameState.piece_map.values():
            if piece.color == curr_color:
                material += piece.value
            else:
                material -= piece.value
        
        move_flexibility = sum(len(moves) for moves in gameState.legal_moves.values())

        check = 0
        if gameState.in_check(curr_color):
            check = -1
        elif gameState.in_check(opp_color):
            check += 1

        return 3 * material + 2 * check + 1 * move_flexibility