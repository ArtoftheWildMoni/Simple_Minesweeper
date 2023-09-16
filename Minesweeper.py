import logging  # logging.warning(function name, lists, etc)
import math
import random
import tkinter as tk

GAME_STATE = "start"
canvas = None

SQUARE_LENGTH = 30
RADIUS = SQUARE_LENGTH / 2 - 5
POSITION = {"x": 8, "y": 8}
BORDER_WIDTH = 2
NUMBER = 20
LENGTH = SQUARE_LENGTH * NUMBER + BORDER_WIDTH * NUMBER
MAX_NUM_FLAG = 40
BOMBS_COUNT = 40

field = [[0 for _ in range(NUMBER)] for _ in range(NUMBER)]
opened = [[False] * NUMBER for _ in range(NUMBER)]
flags = [[False] * NUMBER for _ in range(NUMBER)]

def initialize_mines():
  # bomb = -1
  global field
  field = [[0] * NUMBER for _ in range(NUMBER)]

  # Place mines randomly
  for _ in range(BOMBS_COUNT):
    x = random.randint(0, NUMBER - 1)
    y = random.randint(0, NUMBER - 1)
    while field[y][x] == -1:
      x = random.randint(0, NUMBER - 1)
      y = random.randint(0, NUMBER - 1)
    field[y][x] = -1
    logging.warning(f"bombs placed: {y}, {x}")

def set_field():
  canvas.create_rectangle(POSITION["x"], POSITION["y"], LENGTH + POSITION["x"], LENGTH + POSITION["y"], fill='#aaa', width=BORDER_WIDTH)

  for i in range(NUMBER):
    for j in range(NUMBER):
      # Call set_item to render empty cell appearance
      set_item(None, i, j)

      x = POSITION["x"] + SQUARE_LENGTH * (i + 1) + BORDER_WIDTH * i + BORDER_WIDTH
      y = POSITION["y"] + SQUARE_LENGTH * (i + 1) + BORDER_WIDTH * i + BORDER_WIDTH
      canvas.create_line(x, POSITION["y"], x, LENGTH + POSITION["y"], width=BORDER_WIDTH)
      canvas.create_line(POSITION["x"], y, LENGTH + POSITION["x"], y, width=BORDER_WIDTH)

def set_item(kind, x, y):
  center_x = POSITION["x"] + BORDER_WIDTH * x + BORDER_WIDTH / 2 + SQUARE_LENGTH * x + SQUARE_LENGTH / 2
  center_y = POSITION["y"] + BORDER_WIDTH * y + BORDER_WIDTH / 2 + SQUARE_LENGTH * y + SQUARE_LENGTH / 2

  if opened[y][x]:
    canvas.create_rectangle(center_x - SQUARE_LENGTH / 2, center_y - SQUARE_LENGTH / 2, center_x + SQUARE_LENGTH / 2, center_y + SQUARE_LENGTH / 2, fill="#fff", width=0)
    # 開けたますの色が白だと文字の色と被って何も見えないので黒に変更

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
  canvas = tk.Canvas(root, width=(
    LENGTH + POSITION['x']), height=(LENGTH + POSITION['y']))
  canvas.place(x=0, y=0)

  return root, canvas

def get_eight_cells():
    return [[0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1]]

def cell_counts():
  # fieldはグローバル変数だから呼び出す時はいいけど代入する時は下のコードを入れないと関数内のローカル変数に代入されて変更が反映されない
  global field
  for y in range(NUMBER):
    for x in range(NUMBER):
      bombs_count = count_bombs(x, y)
      if field[y][x] != -1:
        field[y][x] = bombs_count

def count_bombs(x, y, first_click=False):
  bombs_count = 0
  cells_around = get_eight_cells()

  for offset in cells_around:
    dx, dy = offset
    nx, ny = x + dx, y + dy

    if 0 <= nx < NUMBER and 0 <= ny < NUMBER:
      if first_click and field[ny][nx] == -1:
        # Ensure the first click cell is not a bomb
        return 0
      if field[ny][nx] == -1:
        bombs_count += 1

  return bombs_count

