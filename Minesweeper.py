import logging
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
MAX_NUM_FLAG = 50
BOMBS_COUNT = 10

field = [[0 for _ in range(NUMBER)] for _ in range(NUMBER)]
opened = [[False] * NUMBER for _ in range(NUMBER)]
flags = [[False] * NUMBER for _ in range(NUMBER)]

def initialize_mines(): # bomb = -1
  global field
  field = [[0] * NUMBER for _ in range(NUMBER)]

  for _ in range(BOMBS_COUNT): #爆弾設置
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

def get_eight_cells(): #クリックした周りのセル
    return [[0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1]]

def cell_counts(): #空きセルに表示する番号取得
  global field
  
  for y in range(NUMBER):
    for x in range(NUMBER):
      bombs_count = count_bombs(x, y)
      if field[y][x] != -1:
        field[y][x] = bombs_count

def count_bombs(x, y, first_click=False):
  bombs_count = 0
  cells_around = get_eight_cells()

  for offset in cells_around: #offset＝該当するものの周り、ズレた位置という意味
    dx, dy = offset
    nx, ny = x + dx, y + dy #dx,dy=隣り合うセルまでに距離、nx,ny=隣り合うセルの位置

    if 0 <= nx < NUMBER and 0 <= ny < NUMBER:
      if first_click and field[ny][nx] == -1: #最初のセルが爆弾だった場合は変更
        return 0
      if field[ny][nx] == -1:
        bombs_count += 1

  return bombs_count

def open_zero_around_cells(x, y):
  eight_cells = get_eight_cells()

  for dx, dy in eight_cells:
    nx, ny = x + dx, y + dy
    if 0 <= nx < NUMBER and 0 <= ny < NUMBER:
      if not field[ny][nx] == -1 and not opened[ny][nx]:
        if flags[ny][nx]:
          remove_flag(nx, ny) 
        opened[ny][nx] = True
        if field[ny][nx] == 0:
          set_item(None, nx, ny)
          open_zero_around_cells(nx, ny)
        else:
          set_item(str(field[ny][nx]), nx, ny)

def open_cell(x, y):
  global GAME_STATE
  global opened

  if opened[y][x] or flags[y][x] or GAME_STATE == "lost" or GAME_STATE == "won":
    return

  check_game_state(x, y)

def check_game_state(x, y):
  global GAME_STATE
  global opened
  if GAME_STATE == "start": #初手であるかをGAMESTATEで判断
    move_bombs(x, y)
    GAME_STATE = "progressing"

  opened[y][x] = True
  bombs_around_cell = count_bombs(x, y, first_click=(GAME_STATE == "start"))

  if bombs_around_cell == 0 and field[y][x] != -1:
    set_item(None, x, y)
    open_zero_around_cells(x, y)
  elif field[y][x] == -1:
    set_item("bomb", x, y)
    game_over()
  else:
    set_item(field[y][x], x, y)

  check_win()

def move_bombs(x, y):
  global field
  logging.warning(f"clicked positions: {x}, {y}")
  check_cells = get_eight_cells()  
  check_cells.append([0, 0]) #元の関数にクリックしてる中心のセルも確認するように追加
  adjacent_bombs = []  

  coordinates = [] #座標
  for dx, dy in check_cells:
    nx, ny = x + dx, y + dy
    coordinates.append([nx, ny])

    if 0 <= nx < NUMBER and 0 <= ny < NUMBER and field[ny][nx] == -1:
      adjacent_bombs.append((nx, ny))

  for bomb_x, bomb_y in adjacent_bombs: #ロジックで爆弾の消去
    field[bomb_y][bomb_x] = 0  
  logging.warning(f"bombs need to move positions: {adjacent_bombs}")
  new_bomb_positions = generate_new_bomb_positions(adjacent_bombs, x, y, coordinates) #爆弾の新しい場所

  for new_x, new_y in new_bomb_positions:
    field[new_y][new_x] = -1 
    logging.warning(f"new bomb positions: {new_y}, {new_x}")

  cell_counts()# 数を数え直す

def generate_new_bomb_positions(adjacent_bombs, x, y, coordinates): #xyは押したセルにまた爆弾が置かれないようにこの情報が必要、ここ消すとエラー
  new_bomb_positions = []
  valid_positions = [(x, y) for x in range(NUMBER) for y in range(NUMBER) if not [x, y] in coordinates and field[y][x] != -1]
  random.shuffle(valid_positions)
  print("regenerated")
  for i in range(len(adjacent_bombs)): #adjacent=隣り合う
    if i < len(valid_positions):
      new_bomb_positions.append(valid_positions[i])
      logging.warning(f"New bomb position: ({valid_positions[i][0]}, {valid_positions[i][1]})")

  return new_bomb_positions

def check_win():
  for y in range(NUMBER):
    for x in range(NUMBER):
      if field[y][x] != -1 and not opened[y][x]:
        return
  global GAME_STATE
  GAME_STATE = "won"
  print("Game Clear")

def game_over():
  global GAME_STATE
  global flags

  for y in range(NUMBER):
    for x in range(NUMBER):
      if flags[y][x]:
        flags[y][x] = False

  open_bomb_cells()
  GAME_STATE = "lost" 
  print("Game Over") 

def open_bomb_cells():
  for y in range(NUMBER):
    for x in range(NUMBER):
      if field[y][x] == -1:
        open_cell(x, y)

def click(event):
  x, y = point_to_numbers(event.x, event.y)

  if event.num == 1:  # 左クリック
    open_cell(x, y)
  elif event.num == 2:  # 右クリック
    toggle_flag(x, y)

def place_flag(x, y):
  global MAX_NUM_FLAG  
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
  global MAX_NUM_FLAG  
  global GAME_STATE

  if opened[y][x] or GAME_STATE == "lost" or GAME_STATE == "won":
    return

  if flags[y][x]:
    remove_flag(x, y)
  elif MAX_NUM_FLAG > 0:
    place_flag(x, y)

def remove_flag(x, y):
  global MAX_NUM_FLAG

  if opened[y][x] or not flags[y][x]:
    return

  flags[y][x] = False
  MAX_NUM_FLAG += 1
  opened[y][x] = False  
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
