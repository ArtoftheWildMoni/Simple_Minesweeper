import tkinter as tk
import math
import random
import logging #logging.warning(function name, lists, etc)
#examples
# logging.warning(f"reveal_cell: {i}, {j}")
# logging.warning(f"field: {field[j][i]}, {field}")
# logging.warning(f"reveal_cell: {y}, {x}")
# logging.warning(f"field: {field[y][x]}, {field}")

#LOG
#unable revealing of cell when a flag is placed.(DONE)
#remove flag when right click is done again on a flagged cell.(SOLVED)
#bombs turned to 0 (SOLVED)
#Flagged cell displaying the word flag instead of numbers (SOLVED)
#Flags disappearing upon opening any cell, resulting in "visiually unflagged" non openable cell. (Temporarily solved)
#flagged cells turning to 1 (SOLVED)
#game is successfully ending upon clicking bomb. But visually it doesn't show. (cells stay unopened, clicking unabled.)(SOLVED)
#clicking -1 doesn't reveal all cells (change this to reveal bomb cells)(SOLVED)
#Open bomb cells instead of empty cells upon game end (SOLVED)
#fix bomb graphic code placement error (SOLVED)

#ERRORS

#ToDO
#remove "flag" when game over or win
#reveal 0 adjacent cells function, adjust to open all 0 cells using a new coordinates function(NOT FIXED)

GAME_STATE = "progressing"
canvas = None


SQUARE_LENGTH = 30
RADIUS = SQUARE_LENGTH / 2 - 5
POSITION = {"x": 8, "y": 8}
BORDER_WIDTH = 2
NUMBER = 20
LENGTH = SQUARE_LENGTH * NUMBER + BORDER_WIDTH * NUMBER
MAX_NUM_FLAG = NUMBER

field = [[0 for _ in range(NUMBER)] for _ in range(NUMBER)]
revealed = [[False] * NUMBER for _ in range(NUMBER)]
flags = [[False] * NUMBER for _ in range(NUMBER)]


def initialize_mines():
   #bomb = -1
    global field
    field = [[0] * NUMBER for _ in range(NUMBER)]

    # Place mines randomly
    for _ in range(NUMBER):
        x = random.randint(0, NUMBER - 1)
        y = random.randint(0, NUMBER - 1)
        while field[y][x] == -1:
            x = random.randint(0, NUMBER - 1)
            y = random.randint(0, NUMBER - 1)
        field[y][x] = -1

def cell_counts():
    for y in range(NUMBER):
        for x in range(NUMBER):
            bombs_count = count_bombs(x, y)
            if field[y][x] != -1:
                field[y][x] = bombs_count
                
def set_field():
    canvas.create_rectangle(POSITION["x"], POSITION["y"], LENGTH + POSITION["x"], LENGTH + POSITION["y"], fill='#aaa', width=BORDER_WIDTH)

    for i in range(NUMBER):
        for j in range(NUMBER):
            set_item(None, i, j)  # Call set_item to render empty cell appearance

            x = POSITION["x"] + SQUARE_LENGTH * (i + 1) + BORDER_WIDTH * i + BORDER_WIDTH
            y = POSITION["y"] + SQUARE_LENGTH * (i + 1) + BORDER_WIDTH * i + BORDER_WIDTH
            canvas.create_line(x, POSITION["y"], x, LENGTH + POSITION["y"], width=BORDER_WIDTH)
            canvas.create_line(POSITION["x"], y, LENGTH + POSITION["x"], y, width=BORDER_WIDTH)
    
