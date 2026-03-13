from tkinter import *
from random import randint
import logging

logging.basicConfig(level='DEBUG', format='%(levelname)s - %(message)s')

HIGH_SPEED = 100
NORMAL_SPEED = 400
SPEED = NORMAL_SPEED
SPACE_SIZE = 30
WIDTH = 10
HEIGHT = 20
GAME_WIDTH  = SPACE_SIZE*WIDTH
GAME_HEIGHT = SPACE_SIZE*HEIGHT

BG_COLOR    = "#000000"

emptyForm = []

I_form = [[False,False,False,False],
         [True, True, True, True],
         [False,False,False,False],
         [False,False,False,False]]

Z_form = [[True, False,False],
          [True, True, False],
          [False,True, False]]

rect_form = [[True,True],
             [True,True]]

L_form = [[False,False,True],
          [True, True, True],
          [False,False,False]]

T_form = [[False,True, False],
          [True, True, True],
          [False,False,False]]

Z_form_mirror = [[False,True, False],
                 [True, True, False],
                 [True, False,False]]

L_form_mirror = [[False,False, False],
                 [True, True, True],
                 [False,False,True]]

all_forms = [I_form,Z_form,rect_form,L_form,T_form,Z_form_mirror,L_form_mirror]
all_colors = [
    "#FF5555",  # Rot
    "#FFAA00",  # Orange
    "#FFFF55",  # Gelb
    "#55FF55",  # Grün
    "#00FFFF",  # Cyan
    "#5599FF",  # Blau
    "#FF55FF"   # Magenta
]

def new_game():

    global end_screen
    global points

    if end_screen:
        logging.info("Neues Spiel gestartet!")

        end_screen = False

        points = 0
        stack.clear()
        canvas.delete(ALL)
        label.config(text="Score:{}".format(0), font=('consolas', 20))

        window.bind('<w>', lambda event: turn())
        window.bind('<a>', lambda event: move_left())
        window.bind('<KeyPress-s>', lambda event: setHighSpeed())
        window.bind('<KeyRelease-s>', lambda event: setNormalSpeed())
        window.bind('<d>', lambda event: move_right())

        next_move()

class Rectangle:
    def __init__(self,x_pos,y_pos,color):
        self.ref = canvas.create_rectangle(x_pos*SPACE_SIZE, y_pos*SPACE_SIZE, (x_pos+1)*SPACE_SIZE, (y_pos+1)*SPACE_SIZE, fill=color)
    def __del__(self):
        canvas.delete(self.ref)

class Stack:
    def __init__(self):
        self.state = []
        self.rectangles = []
        for y in range(HEIGHT):
            self.state.append([0]*WIDTH)

    def clear(self):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                self.state[y][x] = 0

    def draw(self):
        self.rectangles.clear()
        for y in range(HEIGHT):
            for x in range(WIDTH):
                color = self.state[y][x]
                if color != 0:
                    self.rectangles.append(Rectangle(x,y,color))

    def add_stone(self,stone):
        start_x = stone.start_x
        start_y = stone.start_y
        for x in range(stone.len):
            for y in range(stone.len):
                if stone.form[y][x]:
                    self.state[start_y + y][start_x + x] = stone.color

    def check_collision(self,stone):
        for x in range(stone.len):
            for y in range(stone.len):
                x_stack = stone.start_x + x
                y_stack = stone.start_y + y + 1

                #Ignore x values outside stack
                if x_stack >= WIDTH or x_stack < 0:
                    continue

                if y_stack >= HEIGHT:
                    # Reached bottom of stack, return True
                    if stone.form[y][x]:
                        return True
                    #Ignore
                    else:
                        continue

                if stone.form[y][x] and self.state[y_stack][x_stack] != 0:
                    return True
        return False

    def check_full_line(self):
        for y in range(HEIGHT):
            full_line = True
            for x in range(WIDTH):
                if self.state[y][x] == 0:
                    full_line = False
            if full_line:
                return True,y
        return False,0

    def remove_line(self,line):
        self.state.pop(line)
        self.state.insert(0,[0]*WIDTH)

    def check_game_over(self):
        for x in range(WIDTH):
            if self.state[0][x] != 0:
                return True
        return False

