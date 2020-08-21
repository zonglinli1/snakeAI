#!/usr/bin/env python
import curses
from random import randint

# field size 
HEIGHT = 10 
WIDTH = 20
FIELD_SIZE = HEIGHT * WIDTH
HEAD = 0
FOOD = 0
UNDEFINED = FIELD_SIZE 
SNAKE = 2 * UNDEFINED
# 1D array represent the board 
# snake head start at pos (1,1) and has length 1
food = 3 * WIDTH + 3
board = [0] * FIELD_SIZE
snake = [0] * (FIELD_SIZE+1)
snake[HEAD] = 1*WIDTH+1
snake_size = 1
# move
LEFT = -1
RIGHT = 1
UP = -WIDTH
DOWN = WIDTH
mov = [LEFT, RIGHT, UP, DOWN]
ERR = -1111
# temp
tmpboard = [0] * FIELD_SIZE
tmpsnake = [0] * (FIELD_SIZE+1)
tmpsnake[HEAD] = 1*WIDTH+1
tmpsnake_size = 1


def is_move_possible(idx, move):
    if move == LEFT:
        return idx%WIDTH > 1
    elif move == RIGHT:
        return idx%WIDTH < (WIDTH-2) 
    elif move == UP:
        return idx > (2*WIDTH-1) 
    elif move == DOWN:
        return idx < (FIELD_SIZE-2*WIDTH)
    
# BFS search the board，and mark len of the path to food for every cell
def board_refresh(pfood, psnake, pboard):
    queue = []
    queue.append(pfood)
    inqueue = [0] * FIELD_SIZE
    found = False
    while len(queue)!=0: 
        idx = queue.pop(0)
        if inqueue[idx] != 1:
            inqueue[idx] = 1
            for i in range(4):
                if is_move_possible(idx, mov[i]):
                    if idx + mov[i] == psnake[HEAD]:
                        found = True
                    if pboard[idx+mov[i]] < SNAKE: 
                        if pboard[idx+mov[i]] > pboard[idx]+1:
                            pboard[idx+mov[i]] = pboard[idx] + 1
                        if inqueue[idx+mov[i]] == 0:
                            queue.append(idx+mov[i])
    return found

# after board_refresh all cell of the board contain the length to food
# reset path len to undefined
def board_reset(psnake, psize, pboard):
    for i in range(FIELD_SIZE): 
        if i == food:
            pboard[i] = FOOD
        elif not (i in psnake[:psize]):
            pboard[i] = UNDEFINED
        else: 
            pboard[i] = SNAKE

def choose_shortest_safe_move(psnake, pboard):
    best_move = ERR
    min = float('inf')
    for i in range(4):
        if is_move_possible(psnake[HEAD], mov[i]) and pboard[psnake[HEAD]+mov[i]]<min:
            min = pboard[psnake[HEAD]+mov[i]]
            best_move = mov[i]
    return best_move

def choose_longest_safe_move(psnake, pboard):
    best_move = ERR
    max = -1
    for i in range(4):
        if is_move_possible(psnake[HEAD], mov[i]) and pboard[psnake[HEAD]+mov[i]]<UNDEFINED and pboard[psnake[HEAD]+mov[i]]>max:
            max = pboard[psnake[HEAD]+mov[i]]
            best_move = mov[i]
    return best_move

# avoid impasse
def temp_is_tail_inside():
    global tmpboard, tmpsnake, food, tmpsnake_size
    tmpboard[tmpsnake[tmpsnake_size-1]] = FOOD 
    tmpboard[food] = SNAKE 
    result = board_refresh(tmpsnake[tmpsnake_size-1], tmpsnake, tmpboard) 
    for i in range(4): 
        if is_move_possible(tmpsnake[HEAD], mov[i]) and tmpsnake[HEAD]+mov[i]==tmpsnake[tmpsnake_size-1] and tmpsnake_size>3:
            result = False
    return result

