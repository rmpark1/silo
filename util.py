from reportlab.lib.colors import rgb2cmyk as rl_rgb2cmyk

def hex2cmyk(hex_code):
    hex_code = hex_code.lstrip('#')
    r, g, b = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
    return rl_rgb2cmyk(r/255., g/255., b/255.)

def rgb2cmyk(r, g, b): return rl_rgb2cmyk(r/255., g/255., b/255.)
