import curses
import random
from curses import wrapper

SIZE = 4

def new_board():
    return [[0]*SIZE for _ in range(SIZE)]

def add_random(board):
    empties = [(r,c) for r in range(SIZE) for c in range(SIZE) if board[r][c]==0]
    if not empties: return False
    r,c = random.choice(empties)
    board[r][c] = 4 if random.random() < 0.1 else 2
    return True

def transpose(b):
    return [list(row) for row in zip(*b)]

def reverse_rows(b):
    return [list(reversed(row)) for row in b]

def compress_merge_row(row):
    new = [v for v in row if v!=0]
    score = 0
    i = 0
    merged = []
    while i < len(new):
        if i+1 < len(new) and new[i] == new[i+1]:
            merged.append(new[i]*2)
            score += new[i]*2
            i += 2
        else:
            merged.append(new[i])
            i += 1
    merged += [0]*(SIZE - len(merged))
    moved = merged != row
    return merged, moved, score

def move_left(board):
    moved_any = False
    score_gain = 0
    newb = []
    for row in board:
        nr, moved, gain = compress_merge_row(row)
        newb.append(nr)
        moved_any |= moved
        score_gain += gain
    return newb, moved_any, score_gain

def move(board, direction):
    # direction: 'left','right','up','down'
    if direction == 'left':
        return move_left(board)
    if direction == 'right':
        rb = reverse_rows(board)
        movedb, moved, score = move_left(rb)
        return reverse_rows(movedb), moved, score
    if direction == 'up':
        tb = transpose(board)
        movedb, moved, score = move_left(tb)
        return transpose(movedb), moved, score
    if direction == 'down':
        tb = transpose(board)
        rb = reverse_rows(tb)
        movedb, moved, score = move_left(rb)
        return transpose(reverse_rows(movedb)), moved, score

def can_move(board):
    for r in range(SIZE):
        for c in range(SIZE):
            v = board[r][c]
            if v == 0:
                return True
            for dr,dc in ((1,0),(0,1)):
                nr, nc = r+dr, c+dc
                if 0<=nr<SIZE and 0<=nc<SIZE and board[nr][nc] == v:
                    return True
    return False

def draw(stdscr, board, score):
    stdscr.clear()
    h,w = stdscr.getmaxyx()
    title = " 2048 (q: quit) "
    stdscr.addstr(0, max(0,(w-len(title))//2), title, curses.A_BOLD)
    stdscr.addstr(1, 0, f"Score: {score}")
    cell_w = 7
    top = 3
    left = max(0, (w - (cell_w*SIZE))//2)
    for r in range(SIZE):
        for c in range(SIZE):
            val = board[r][c]
            s = str(val) if val!=0 else ""
            x = left + c*cell_w
            y = top + r*2
            box = "[" + s.center(cell_w-2) + "]"
            try:
                stdscr.addstr(y, x, box)
            except curses.error:
                pass
    stdscr.refresh()

def game_loop(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)
    random.seed()
    board = new_board()
    add_random(board)
    add_random(board)
    score = 0

    draw(stdscr, board, score)

    while True:
        ch = stdscr.getch()
        if ch in (ord('q'), ord('Q')):
            break
        mapping = {
            curses.KEY_LEFT: 'left',
            curses.KEY_RIGHT: 'right',
            curses.KEY_UP: 'up',
            curses.KEY_DOWN: 'down',
            ord('a'): 'left', ord('A'): 'left',
            ord('d'): 'right', ord('D'): 'right',
            ord('w'): 'up', ord('W'): 'up',
            ord('s'): 'down', ord('S'): 'down',
        }
        if ch not in mapping:
            continue
        direction = mapping[ch]
        newb, moved, gain = move(board, direction)
        if moved:
            board = newb
            score += gain
            add_random(board)
            draw(stdscr, board, score)
            if not can_move(board):
                draw(stdscr, board, score)
                msg = " GAME OVER - press r to restart or q to quit "
                h,w = stdscr.getmaxyx()
                stdscr.addstr(min(h-1, SIZE*2+5), max(0,(w-len(msg))//2), msg, curses.A_REVERSE)
                stdscr.refresh()
                while True:
                    ch2 = stdscr.getch()
                    if ch2 in (ord('q'), ord('Q')):
                        return
                    if ch2 in (ord('r'), ord('R')):
                        board = new_board()
                        add_random(board); add_random(board)
                        score = 0
                        draw(stdscr, board, score)
                        break

def main(stdscr):
    try:
        game_loop(stdscr)
    except Exception as e:
        curses.endwin()
        print("Error:", e)

if __name__ == "__main__":
    wrapper(main)