def set_item(kind, x, y):
    center_x = POSITION["x"] + BORDER_WIDTH * x + BORDER_WIDTH / 2 + SQUARE_LENGTH * x + SQUARE_LENGTH / 2
    center_y = POSITION["y"] + BORDER_WIDTH * y + BORDER_WIDTH / 2 + SQUARE_LENGTH * y + SQUARE_LENGTH / 2

    if revealed[y][x]:
        canvas.create_rectangle(center_x - SQUARE_LENGTH / 2, center_y - SQUARE_LENGTH / 2, center_x + SQUARE_LENGTH / 2, center_y + SQUARE_LENGTH / 2, fill="#fff", width=0)

        if kind != None:
            if kind == "bomb":
                canvas.create_oval(center_x - RADIUS, center_y - RADIUS, center_x + RADIUS, center_y + RADIUS, fill="#f00", width=0)
            else:
                canvas.create_text(center_x, center_y, text=kind, justify="center", font=("", 25), tag="count_text")
    else:
        canvas.create_rectangle(center_x - SQUARE_LENGTH / 2, center_y - SQUARE_LENGTH / 2, center_x + SQUARE_LENGTH / 2, center_y + SQUARE_LENGTH / 2, fill="#aaa", width=0)

def point_to_numbers(event_x, event_y):
    x = math.floor((event_x - POSITION["x"]) / (SQUARE_LENGTH + BORDER_WIDTH))
    y = math.floor((event_y - POSITION["y"]) / (SQUARE_LENGTH + BORDER_WIDTH))
    return x, y

def create_canvas():
   
    root = tk.Tk()
    root.geometry(f"{LENGTH + POSITION['x'] * 2}x{LENGTH + POSITION['y'] * 2}")
    root.title("Minesweeper")
    canvas = tk.Canvas(root, width=(LENGTH + POSITION['x']), height=(LENGTH + POSITION['y']))
    canvas.place(x=0, y=0)

    return root, canvas

def coordinates():
    coordinates = [ [0,-1], [1,-1], [1,0], [1,1], [0,1], [-1,1], [-1,0], [-1,-1] ]
    return coordinates

def count_bombs(x, y):
    bombs_count = 0
    hash_offsets = coordinates()

    for offset in hash_offsets:
        dx, dy = offset
        nx, ny = x + dx, y + dy
        
        if 0 <= nx < NUMBER and 0 <= ny < NUMBER and field[ny][nx] == -1:
            bombs_count += 1

    return bombs_count

def reveal_zero_adjacent_cells(x, y):

    four_coordinates = adjacent_cell_coordinates()

    # Now, recursively call reveal_zero_adjacent_cells for adjacent cells
    for dx, dy in four_coordinates:
        nx, ny = x + dx, y + dy
        if 0 <= nx < NUMBER and 0 <= ny < NUMBER:
            if flags[ny][nx]:
                clear_flag(nx, ny)  # Clear flag
            if not revealed[ny][nx] and field[ny][nx] == 0:
                revealed[ny][nx] = True
                set_item(None, nx, ny)
                reveal_zero_adjacent_cells(nx, ny)
            elif not revealed[ny][nx]:
                revealed[ny][nx] = True
                set_item(str(field[ny][nx]), nx, ny)  # Reveal the count of adjacent mines

        

def adjacent_cell_coordinates():
    four_coordinates = [ [0,-1], [1,0], [0,1], [-1,0] ]
    return four_coordinates

def reveal_cell(x, y):
    global GAME_STATE

    if revealed[y][x] or flags[y][x] or GAME_STATE == "lost":
        return

    revealed[y][x] = True
        
    if field[y][x] == -1:
        set_item("bomb", x, y)  # Set the bomb icon at the specified cell (x, y)
        end_game()
        GAME_STATE = "lost"
    elif field[y][x] == 0:
        set_item(None, x, y)

        reveal_zero_adjacent_cells(x, y)  # Or your reveal logic for non-bomb cells
    else:
        set_item(field[y][x], x, y)

    if check_win():
        end_game()
        GAME_STATE = "won"
    
    if revealed[y][x] and flags[y][x]:
        set_item(field[y][x], x, y)# Restore the original state of the cell


def check_win():
    """
    Check if the player has won the game.
    If all non-mine cells are revealed, set GAME_STATE to "won".
    """
    for y in range(NUMBER):
        for x in range(NUMBER):
            if field[y][x] != -1 and not revealed[y][x]:
                return False
    return True

