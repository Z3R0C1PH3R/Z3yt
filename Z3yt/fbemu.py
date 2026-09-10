import PIL.Image as Image
from time import sleep

FB_DEVICE="fb"
RES = (640,480) #w,h

with open(FB_DEVICE, "rb") as fb:
    prev = data = 0
    while True:
        while data == prev:
            sleep(1)
            fb.seek(0)
            data = fb.read(4*RES[0]*RES[1])

        Image.frombytes("RGBA", RES, data).show()
        prev = data