def open_zero_around_cells(x, y):
  eight_cells = get_eight_cells()

  for dx, dy in eight_cells:
    nx, ny = x + dx, y + dy
    if 0 <= nx < NUMBER and 0 <= ny < NUMBER:
      # 爆弾のますに対しては何もしないようにしないと爆弾のますの旗が消えてしまう
      if not field[ny][nx] == -1 and not opened[ny][nx]:
        if flags[ny][nx]:
          clear_flag(nx, ny)  # Clear flag
        opened[ny][nx] = True
        if field[ny][nx] == 0:
          set_item(None, nx, ny)
          open_zero_around_cells(nx, ny)
        else:
          set_item(str(field[ny][nx]), nx, ny)

def open_cell(x, y):
    global GAME_STATE
    global opened

    if opened[y][x] or flags[y][x] or GAME_STATE == "lost":
        return

    if GAME_STATE == "start":
        logging.warning("Before moving bombs")
        move_bombs(x, y)
        logging.warning("After moving bombs")
        GAME_STATE = "progressing"

    # ここでopenにすると爆弾か確認する前にロジック上は開いてしまう？
    opened[y][x] = True

    bombs_around_cell = count_bombs(x, y, first_click=(GAME_STATE == "start"))

    # この条件式だと押したところが爆弾でも周りに爆弾がない限りNoneのマスが開かれる
    # if bombs_around_cell == 0:
    if bombs_around_cell == 0 and field[y][x] != -1:
        set_item(None, x, y)
        open_zero_around_cells(x, y)
    elif field[y][x] == -1:
        set_item("bomb", x, y)
        end_game()
        GAME_STATE = "lost"
    else:
        set_item(field[y][x], x, y)

    check_win()
    if GAME_STATE == "won":
        print("Game Clear")

    if opened[y][x] and flags[y][x]:
        set_item(field[y][x], x, y)  # Restore the original state of the cell

def move_bombs(x, y):
  global field
  logging.warning(f"clicked positions: {x}, {y}")
  # Step 1: Find the bombs in adjacent cells
  check_cells = get_eight_cells()  # Get the adjacent cell coordinates
  check_cells.append([0, 0])
  adjacent_bombs = []  # Initialize a list to store bombs in adjacent cells

  coordinates = []
  for dx, dy in check_cells:
    nx, ny = x + dx, y + dy
    coordinates.append([nx, ny])

    if 0 <= nx < NUMBER and 0 <= ny < NUMBER and field[ny][nx] == -1:
      adjacent_bombs.append((nx, ny))

  # Step 2: Remove the bombs from their current positions (both visually and logically)
  for bomb_x, bomb_y in adjacent_bombs:
    field[bomb_y][bomb_x] = 0  # Clear the bomb from the logical field
    # set_item(None, bomb_x, bomb_y)  # Clear the bomb visually
    # この時点では表示はする必要ない

  logging.warning(f"bombs need to move positions: {adjacent_bombs}")

  # Step 3: Generate new positions for the bombs
  new_bomb_positions = generate_new_bomb_positions(adjacent_bombs, x, y, coordinates)

  # Step 4: Place the bombs in their new positions (both visually and logically)
  for new_x, new_y in new_bomb_positions:
    field[new_y][new_x] = -1  # Set the bomb in the logical field
    # set_item("bomb", new_x, new_y)  # Display the bomb visually
    # この時点では表示はする必要ない
    logging.warning(f"new bomb positions: {new_y}, {new_x}")

  # 数を数え直す
  cell_counts()

def generate_new_bomb_positions(adjacent_bombs, clicked_x, clicked_y, coordinates):
  new_bomb_positions = []
  # Define the range of valid positions
  valid_positions = [(x, y) for x in range(NUMBER) for y in range(NUMBER) if not [x, y] in coordinates and field[y][x] != -1]
  # Shuffle the valid positions randomly
  random.shuffle(valid_positions)
  print("regenerated")
  # Take the first N valid positions to place the bombs
  for i in range(len(adjacent_bombs)):
    if i < len(valid_positions):
      new_bomb_positions.append(valid_positions[i])
      logging.warning(f"New bomb position: ({valid_positions[i][0]}, {valid_positions[i][1]})")

  return new_bomb_positions

