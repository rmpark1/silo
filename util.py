from reportlab.lib.colors import rgb2cmyk

def hex2cmyk(hex_code):
    hex_code = hex_code.lstrip('#')
    r, g, b = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
    return rgb2cmyk(r/255., g/255., b/255.)