class Stone:
    def __init__(self,form,color):
        self.color = color
        self.start_form = form
        self.form = form
        self.len = len(form)
        self.rectangles = []
        self.start_x = 5 - int(self.len / 2)
        self.start_y = 0
        self.x_min = 0
        self.x_max = WIDTH - self.len
        self.calc_boundarys()
        self.create_rectangles(self.start_x,self.start_y)

    def calc_boundarys(self):
        x_min = 0
        x_max = WIDTH - self.len
        y_end = self.start_y + self.len
        x=0
        while x < self.len:
            emptyCol = True
            for y in range(self.len):
                if self.form[y][x]:
                    emptyCol = False
            if emptyCol:
                x_min -= 1
            else:
                break
            x += 1
        self.x_min = x_min

        x = self.len - 1
        while x >= 0:
            emptyCol = True
            for y in range(self.len):
                if self.form[y][x]:
                    emptyCol = False
            if emptyCol:
                x_max += 1
            else:
                break
            x -= 1
        self.x_max = x_max

        if self.start_x < self.x_min:
            self.start_x = self.x_min
        if self.start_x > self.x_max:
            self.start_x = self.x_max

    def create_rectangles(self,start_x,start_y):
        self.rectangles.clear()
        for x in range(self.len):
            for y in range(self.len):
                if self.form[y][x]:
                    self.rectangles.append(Rectangle(start_x+x,start_y+y,self.color))

    def turn(self):
        tmp=[]
        for i in range(self.len):
            tmp.append([False]*self.len)

        for x in range(self.len):
            for y in range(self.len):
                tmp[x][y] = self.form[self.len-1-y][x]

        self.form = tmp
        self.calc_boundarys()
        self.create_rectangles(self.start_x, self.start_y)

    def move_left(self):
        if self.start_x > self.x_min:
            self.start_x -= 1
            self.create_rectangles(self.start_x, self.start_y)


    def move_right(self):
        if self.start_x < self.x_max:
            self.start_x += 1
            self.create_rectangles(self.start_x, self.start_y)

    def move_down(self):
        self.start_y += 1
        self.create_rectangles(self.start_x, self.start_y)

activeStone = Stone(emptyForm,BG_COLOR)
stack = Stack()
createStone = True
points = 0
fullLineCnt = 0

def next_move():
    global activeStone
    global createStone
    global points
    global fullLineCnt

    if createStone:
        createStone = False
        rand = randint(0,len(all_forms)-1)
        form = all_forms[rand]
        color = all_colors[rand]
        activeStone = Stone(form, color)
    else:
        activeStone.move_down()

    if stack.check_collision(activeStone):
        stack.add_stone(activeStone)
        createStone = True
        stack.draw()

    ret,line = stack.check_full_line()
    if ret:
        fullLineCnt += 1

    if fullLineCnt >= 2:
        fullLineCnt = 0
        stack.remove_line(line)
        points += 1
        label.config(text="Score:{}".format(points), font=('consolas', 20))
        stack.draw()

    if stack.check_game_over():
        game_over()
    else:
        window.after(SPEED, next_move)

def game_over():
    global end_screen
    end_screen = True
    canvas.delete(ALL)

    canvas.create_text(canvas.winfo_width() / 2, canvas.winfo_height() / 2, text = "GAME OVER!", fill = "red", font = ("consolas",40), tag = "gameover")
    canvas.create_text(canvas.winfo_width() / 2, canvas.winfo_height() / 2 + 100, text="Leertaste drücken für neues Spiel!", fill="red",
                       font=("consolas", 10), tag="newGame")

def move_left():
    activeStone.move_left()

def move_right():
    activeStone.move_right()

def turn():
    activeStone.turn()

def setNormalSpeed():
    global SPEED
    SPEED = NORMAL_SPEED

def setHighSpeed():
    global SPEED
    SPEED = HIGH_SPEED


window = Tk()
window.title("Tetris Game")
window.resizable(False, False)

end_screen = True

label = Label(window, text="Score:{}".format(0), font=('consolas', 20))
label.pack()

canvas = Canvas(window, bg=BG_COLOR, height=GAME_HEIGHT, width=GAME_WIDTH)
canvas.pack()

window.update()

window_width = window.winfo_width()
window_height = window.winfo_height()

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

x = int((screen_width/2) - (window_width/2))
y = int((screen_height/2) - (window_height/2))

window.geometry(f"{window_width}x{window_height}+{x}+{y}")

window.bind('<space>', lambda event: new_game())    

window.mainloop()