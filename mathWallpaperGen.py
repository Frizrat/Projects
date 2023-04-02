"""
Use python mathWaalpaperGen.py 'img_path', 'deciamls_path', 'save_path'
"""


import itertools, sys
from PIL import Image, ImageDraw, ImageFont

COLORS = (200, 255)
FONTS = [ImageFont.truetype(font, 20) for font in ('cour.ttf', 'courbd.ttf')]

def _get_mean_pixel_area(img:Image.Image, top_left:tuple[int], bbox:tuple[int]):
    mean_pix = 0
    for x, y in itertools.product(range(top_left[0], top_left[0] + bbox[2]), range(top_left[1], top_left[1] + bbox[3])):
        try: mean_pix += img.getpixel((x, y))
        except: break

    return mean_pix / (bbox[2] * bbox[3])

def number_to_img(img_path, decimals_path, save_path):
    num = Image.open(img_path).convert('L')
    decimals = open(decimals_path, 'r', encoding='utf-8').read()

    img = Image.new('L', num.size, 0)
    txt = ''; i = 0; j = 0

    while i < len(decimals) and FONTS[0].getbbox(txt)[3]*j < num.size[1]:
        if FONTS[0].getlength(txt) >= num.size[0]-220: j += 1; txt = ''
            
        pos = (100 + int(FONTS[0].getlength(txt)), 20*j)
        cond = _get_mean_pixel_area(num, pos, FONTS[0].getbbox(decimals[i])) > 155

        ImageDraw.Draw(img).text(pos, decimals[i], COLORS[cond], font=FONTS[cond])

        txt += decimals[i]
        i += 1

    img.save(save_path)

if __name__ == '__main__':
    number_to_img(sys.argv[1], sys.argv[2], sys.argv[3])