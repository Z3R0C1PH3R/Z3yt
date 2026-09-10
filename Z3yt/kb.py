import os
import display
import buttoninput
from time import sleep

KB_SIZE = (10,4)
KB_POS = (5,480-64*4-2)
KB_CELL_SIZE = display.RES[0]//KB_SIZE[0]-1
w,h = 21,38
FONT_PADDING = (((display.RES[0]//KB_SIZE[0]-1) - w)//2, ((display.RES[0]//KB_SIZE[0]-1) - h)//2)

br_fs = (210, 38)
GLYPH = w*h*4
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "font4.bin"), "rb") as f:
    _font4 = f.read()

# Same layout as font32.bin: fixed size glyphs one after another, so slicing
# out glyph i gives exactly what draw_part wants.
bottom_row = [_font4[i*GLYPH:(i+1)*GLYPH] for i in range(len(_font4)//GLYPH)]

SET1 =   "qwertyuiopasdfghjkl.zxcvbnm,?!"
SET2 =   "QWERTYUIOPASDFGHJKL.ZXCVBNM,?!"
SET3 = """1234567890@#$_&-+()./*"':;=,!?"""
SET4 = """1234567890~`|%<>[]{}\\^        """
SETS = [SET1, SET2, SET3, SET4]


cur_set = 0
cursor = 0
buffer = ""
max_buffer = 29
selected = [0,0]


def draw_kb_frame():
    display.draw_screen(display.BLACK*display.FULL)
    for j in range(KB_SIZE[1]):
        for i in range(KB_SIZE[0]):
            display.draw_rect(display.WHITE, (KB_CELL_SIZE, KB_CELL_SIZE), (KB_POS[0] + i*KB_CELL_SIZE, KB_POS[1] + j*KB_CELL_SIZE))



def select_cell(selected=(0,0)):
    display.inv_part((KB_CELL_SIZE, KB_CELL_SIZE), (KB_POS[0] + selected[0]*KB_CELL_SIZE, KB_POS[1] + selected[1]*KB_CELL_SIZE))


def draw_keys(S=0):
    for j in range(KB_SIZE[1]-1):
        for i in range(KB_SIZE[0]):
            display.draw_text(SETS[S][j*KB_SIZE[0]+i], (FONT_PADDING[0] + KB_POS[0] + i*KB_CELL_SIZE, FONT_PADDING[1] + KB_POS[1] + j*KB_CELL_SIZE))
    j = 3
    for i in range(len(bottom_row)):
        display.draw_part(bottom_row[i], (w,h), (FONT_PADDING[0] + KB_POS[0] + i*KB_CELL_SIZE, FONT_PADDING[1] + KB_POS[1] + j*KB_CELL_SIZE))


def draw_buffer(redraw=True):
    if not redraw:
        i = cursor-1
        display.draw_text(buffer[-1], (FONT_PADDING[0] + (i%max_buffer)*w, FONT_PADDING[1] + (i//max_buffer)*h))
        display.inv_part((w,h), (FONT_PADDING[0] + (cursor%max_buffer)*w, FONT_PADDING[1] + (cursor//max_buffer)*h))    
        return
    display.draw_screen(display.BLACK*(display.RES[0]*KB_POS[1]))
    display.draw_text(buffer, FONT_PADDING)
    display.inv_part((w,h), (FONT_PADDING[0] + (cursor%max_buffer)*w, FONT_PADDING[1] + (cursor//max_buffer)*h))

def handle_press(selected):
    global buffer, cur_set, cursor
    if selected[1]<3: #LETTERS
        buffer = buffer[:cursor]+SETS[cur_set][selected[1]*KB_SIZE[0]+selected[0]]+buffer[cursor:]
        cursor += 1
        draw_buffer(False if cursor == len(buffer) and cursor else True)

    elif selected == [5,3]:  #SPACE
        buffer = buffer[:cursor]+" "+buffer[cursor:]
        cursor += 1
        draw_buffer()


    elif selected == [6,3] and cursor: #BACKSPACE
        buffer = buffer[:cursor-1]+buffer[cursor:]
        cursor -= 1
        draw_buffer()

    elif selected == [7,3] and len(buffer) > 0: #CLEAR
        buffer = ""
        cursor = 0
        draw_buffer()
    
    elif selected == [0,3]: #SHIFT SET
        cur_set = (cur_set+1) % len(SETS)
        draw_keys(cur_set)

    elif selected == [3,3] and cursor < len(buffer): #CURSOR RIGHT
        display.inv_part((w,h), (FONT_PADDING[0] + (cursor%max_buffer)*w, FONT_PADDING[1] + (cursor//max_buffer)*h))
        cursor = cursor+1
        display.inv_part((w,h), (FONT_PADDING[0] + (cursor%max_buffer)*w, FONT_PADDING[1] + (cursor//max_buffer)*h))

    elif selected == [2,3] and cursor: #CURSOR LEFT
        display.inv_part((w,h), (FONT_PADDING[0] + (cursor%max_buffer)*w, FONT_PADDING[1] + (cursor//max_buffer)*h))
        cursor = cursor-1
        display.inv_part((w,h), (FONT_PADDING[0] + (cursor%max_buffer)*w, FONT_PADDING[1] + (cursor//max_buffer)*h))

    elif selected == [4,3] and cursor < len(buffer): #CURSOR RIGHTMOST
        display.inv_part((w,h), (FONT_PADDING[0] + (cursor%max_buffer)*w, FONT_PADDING[1] + (cursor//max_buffer)*h))
        cursor = len(buffer)
        display.inv_part((w,h), (FONT_PADDING[0] + (cursor%max_buffer)*w, FONT_PADDING[1] + (cursor//max_buffer)*h))

    elif selected == [1,3] and cursor: #CURSOR LEFTMOST
        display.inv_part((w,h), (FONT_PADDING[0] + (cursor%max_buffer)*w, FONT_PADDING[1] + (cursor//max_buffer)*h))
        cursor = 0
        display.inv_part((w,h), (FONT_PADDING[0] + (cursor%max_buffer)*w, FONT_PADDING[1] + (cursor//max_buffer)*h))
    
    elif selected == [8,3]: #OK
        return 1
    
    elif selected == [9,3]: #CANCEL
        return 2
    

def text_input(placeholder=""):
    global buffer, cursor
    if placeholder:
        buffer=placeholder
        cursor = len(buffer)
    draw_kb_frame()
    draw_keys(0)
    select_cell()
    draw_buffer()

    while True:
        button, state = buttoninput.take_input().split()
        state = int(state)
        if button == "DX" and state:
            select_cell(selected)
            selected[0] = (selected[0] + state) % KB_SIZE[0]
            select_cell(selected)

        elif button == "DY" and state:
            select_cell(selected)
            selected[1] = (selected[1] - state) % KB_SIZE[1]
            select_cell(selected)
            sleep(0.1)

        elif button == "A" and state:
            select_cell(selected)
            ret = handle_press(selected)
            if ret:
                display.draw_screen(display.BLACK*display.FULL)
                if ret == 1:
                    return buffer
                elif ret == 2:
                    return False
            select_cell(selected)



def reset_buffer():
    global cur_set, cursor, buffer, max_buffer, selected
    cur_set = 0
    cursor = 0
    buffer = ""
    max_buffer = 29
    selected = [0,0]


if __name__ == "__main__":
    print(text_input())