def end_game():
    for y in range(NUMBER):
        for x in range(NUMBER):
            if flags[y][x]:
                flags[y][x] = False
                
    reveal_bomb_cells()

def reveal_bomb_cells():
    global revealed

    for y in range(NUMBER):
        for x in range(NUMBER):
            if field[y][x] == -1:
                reveal_cell(x, y)


def click(event):
    x, y = point_to_numbers(event.x, event.y)
    
    if event.num == 1:  # Left mouse button
        reveal_cell(x, y)
    elif event.num == 2:  # Right mouse button
        if flags[y][x]:
            remove_flag(x, y)  # Remove flag　
            logging.warning(f"remove_flag: {y}, {x}")
        else:
            place_flag(x, y)  # Place flag
        

def place_flag(x, y):
    global MAX_NUM_FLAG  # Use the global variable

    if revealed[y][x] or MAX_NUM_FLAG <= 0:
        return
    
    else:
        center_x = POSITION["x"] + BORDER_WIDTH * x + BORDER_WIDTH / 2 + SQUARE_LENGTH * x + SQUARE_LENGTH / 2
        center_y = POSITION["y"] + BORDER_WIDTH * y + BORDER_WIDTH / 2 + SQUARE_LENGTH * y + SQUARE_LENGTH / 2
        flags[y][x] = True
        MAX_NUM_FLAG -= 1

    flag_length = RADIUS
    flag_height = 8
    flagstick_x = center_x + RADIUS - flag_height
    flagstick_top = center_y + flag_length / 2
    polygon_top = center_y - flag_length / 2
    flagstick_bottom = center_y + flag_length / 2
    canvas.create_line(center_x, flagstick_top, flagstick_x, flagstick_top, fill="blue", width=15)  # Stick
    canvas.create_polygon(flagstick_x, flagstick_bottom, center_x + RADIUS, center_y, flagstick_x, polygon_top, fill="red")  # Flag


def toggle_flag(x, y):
    global MAX_NUM_FLAG  # Use the global variable

    if revealed[y][x]:
        return

    if flags[y][x]:
        clear_flag(x, y)
         # Increase the remaining number of flags
    elif MAX_NUM_FLAG > 0:
        place_flag(x, y)
          # Decrease the remaining number of flags

def remove_flag(x, y):
    if revealed[y][x] or not flags[y][x]:
        return
    
    global MAX_NUM_FLAG
    flags[y][x] = False
    MAX_NUM_FLAG += 1

    clear_flag_image(x, y) 

def clear_flag_image(x, y):
    center_x = POSITION["x"] + BORDER_WIDTH * x + BORDER_WIDTH / 2 + SQUARE_LENGTH * x + SQUARE_LENGTH / 2
    center_y = POSITION["y"] + BORDER_WIDTH * y + BORDER_WIDTH / 2 + SQUARE_LENGTH * y + SQUARE_LENGTH / 2

    canvas.create_rectangle(
        center_x - SQUARE_LENGTH / 2,
        center_y - SQUARE_LENGTH / 2,
        center_x + SQUARE_LENGTH / 2,
        center_y + SQUARE_LENGTH / 2,
        fill="#aaa",
        width=0
    )

    if field[y][x] == -1:
        set_item("bomb", x, y)
    elif field[y][x] != 0:
        set_item(str(field[y][x]), x, y)


def clear_flag(x, y):
    revealed[y][x] = False
    remove_flag(x, y)  # Call remove_flag to update the flags and flag count

#issue: Find a way to revert cell to a closed cell after flag removal. Not just the looks but the inner values too. 

def play():
    global canvas
    root, canvas = create_canvas()
    set_field()

    initialize_mines() 
    cell_counts() 

    canvas.bind("<Button-1>", lambda event: click(event))  # Left mouse button
    canvas.bind("<Button-2>", lambda event: click(event))  # Right mouse button
    root.mainloop()

play()
