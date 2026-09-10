"""Framebuffer drawing, standard library only.

/dev/fb0 is just 640x480 pixels of 4 bytes each, so an mmap plus byte slicing
does everything numpy used to do here, without the 34 MB dependency. Colours are
4-byte little-endian ARGB, and a run of pixels is simply that repeated, so
BLACK * FULL is a black screen and WHITE * 8 is an eight pixel white dash.
"""

from fcntl import ioctl
from mmap import mmap
import os
import stat

# Overridable so the drawing can be exercised against a plain file off-device,
# the way fbemu.py expects.
FB_DEVICE = os.environ.get("Z3_FB", "/dev/fb0")
RES = (640,480) #w,h
RES2 = (RES[0]-1, RES[1]-1)
FULL = RES[0]*RES[1]
BPP = 4

WHITE = b"\xff\xff\xff\xff"
BLACK = b"\x00\x00\x00\xff"

fb = open(FB_DEVICE, "r+b")
mm = mmap(fb.fileno(), BPP*FULL)

fs = (21, 3610)
w,h = 21,38
FIRST, GLYPHS = 32, 95
_GLYPH_BYTES = w*h*BPP
_ROW_BYTES = w*BPP

# Look next to this file first so the font is found regardless of the cwd.
for _dir in (os.path.dirname(os.path.abspath(__file__)), os.getcwd()):
    try:
        with open(os.path.join(_dir, "font32.bin"), "rb") as f:
            _font = f.read()
        break
    except OSError:
        continue
else:
    raise OSError("font32.bin not found")

_MISSING_ROW = WHITE * w
_INVERT = bytes(255-i for i in range(256))
_BLANK_SCREEN = None


def reset_screen():
    if not stat.S_ISCHR(os.fstat(fb.fileno()).st_mode):
        return  # a plain file has no ioctls to speak of
    # NEXT LINE IS RESOLUTION SPECIFIC
    ioctl(fb, 0x4601, b'\x80\x02\x00\x00\xe0\x01\x00\x00\x80\x02\x00\x00\xc0\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00^\x00\x00\x00\x96\x00\x00\x00\x00\x00\x00\x00\xc2\xa2\x00\x00\x1a\x00\x00\x00T\x00\x00\x00\x0c\x00\x00\x00\x1e\x00\x00\x00\x14\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    ioctl(fb, 0x4611, 0)


def _blit(x, y, data):
    """Write a run of pixels at (x,y), clipped to the end of the screen."""
    start = (y*RES[0] + x)*BPP
    if start < 0 or start >= BPP*FULL:
        return
    mm.seek(start)
    mm.write(data[:BPP*FULL - start])


def clear(colour=BLACK):
    global _BLANK_SCREEN
    if colour == BLACK:
        if _BLANK_SCREEN is None:
            _BLANK_SCREEN = BLACK*FULL
        fill = _BLANK_SCREEN
    else:
        fill = colour*FULL
    mm.seek(0)
    mm.write(fill)


def draw_screen(b, pos=(0,0)):
    """Write a flat run of pixels starting at pos, wrapping onto the next row."""
    _blit(pos[0], pos[1], b)


def draw_part(b, dim=RES2, pos=(0,0)):
    """pos: (x,y) top left of part, dim: (w,h) width and height of part"""
    row = dim[0]*BPP
    for y in range(dim[1]):
        _blit(pos[0], pos[1]+y, b[y*row:(y+1)*row])


def inv_part(dim=RES2, pos=(0,0)):
    """pos: (x,y) top left of part, dim: (w,h) width and height of part"""
    row = dim[0]*BPP
    for y in range(pos[1], pos[1]+dim[1]):
        start = (y*RES[0] + pos[0])*BPP
        mm.seek(start)
        # Invert the colour but put the alpha byte back, matching ~px | BLACK.
        px = bytearray(mm.read(row).translate(_INVERT))
        px[BPP-1::BPP] = b"\xff"*(len(px)//BPP)
        mm.seek(start)
        mm.write(px)


def draw_line(p1, p2, c):
    """Draws a line from p1(x,y) to p2(x,y) of color c(4)"""
    x0, y0 = p1
    x1, y1 = p2
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    error = dx + dy
    if dy == 0:
        draw_screen(c*dx, (min(p1[0],p2[0]) ,p1[1]))
    if dx == 0:
        draw_part(c*-dy, (1,-dy), (p1[0] ,min(p1[1],p2[1])))
    while True:
        _blit(x0, y0, c)
        if x0 == x1 and y0 == y1: break
        e2 = 2 * error
        if e2 >= dy:
            if x0 == x1: break
            error = error + dy
            x0 = x0 + sx
        if e2 <= dx:
            if y0 == y1: break
            error = error + dx
            y0 = y0 + sy


def draw_rect(c=WHITE, dim=RES2, pos=(0,0)):
    """Draws a rect, pos:(x,y) top left, dim:(w,h) of color c(4)"""
    x, y = pos
    span = c*(dim[0]+1)
    _blit(x, y, span)
    _blit(x, y+dim[1], span)
    for yy in range(y, y+dim[1]+1):
        _blit(x, yy, c)
        _blit(x+dim[0], yy, c)


def _glyph_row(char, row):
    index = ord(char) - FIRST
    if 0 <= index < GLYPHS:
        start = index*_GLYPH_BYTES + row*_ROW_BYTES
        return _font[start:start+_ROW_BYTES]
    return _MISSING_ROW


def draw_text(text, pos=(0,0)):
    """Draw text at pos (x,y), hard-wrapping at the screen edge."""
    x, y = pos
    max_chars = max((RES[0]-x)//w, 1)
    lines = []
    for line in text.split("\n"):
        lines.extend([line[i:i+max_chars] for i in range(0, len(line), max_chars)] or [""])

    for index, line in enumerate(lines):
        top = y + index*h
        if top >= RES[1]:
            break
        for row in range(min(h, RES[1]-top)):
            data = b"".join(_glyph_row(char, row) for char in line)
            if data:
                _blit(x, top+row, data[:(RES[0]-x)*BPP])


reset_screen()
