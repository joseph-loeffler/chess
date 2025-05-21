from board import Board, log_debug

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
            before_move_key = gameState.compute_position_key()
            before_move_vis = gameState.get_board_visual()
            for action in [first_move, *moves]:
                # Get arguments for undoing the action later
                undo_arguments = [*action]
                pos = action[0]
                was_first_move = not gameState.piece_map[pos].has_moved
                undo_arguments.append(was_first_move)

                if gameState.is_capture(action):
                    capture_details = gameState.get_capture_details(action)
                    undo_arguments += capture_details

                # Make the move and evaluate it
                log_debug(f"[depth={depth}] MOVE: {action}, Key before: {before_move_key}")
                gameState.move(action)
                maxV = max(maxV, minVal(gameState, alpha, beta, depth))

                # Return board to prev state by undoing the move
                gameState.undo_move(*undo_arguments)
                after_undo_key = gameState.compute_position_key()
                after_undo_vis = gameState.get_board_visual()
                log_debug(f"[depth={depth}] UNDO: {action}, Key after: {after_undo_key}")
                assert before_move_key == after_undo_key, f"Undo failed at depth={depth}, ply={gameState.ply}. Keys: {before_move_key} != {after_undo_key}.\nBefore:\n{before_move_vis}\n\nAfter:\n{after_undo_vis}"

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
            before_move_key = gameState.compute_position_key()
            before_move_vis = gameState.get_board_visual()
            for action in [first_move, *moves]:
                # Get arguments for undoing the action later
                undo_arguments = [*action]
                pos = action[0]
                was_first_move = not gameState.piece_map[pos].has_moved
                undo_arguments.append(was_first_move)

                if gameState.is_capture(action):
                    capture_details = gameState.get_capture_details(action)
                    undo_arguments += capture_details

                # Make the move and evaluate it
                log_debug(f"[depth={depth}] MOVE: {action}, Key before: {before_move_key}")
                gameState.move(action)
                current_vis = gameState.get_board_visual()
                minV = min(minV, maxVal(gameState, alpha, beta, depth + 1))

                # Return board to prev state by undoing the move
                gameState.undo_move(*undo_arguments)
                after_undo_key = gameState.compute_position_key()
                after_undo_vis = gameState.get_board_visual()
                log_debug(f"[depth={depth}] UNDO: {action}, Key after: {after_undo_key}")
                assert before_move_key == after_undo_key, (
                    f"Undo failed at depth={depth}, ply={gameState.ply}. "
                    f"Keys: {before_move_key} != {after_undo_key}.\n"
                    f"Before:\n{before_move_vis}\n\n"
                    f"Move: {action}\n\n"
                    f"After move (before undo):\n{current_vis}\n\n"
                    f"After undo:\n{after_undo_vis}"
                )

                if minV <= alpha:
                    return minV

                beta = min(beta, minV)

            return minV
        
        bestVal = float("-inf")
        bestAct = None
        alpha, beta = float("-inf"), float("inf")
        for move in gameState.get_all_legal_moves():
            undo_arguments = [*move]
            pos = move[0]
            was_first_move = not gameState.piece_map[pos].has_moved
            undo_arguments.append(was_first_move)

            if gameState.is_capture(move):
                capture_details = gameState.get_capture_details(move)
                undo_arguments += capture_details

            before_move_key = gameState.compute_position_key()
            before_move_vis = gameState.get_board_visual()
            log_debug(f"[depth=0] MOVE: {move}, Key before: {before_move_key}")
            gameState.move(move)
            current_vis = gameState.get_board_visual()
            val = minVal(gameState, alpha, beta, depth=1)
            gameState.undo_move(*undo_arguments)
            after_undo_key = gameState.compute_position_key()
            after_undo_vis = gameState.get_board_visual()
            log_debug(f"[depth=0] UNDO: {move}, Key after: {after_undo_key}")
            assert before_move_key == after_undo_key, (
                f"Undo failed at depth=0, ply={gameState.ply}. "
                f"Keys: {before_move_key} != {after_undo_key}.\n"
                f"Before:\n{before_move_vis}\n\n"
                f"Move: {move}\n\n"
                f"After move (before undo):\n{current_vis}\n\n"
                f"After undo:\n{after_undo_vis}"
            )

            if val >= bestVal:
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

        check = 0
        if gameState.in_check(curr_color):
            check = -1
        elif gameState.in_check(opp_color):
            check += 1

        return 3 * material + check