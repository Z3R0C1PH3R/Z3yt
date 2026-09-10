import display
import buttoninput

def text_area(text, dim=display.RES2, pos=(0,0), padding=(1,1)):
    max_chars = (dim[0]-2*padding[0])//display.w
    text = [i[j:j+max_chars] for i in text.split("\n") for j in range(0, len(i), max_chars)]
    max_lines = (dim[1]-2*padding[1])//display.h
    pages = [text[i:i+max_lines] for i in range(0,len(text), max_lines)]
    num_pages = len(pages)
    cur_page = 0

    display.draw_screen(display.BLACK*display.FULL)
    display.draw_rect(display.WHITE, dim, pos)
    if cur_page < num_pages-1:
        display.draw_screen((display.WHITE*8 + display.BLACK*10)*(dim[0]//18), (pos[0], pos[1]+dim[1]))
    display.draw_text("\n".join(pages[cur_page]), (pos[0]+padding[0], pos[1]+padding[1]))

    while True:
        button, state = buttoninput.take_input().split()
        state = int(state)
        if button == "DY" and state:
            cur_page = (cur_page - state) % num_pages
            display.draw_screen(display.BLACK*display.FULL)
            display.draw_rect(display.WHITE, dim, pos)
            if cur_page > 0:
                display.draw_screen((display.WHITE*8 + display.BLACK*10)*(dim[0]//18), pos)
            if cur_page < num_pages-1:
                display.draw_screen((display.WHITE*8 + display.BLACK*10)*(dim[0]//18), (pos[0], pos[1]+dim[1]))
            display.draw_text("\n".join(pages[cur_page]), (pos[0]+padding[0], pos[1]+padding[1]))

        if (button == "B" or button == "MENU") and state:
            break

    display.draw_screen(display.BLACK*display.FULL)
    return cur_page

def menu(options, title="Select", cur_option=0, dim=display.RES2, pos=(0,0), padding=(1,1), images=[]): # images = [link, dim, pos]
    selecting = True
    while selecting:
        text = f"< {title}: {cur_option+1} >\n" + options[cur_option]
        max_chars = (dim[0]-2*padding[0])//display.w
        text = [i[j:j+max_chars] for i in text.split("\n") for j in range(0, len(i), max_chars)]
        max_lines = (dim[1]-2*padding[1])//display.h
        pages = [text[i:i+max_lines] for i in range(0,len(text), max_lines)]
        num_pages = len(pages)
        cur_page = 0

        display.draw_screen(display.BLACK*display.FULL)
        display.draw_rect(display.WHITE, dim, pos)
        if cur_page < num_pages-1:
            display.draw_screen((display.WHITE*8 + display.BLACK*10)*(dim[0]//18), (pos[0], pos[1]+dim[1]))
        display.draw_text("\n".join(pages[cur_page]), (pos[0]+padding[0], pos[1]+padding[1]))

        if images:
            display.draw_part(*images[cur_option])

        while True:
            button, state = buttoninput.take_input().split()
            state = int(state)
            if button == "DY" and state:
                cur_page = (cur_page - state) % num_pages
                display.draw_screen(display.BLACK*display.FULL)
                display.draw_rect(display.WHITE, dim, pos)
                if cur_page > 0:
                    display.draw_screen((display.WHITE*8 + display.BLACK*10)*(dim[0]//18), pos)
                if cur_page < num_pages-1:
                    display.draw_screen((display.WHITE*8 + display.BLACK*10)*(dim[0]//18), (pos[0], pos[1]+dim[1]))
                if cur_page == 0 and images:
                    display.draw_part(*images[cur_option])
                display.draw_text("\n".join(pages[cur_page]), (pos[0]+padding[0], pos[1]+padding[1]))

            if button == "DX" and state and 0 <= state + cur_option < len(options):
                cur_option += state 
                break

            if button == "A" and state:
                selecting = False
                break

            if button=="B" and state:
                display.draw_screen(display.BLACK*display.FULL)
                return -2

            if button=="MENU" and state:
                display.draw_screen(display.BLACK*display.FULL)
                return -1

    display.draw_screen(display.BLACK*display.FULL)
    return cur_option