def check_win():
  """
  Check if the player has won the game.
  If all non-mine cells are opened, set GAME_STATE to "won".
  """
  for y in range(NUMBER):
    for x in range(NUMBER):
        if field[y][x] != -1 and not opened[y][x]:
            return
  global GAME_STATE
  GAME_STATE = "won"

def end_game():
  global flags
  for y in range(NUMBER):
    for x in range(NUMBER):
        if flags[y][x]:
            flags[y][x] = False

  open_bomb_cells()

def open_bomb_cells():
  for y in range(NUMBER):
      for x in range(NUMBER):
          if field[y][x] == -1:
              open_cell(x, y)

def click(event):
  x, y = point_to_numbers(event.x, event.y)

  if event.num == 1:  # Left mouse button
    open_cell(x, y)
  elif event.num == 2:  # Right mouse button
    if flags[y][x]:
      remove_flag(x, y)  # Remove flag　
      logging.warning(f"remove_flag: {y}, {x}")
    else:
      place_flag(x, y)  # Place flag
# 旗周りの関数が多すぎる
# placeとremoveをtoggleから呼ぶ形にしてclickからはtoggleのみ呼ぶようにするとか？
def place_flag(x, y):
  global MAX_NUM_FLAG  # Use the global variable
  global flags

  if opened[y][x] or MAX_NUM_FLAG <= 0:
    return

  else:
    center_x = POSITION["x"] + BORDER_WIDTH * x + \
      BORDER_WIDTH / 2 + SQUARE_LENGTH * x + SQUARE_LENGTH / 2
    center_y = POSITION["y"] + BORDER_WIDTH * y + \
      BORDER_WIDTH / 2 + SQUARE_LENGTH * y + SQUARE_LENGTH / 2
    flags[y][x] = True
    MAX_NUM_FLAG -= 1

  flag_length = RADIUS
  flag_height = 8
  flagstick_x = center_x + RADIUS - flag_height
  flagstick_top = center_y + flag_length / 2
  polygon_top = center_y - flag_length / 2
  flagstick_bottom = center_y + flag_length / 2
  canvas.create_line(center_x, flagstick_top, flagstick_x,flagstick_top, fill="blue", width=15)  # Stick
  canvas.create_polygon(flagstick_x, flagstick_bottom, center_x + RADIUS, center_y, flagstick_x, polygon_top, fill="red")  # Flag

def toggle_flag(x, y):
  global MAX_NUM_FLAG  # Use the global variable

  if opened[y][x]:
    return

  if flags[y][x]:
    clear_flag(x, y)
    # Increase the remaining number of flags
  elif MAX_NUM_FLAG > 0:
    place_flag(x, y)
    # Decrease the remaining number of flags

def remove_flag(x, y):
  global MAX_NUM_FLAG
  global flags
  if opened[y][x] or not flags[y][x]:
    return

  global MAX_NUM_FLAG
  flags[y][x] = False
  MAX_NUM_FLAG += 1

  clear_flag_image(x, y)

def clear_flag_image(x, y):
  center_x = POSITION["x"] + BORDER_WIDTH * x + \
    BORDER_WIDTH / 2 + SQUARE_LENGTH * x + SQUARE_LENGTH / 2
  center_y = POSITION["y"] + BORDER_WIDTH * y + \
    BORDER_WIDTH / 2 + SQUARE_LENGTH * y + SQUARE_LENGTH / 2

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
  opened[y][x] = False
  remove_flag(x, y)  # Call remove_flag to update the flags and flag count

def play():
  global canvas
  global GAME_STATE
  GAME_STATE = "start"
  root, canvas = create_canvas()
  set_field()

  initialize_mines()

  canvas.bind("<Button-1>", lambda event: click(event))  # Left mouse button
  canvas.bind("<Button-2>", lambda event: click(event))  # Right mouse button
  root.mainloop()

play()