def follow_tail():
    global tmpboard, tmpsnake, food, tmpsnake_size
    tmpsnake_size = snake_size
    tmpsnake = snake[:]
    board_reset(tmpsnake, tmpsnake_size, tmpboard) 
    tmpboard[tmpsnake[tmpsnake_size-1]] = FOOD # make tail to food 
    tmpboard[food] = SNAKE # avoid food 
    board_refresh(tmpsnake[tmpsnake_size-1], tmpsnake, tmpboard) # bfs
    tmpboard[tmpsnake[tmpsnake_size-1]] = SNAKE # reset tail 
    return choose_longest_safe_move(tmpsnake, tmpboard) 

# try any possible move
def any_possible_move():
    global food , snake, snake_size, board
    best_move = ERR
    board_reset(snake, snake_size, board)
    board_refresh(food, snake, board)
    min = SNAKE
    for i in range(4):
        if is_move_possible(snake[HEAD], mov[i]) and board[snake[HEAD]+mov[i]]<min:
            min = board[snake[HEAD]+mov[i]]
            best_move = mov[i]
    return best_move

def new_food():
    global food, snake_size
    cell_free = False
    while not cell_free:
        w = randint(1, WIDTH-2)
        h = randint(1, HEIGHT-2)
        food = h * WIDTH + w
        cell_free = not (food in snake[:snake_size])
    win.addch(food//WIDTH, food%WIDTH, '@')

def make_move(pbest_move):
    global snake, board, snake_size
    for i in range(snake_size, 0, -1):
        snake[i] = snake[i-1]
    snake[HEAD] += pbest_move

    win.getch()
    p = snake[HEAD]
    win.addch(p//WIDTH, p%WIDTH, '*')
    
    if snake[HEAD] == food:
        board[snake[HEAD]] = SNAKE # new head 
        snake_size += 1
        if snake_size < FIELD_SIZE: 
            new_food()
    else:
        board[snake[HEAD]] = SNAKE # new head
        board[snake[snake_size]] = UNDEFINED 
        win.addch(snake[snake_size]//WIDTH, snake[snake_size]%WIDTH, ' ')

# try shortest move to food
def virtual_shortest_move():
    global snake, board, snake_size, tmpsnake, tmpboard, tmpsnake_size, food
    tmpsnake_size = snake_size
    tmpsnake = snake[:] 
    tmpboard = board[:] 
    board_reset(tmpsnake, tmpsnake_size, tmpboard)
    
    ate = False
    while not ate:
        board_refresh(food, tmpsnake, tmpboard)    
        move = choose_shortest_safe_move(tmpsnake, tmpboard)
        for i in range(tmpsnake_size, 0, -1):
            tmpsnake[i] = tmpsnake[i-1]
        tmpsnake[HEAD] += move 

        if tmpsnake[HEAD] == food:
            tmpsnake_size += 1
            board_reset(tmpsnake, tmpsnake_size, tmpboard) 
            tmpboard[food] = SNAKE
            ate = True
        else: 
            tmpboard[tmpsnake[HEAD]] = SNAKE
            tmpboard[tmpsnake[tmpsnake_size]] = UNDEFINED

def find_safe_way():
    global snake, board
    safe_move = ERR
    virtual_shortest_move() 
    if temp_is_tail_inside():
        return choose_shortest_safe_move(snake, board)
    safe_move = follow_tail() 
    return safe_move


curses.initscr()
win = curses.newwin(HEIGHT, WIDTH, 0, 0)
curses.noecho()
curses.curs_set(0)
win.border(0)
win.nodelay(1)
win.addch(food//WIDTH, food%WIDTH, '@')

while snake_size < (((WIDTH - 2) * (HEIGHT - 2)) - 1):
    win.border(0)
    win.timeout(20)

    board_reset(snake, snake_size, board)

    if board_refresh(food, snake, board):
        best_move  = find_safe_way() 
    else:
        best_move = follow_tail()

    if best_move == ERR:
        best_move = any_possible_move()

    if best_move != ERR: 
        make_move(best_move) 
    else: break        
curses.endwin()