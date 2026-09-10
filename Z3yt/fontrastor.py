from PIL import Image, ImageDraw, ImageFont

# SIZE = 24
# w,h = 16,28
# PADDINGS = (1,-2)

SIZE = 32
w,h = 21,38
PADDINGS = (1,-2)

# SET1 =   "qwertyuiopasdfghjkl.zxcvbnm,?!"
# SET2 =   "QWERTYUIOPASDFGHJKL.ZXCVBNM,?!"
# SET3 = """1234567890@#$_&-+()./*"':;=,!?"""
# SET4 = """1234567890~`|%<>[]{}\\^        """
# SETS = [SET1, SET2, SET3, SET4]
SETS = ["⇪≪◀▶≫␣←↞✓✗"]
SETS = [i for i in SETS[0]]
# SETS = list("".join([chr(i) for i in range(32,127)]))
print(SETS)
W, H = w*len(SETS[0]), h*len(SETS)
print(W,H)



img = Image.frombytes("RGBA", (W,H), b"\x00\x00\x00\xff"*W*H)
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("JetBrainsMono-Regular.ttf", SIZE)

for j in range(len(SETS)):
    for i in range(len(SETS[0])):
        draw.text((PADDINGS[0]+i*w, PADDINGS[1]+h*j), SETS[j][i],(255,255,255),font=font)

img.show()
with open("font4meow.bin", "wb") as f:
    f.write(img.tobytes())

# for j in range(len(SETS)):
#     for i in range(len(SETS[0])):
#         draw.rectangle(((i*w, j*h), ((i+1)*w, (j+1)*h)), outline = (255,0,0,50))
# img.show()
