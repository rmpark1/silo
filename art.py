import copy
import os

import random
import numpy as np
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from reportlab.graphics import shapes
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Group as G
from reportlab.lib import colors
from scipy.spatial import ConvexHull

from util import hex2cmyk
from util import rgb2cmyk


INCH_TO_FONTSIZE = 295/3.5
cmap = lambda hex: colors.CMYKColor(*hex2cmyk(hex))
rmap = lambda r, g, b: colors.CMYKColor(*rgb2cmyk(r, g, b))
TAN = cmap("#FBFBEF")
WHITE = cmap("#FFFFFF")
PPTX = rmap(235, 237, 235)
RED=cmap("#CA1551") # Rosewood
MUTED=cmap("#25283D") # Space Indigo

# FONTS
pdfmetrics.registerFont(TTFont("cards", "fonts/cardcharacters.ttf"))
pdfmetrics.registerFont(TTFont("cardsnarrow", "fonts/cardcharactersnarrow.ttf"))

NSYMBOLS = "A23456789TJQK"

SPOTS = [
"12",
"10 -14",
"10 -14 12",
"00 20 -04 -24",
"00 20 -04 -24 12",
"00 20 -04 -24 02 22",
"00 20 -04 -24 02 22 11",
"00 20 -04 -24 02 22 11 -13",
"00 01 -02 -03 20 21 -22 -23 13",
"00 01 -02 -03 20 21 -22 -23 11 -15",
]


# Canvas settings
settings = {
    "lw": 1,
}

class Deck(object):

    def __init__(self,
            development=True,
            bleed=0.125,
            safety=0.125,
            inset=0.3,
            x=2.5, y=3.5,
            path="figures/deck.pdf",
            base_color=TAN,
        ):

        np.random.seed(0)

        self.size=(inch*(x + 2*bleed), inch*(y + 2*bleed))
        print("Making Deck")
        if development: print("**DEVELOPMENT**")
        print(f"Card Size:     {self.size[0]/inch}\" x {self.size[1]/inch}\"")
        print(f"Bleed:         {bleed}\"")
        print(f"Safety Margin: {safety}\"")

        self.x = inch*x
        self.y = inch*y
        self.sx = inch*x-2*inch*safety
        self.sy = inch*y-2*inch*safety
        self.base_color = base_color
        self.development = development

        self.path = path
        self.bleed = inch*bleed
        self.inset = inch*inset
        self.safety = inch*safety

        self.canvas = canvas.Canvas("figures/deck.pdf",
            pagesize=self.size, enforceColorSpace="CMYK")
        self.set()

        self.front_pattern = self.make_front_pattern()
        self.rule_table_pattern = self.make_rule_table_pattern()

    def make_print_layout(self, page_size=(8.5,11), margin=0.25, gap=0.125,
                          path="figures/print_out.pdf"):
        """Lay decks out onto pages. Save pages pdf.
        
        Args:
            page_size (tuple[float, float]): The (width, height) of the page
            in inches.
            margin (float): The width of the margin for each side in inches.
            gap (float): The gap between each card (including bleed) in inches.
        """
        # Find the maximum number of cards that will fit in each direction
        px, py = page_size[0]*inch, page_size[1]*inch
        m = margin*inch
        g = gap*inch

        # Build canvas
        self.canvas = canvas.Canvas(path, pagesize=(3*px, 3*py),
            enforceColorSpace="CMYK")
        # self.canvas.translate(px/2, py/2)
        # self.draw(G(shapes.Rect(-1, -1000, 2, 2000)))
        self.canvas.translate(px, py)
        self.draw(G(shapes.Rect(0, 0, px, py, fillColor=RED)))
        # self.draw(G(shapes.Rect(-1000, -1, 2000, 2)))

        # Determine best direction of layout (aligned or not)
        # px = 2*m - g + nx*(g + x)
        nxa = int(np.floor((px - 2*m + g)/(g+self.x)))
        nya = int(np.floor((py - 2*m + g)/(g+self.y)))
        nxu = int(np.floor((px - 2*m + g)/(g+self.y)))
        nyu = int(np.floor((py - 2*m + g)/(g+self.x)))
        _, nx, ny, aligned = max((nxa*nya, nxa, nya, True),
                                 (nxu*nyu, nxu, nyu, False))

        print(nx, ny)
        # Now compute individual gaps from margin
        # p - 2m - n*x = (n-1)g
        tw, th = {True: (self.x, self.y), False: (self.y, self.x)}[aligned]
        gx = (px - 2*m - nx*tw)/(nx-1)
        gy = (py - 2*m - ny*th)/(ny-1)

        # Determine position of each card
        # xi = -px/2 + m (i+0.5)*(x+g)
        # yj = py/2 - m - (j+0.5)*(y+g)
        card_faces = [self.make_face(rank, suit)
            for suit in ["C", "D", "H", "S"]
            for rank in np.roll(np.array(list(NSYMBOLS)),-1)]
        page = 0
        for isuit, suit in enumerate(["C", "D", "H", "S"]):
            for jrank, rank in enumerate(np.roll(np.array(list(NSYMBOLS)),-1)):
                # if isuit > 0 or jrank > 0: continue
                id = isuit*len(NSYMBOLS) + jrank
                rem = id % (nx*ny)
                i = rem // ny
                j = rem % ny
                print(i, j, rem)

                # Place on the page
                x = m + i*(tw+gx) + tw/2
                y = m + j*(th+gy) + th/2
                # x, y = m + tw/2, m + th/2
                # print(gx/self.x, m/self.x)
                card_face = self.make_face(rank, suit)
                card_face.translate(x,y)
                # card_face.translate(self.size[0]/2, self.size[1]/2)
                if not aligned: card_face.rotate(90)
                self.draw(card_face)

                if rem == nx*ny - 1:
                    self.canvas.showPage()
                    self.canvas.translate(px, py)
                    self.draw(G(shapes.Rect(0, 0, px, py, fillColor=RED)))

    def make_full_deck_pdf(self, collated=False):

        ctag = "_collated" if collated else ""
        name = f"figures/deck{ctag}.pdf"
        self.canvas = canvas.Canvas(name, pagesize=self.size,
            enforceColorSpace="CMYK")

        # Fix origin to the center of the card
        self.canvas.translate(self.size[0]/2, self.size[1]/2)

        front = self.make_front()
        self.draw(front)
        for suit in ["C", "D", "H", "S"]:
            for rank in np.roll(np.array(list(NSYMBOLS)),-1):
                if collated and f"{suit}{rank}" != "C2": self.make_front()
                face = self.make_face(rank, suit)
                self.canvas.showPage()
                self.canvas.translate(self.size[0]/2, self.size[1]/2)
                self.draw(face)

    def make_front_pdf(self, path="figures/front.pdf"):

        self.canvas = canvas.Canvas(path,
            pagesize=self.size, enforceColorSpace="CMYK") 
        self.front_pattern = self.make_front_pattern()
        front = self.make_front()
        self.draw(front)
        self.canvas.showPage()

    def make_background(self):
        # b = self.bleed
        # return shapes.Rect(
        #     -self.x/2 - b, -self.y/2 - b,
        #     self.x + 2*b, self.y + 2*b,
        #     fillColor=self.base_color, strokeWidth=.1)
        b = 0
        return shapes.Rect(
            -self.x/2 - b, -self.y/2 - b,
            self.x + 2*b, self.y + 2*b,
            fillColor=self.base_color, strokeWidth=.1)

    def make_front(self):
        return G(self.make_background(), self.front_pattern)

    def make_rule_table_pattern(self):
        # TODO: implement rule table
        return self.front_pattern

    def make_front_pattern(self):

        s = self.safety

        x, y = self.x, self.y
        nx, ny = 7, 8
        gw = (x-2*s)/nx
        gh = (y-2*s)/ny
        suits = "SHCD"
        front_pattern = []
        for xi in range(nx):
            for yi in range(ny):
                id = xi*nx + yi
                xp = -x/2 + s + gw/2 + xi*gw
                yp = y/2 - s - gh/2 - yi*gh
                suit_text = suits[id%4] 

                rolled = list(np.roll(list(NSYMBOLS), -1))
                rank = np.random.choice(rolled)
                number = rolled.index(rank)

                if suit_text == "S": group = self.make_spade(t=number/12)
                if suit_text == "H": group = self.make_heart(t=number/12)
                if suit_text == "C":
                    group = self.make_club()
                    # Constant random turning
                    for man in group.contents:
                            if np.random.random() < 0.3:
                                t = np.random.choice([-45, 45])
                                man.rotate(t)
                if suit_text == "D": group = self.make_diamond(random=True)

                g = G(group)
                sc = 0.3
                g.scale(sc, sc)
                g.translate(xp/sc, yp/sc)
                front_pattern.append(g)

        return G(*front_pattern)
        
    def make_face(self, rank, suit):

        # Draw background
        background = self.make_background()

        corners = G()

        if suit == "C":
            club_draw = self.make_club()
            corners = self.make_corners(rank, club_draw, suit)
            center, rings = self.arrange_center(rank, club_draw, suit)
            # Random turning
            n = NSYMBOLS.index(rank)
            if (n > 1) and (n < 10):
                for shape in center.contents:
                    for man in shape.contents[0].contents:
                            if np.random.random() < 0.1*n/2:
                                t = np.random.choice([-45, 45])
                                man.rotate(t)

        elif suit == "D":
            diamond = self.make_diamond()
            corners = self.make_corners(rank, diamond, suit)
            n = NSYMBOLS.index(rank)
            random = (n > 1) and (n < 10)
            diamond = self.make_diamond(random=random)
            center, rings = self.arrange_center(rank, diamond, suit,
                flip_allowed=False)

        elif suit == "H":
            rolled = list(np.roll(list(NSYMBOLS), -1))
            number = rolled.index(rank)
            heart = self.make_heart(t=number/12)
            heart.scale(1.2, 1.2)
            corners = self.make_corners(rank, heart, suit)
            center, rings = self.arrange_center(rank, heart, suit)

        elif suit == "S":
            rolled = list(np.roll(list(NSYMBOLS), -1))
            number = rolled.index(rank)
            spade = self.make_spade(t=number/12)
            corners = self.make_corners(rank, spade, suit)
            center, rings = self.arrange_center(rank, spade, suit)

        card_face = G(background, corners, rings, center)
        return card_face

    def arrange_center(self, rank, suit, suit_text, flip_allowed=True):

        number = NSYMBOLS.index(rank)

        # Face cards
        if number > 9: number = 0 #return G()

        placements = SPOTS[number]
        center_w = (self.sx-2*self.inset)*0.9
        center_h = self.sy*0.9
        gw = center_w/3
        scale = gw/inch
        rings = []
        cmap = {"D": {"strokeColor": RED}, "H": {"strokeColor": RED}, "C": {}, "S": {}}
        rstyle = dict(fillColor=self.base_color, strokeWidth=2, **cmap[suit_text])
        if rank in "JQKA":
            scale*=2.2
            rings.append(G(
                *[shapes.Circle(0,0, inch*scale*(1.2/2 + i*.05), **rstyle)
                  for i in range("JQKA".index(rank) + 1)][::-1]
            ))

        def map_loc(x,y,r):
            if number+1 >= 9:
                if x == 1: gh = center_h/7
                else: gh = center_h/4
            else:
                gh = center_h/5

            x_ = -center_w/2 + gw/2 + gw*x
            y_ = center_h/2 - gh/2 - gh*y
            return x_, y_

        symbols = []
        for sp in placements.split():
            flip = sp.startswith("-")
            s = sp.lstrip("-")
            r, c = list(map(int, s))
            suit_ = copy.deepcopy(G(suit))
            suit_.translate(*map_loc(r, c, rank))
            suit_.scale(scale, scale)
            if flip and flip_allowed: suit_.rotate(180)
            symbols.append(suit_)

        return G(*symbols), G(*rings)

    def make_corners(self, string, suit, suit_text):

        font = "cards"
        shift=0
        if string == "T":
            string = "10"
            font = "cardsnarrow"
            shift = .1

        sx, sy, i, w = self.sx, self.sy, self.inset, self.x
        x, y = (sx-i)/2, sy/2 - i*1.1
        size = 0.85*i
        cmap = {"D": {"fillColor": RED}, "H": {"fillColor": RED}, "C": {}, "S": {}}

        rank = shapes.String(-size*(1.303+shift)/2.9, 0, string,
            fontName=font, fontSize=INCH_TO_FONTSIZE*1.2*size/inch,
            **cmap[suit_text])

        suit = G(suit)
        suit.translate(0, -size)
        suit.scale(size/inch, size/inch)

        corner = G(rank, suit)

        corner.translate(-x, y)
        topright = G(corner)
        topright.translate(2*x)
        top = G(topright, corner)
        bottom = G(top)
        bottom.scale(1, -1)

        corners = G(bottom, top)
        return corners

    def set(self, **d):
        s = copy.deepcopy(settings)
        s.update(d)
        self.canvas.setLineWidth(s["lw"])

    def draw_frames(self, dev=False):
        """Draw the trim and safe zones."""
        c = self.canvas
        b, s = self.bleed, self.safety
        x, y, sx, sy = self.x, self.y, self.sx, self.sy
        i = self.inset

        path = c.beginPath()
        self.set(lw=.1)
        if dev: path.rect(-x/2, -y/2, x, y)
        if dev: path.rect(-sx/2, -sy/2, sx, sy)
        if dev: path.rect(-(sx-2*i)/2, -sy/2, sx-2*i, sy)
        # path.rect(-sx/2*.99, -sy/2*.99, sx*.99, sy*.99)
        c.drawPath(path, stroke=1)

    # SUIT DECALS

    def make_club(self, scale=1.0):
        scale = scale*(2*inch/10/np.pi*1.45)
        l = scale*inch/10
        self.set(lw=scale/2)
        r = l*.47
        men = []
        for angle in [-np.pi/2, 0, np.pi/2, np.pi]:
            shift = r*np.array([np.sin(-angle), np.cos(angle)])
            man = self.make_club_man(scale=scale,
                 angle=180/np.pi*angle, bottom=angle==np.pi)
            man.translate(*shift)
            man.rotate(180/np.pi*angle)
            men.append(man)

        return G(*men)

    def make_diamond(self, random=False):

        path = diamond_2D(random=random, base_color=self.base_color)
        g = G(path)
        g.scale(0.2, 0.2)
        return g

    def make_heart(self, t=0.0):

        a = inch/6
        s=a/10*(1-t) + a/5*t
        b = inch*.8
        c = 1.1*inch
        r = a/2
        nofill = dict(fillColor=self.base_color, strokeOpacity=0.0, strokeWidth=0.0)
        fill = dict(strokeOpacity=0.0, strokeWidth=0.0, fillColor=RED)

        center = G(
            # shapes.Circle(0, 0, inch/3, **fill),
            shapes.Circle(0, 0, a/2+s, **nofill),
            shapes.Circle(0, 0, a/2, **fill),
        )

        lep = lambda a, b: a*(1-t) + b*t
        lep_d = lambda a, b: a * (1-t**2) + b*t**2
        lep_s = lambda a, b: a * (1-(t+1e-12)**(1/2)) + b*(t+1e-12)**(1/2)
        an = lambda t_: np.array([np.cos(t_), np.sin(t_)])
        top = shapes.Path(**fill)
        left = shapes.Path(**fill)
        nin = 8
        skw = np.array([.55, .15])
        shft = np.array([0., 1.6*r])
        crc_in = lambda t_: list(a*.8*an(t_*2*np.pi/nin)*skw + shft)
        crc_out = lambda t_: list((a*an(t_*(2*np.pi/12) + np.pi/4))*skw + shft)
        def star(t_):
            n = 1.
            div = 1/.5523
            vec = np.array([
                [n, 0], [1, n/div], [n/div, 1],
                [0, n], [-n/div, 1], [-1, n/div],
                [-n, 0], [-1, -n/div], [-n/div, -1], [0, -n],
                [n/div, -1], [1, -n/div],
            ])[t_]/n*8
            return skw*vec + shft

        def crc_rnd(t_):
            if t_ > 0 and t_ < 6: return a*an(np.pi/2)*skw + shft
            elif t==0: return a*an(0)*skw + shft
            elif t==6: return a*an(np.pi)*skw + shft
            return a*an(-np.pi/2)*skw + shft

        # for t__ in range(0, 12):
        #     print(t__, crc_rnd(t__))

        H=0.45
        top_segs = {
            "cl":(
                lep(r*an(np.pi/2+np.pi/6)[0], star(9)[0]), lep(r*an(np.pi/2+np.pi/6)[1], star(9)[1]),
                lep(-r, star(8)[0]), lep((2.7-H)*r, star(8)[1]),
                lep_s(-3.7*r, star(7)[0]), lep((3.2-H)*r,star(7)[1]),
                lep_s(-3.8*r, star(6)[0]), lep((3.4-H)*r,star(6)[1]),
            ),
            "tl":(
                lep_s(-2.4*r,star(5)[0]), lep((5.5-H)*r,star(5)[1]),
                lep(-1*r,star(4)[0]), lep((4.7-H)*r,star(4)[1]),
                lep_d(0*r,star(3)[0]), lep_d((3.4-H)*r,star(3)[1]),
            ),
            "tr":(
                lep(1*r,star(2)[0]), lep((4.7-H)*r,star(2)[1]),
                lep_s(2.4*r,star(1)[0]), lep((5.5-H)*r,star(1)[1]),
                lep_s(3.8*r,star(0)[0]), lep((3.4-H)*r,star(0)[1]),
            ),
            "cr":(
                lep_s(3.7*r,star(11)[0]), lep((3.2-H)*r,star(11)[1]),
                lep(r,star(10)[0]), lep((2.7-H)*r,star(10)[1]),
                lep(r*an(np.pi/2-np.pi/6)[0], star(9)[0]), lep(r*an(np.pi/2-np.pi/6)[1], star(9)[1]),
            ),
        }
        left_segs = {
            "cl":(
                lep(r*an(np.pi/2+np.pi/6)[0], r*an(np.pi/2+np.pi/3)[0]), lep(r*an(np.pi/2+np.pi/6)[1], r*an(np.pi/2+np.pi/3)[1]),
                lep(-r, -r/2), lep((2.4-H)*r, (2.4-H)*r),
                lep(-3.7*r, -2.1*r), lep((2.9-H)*r, (2.9-H)*r),
                lep(-3.8*r, -2.4*r), lep((3.4-H)*r, (4.3-H)*r),
            ),
            "el": (
                lep(-5*r, -7*r), lep((-0.6-H)*r, (-0.6-H)*r),
                lep(-r/2*1.1, -r/2*1.1), lep(-r*(3.1+H), -r*(3.1+H)),
                lep(0, -r), lep((-4.6-H)*r, (-4.6-H)*r),
            ),
            "fin": (
                lep(-r/8, -r/8), lep(0, 0),
            )
        }

        def make_path(pth, seg):
            if len(seg) == 8:
                pth.moveTo(seg[0], seg[1])
                pth.curveTo(seg[-6], seg[-5],
                            seg[-4], seg[-3],
                            seg[-2], seg[-1])
            elif len(seg) == 6:
                pth.curveTo(seg[-6], seg[-5],
                            seg[-4], seg[-3],
                            seg[-2], seg[-1])
            elif len(seg) == 2:
                pth.lineTo(seg[0], seg[1])
            return pth

        # flip_seg("cl", reorder=True)
        # flip_seg("tl", reorder=True)
        for seg in top_segs.values(): make_path(top, seg)
        top.closePath()
        for seg in left_segs.values(): make_path(left, seg)
        left.closePath()
        # make_path(top, segs["cr"])
        # make_path(top, segs["tr"])
        # top.closePath()

        left = G(left)
        right = G(left)
        right.scale(-1.0)
        wings = G(left, right)

        return G(
            top,
            wings,
            center,
        )

    def make_spade(self, t=0.0):
        a = inch/5
        s=a/10*(1-t) + a/5*t
        b = inch*.8
        c = 1.1*inch
        nofill = dict(fillColor=self.base_color, strokeOpacity=0.0, strokeWidth=0.0)
        fill = dict(strokeOpacity=0.0, strokeWidth=0.0)

        center = G(
            # shapes.Circle(0, 0, inch/3, **fill),
            shapes.Circle(0, 0, a/2+s, **nofill),
            shapes.Circle(0, 0, a/2, **fill),
        )
        # Right leaf
        trn = lambda x, y, xf, yf: [x*(1-t) + xf*t, y*(1-t) + yf*t]
        an = lambda t: np.array([np.cos(t), np.sin(t)])
        bot = shapes.Path(**fill)
        bot.moveTo(*trn(0, -b/2.5, 0, -b/1.7))
        crc = lambda a: list(b/1.7*an(a))
        bot.curveTo(
            *trn(a/2*(1/3), -b/2.5, *crc(-np.pi/2 + np.pi/18)),
            *trn(a/2*(2/3), -b/2.5, *crc(-np.pi/2 + 2*np.pi/18)),
            *trn(a/2*(3/3), -b/2.5, *crc(-np.pi/2 + 3*np.pi/18)),
        )
        rbase = a/2 + s
        dest = rbase*an(-np.pi/2 + (s/2)/rbase)
        bot.curveTo(
            *trn(a/2*(2.5/3), -b/3*2/3, 0, 0),
            *trn(a/2*(1/5), -b/3 * 1.8/3, 0, 0),
            *trn(dest[0], dest[1], 0, 0),
        )
        bot.lineTo(-s/6,0)
        bot.closePath()

        right = shapes.Path(**fill)
        right.moveTo(*trn(*s*an(np.pi/3), 0, 0))
        right.lineTo(*trn(s/2, a/2+s, 0, 0))
        right.lineTo(*trn(s/2, b*2/3, *crc(np.pi/2 - np.pi/6)))
        # right.lineTo(*b/2*an(-np.pi/3))
        dest2 = rbase*an(-np.pi/2 + (s*3/2)/rbase)
        right.curveTo(
            *trn(b/2.5, c*1/3, *crc(2*np.pi/9)),
            *trn(b/1.5, -b*.56,*crc(np.pi/9)),
            *trn(dest2[0], dest2[1], *crc(0)),
        )
        right.closePath()
        right = G(right, bot)

        left = G(right)
        left.scale(-1)

        return G(
            right,
            left,
            center,
        )

    def draw(self, s):
        drawing = shapes.Drawing(0.0,0.0)
        drawing.add(s)
        renderPDF.draw(drawing, self.canvas, 0.0, 0.0)

    def make_club_man(self, scale=1.0, angle=0.0, bottom=False):
        l = scale*inch/10
        r = l/np.pi
        base = dict(fillColor=self.base_color, strokeWidth=l/50)
        cw, ch = r/5, r*1.3/5
        sclw, sclh = 0.5, 0.66

        if bottom:
            out = shapes.Path(strokeOpacity=0.0)
            out.moveTo(0.006*r, r*.95)
            out.lineTo(1.1*r, r*.95)
            out.curveTo(1.2*r, r/2, cw*1.5, 0, cw*1.18, -r*.63)
            out.lineTo(0.006*r, -r*.63)
            out.curveTo(cw*1.5, 0, cw*2.5, 0, 0.4*r, r/2)
            out.lineTo(0.006*r, r/2)
            out.closePath()
            arms = G(out)
            right = G(arms)
            right.scale(-1)
            arms = G(arms, right)
        else:
            arms = G(shapes.Circle(0, 0, r*1.04, strokeOpacity=0),
                     shapes.Circle(0, -r*.102, r/1.35, strokeOpacity=0, fillColor=self.base_color))

        man = G(
            # head
            shapes.Circle(0, r*.7, r*.5, strokeWidth=l/100, strokeOpacity=0.0, fillColor=self.base_color),
            shapes.Circle(0, r*.7, r*.35, strokeWidth=l/20),
            shapes.Rect(-r*.5, -r*1.0, r, r*.385, strokeOpacity=.0, **base),
            shapes.Rect(-r*.25*1.3, -r*1.1, r/2*1.3, r*.13, strokeOpacity=.0, **base),
        )
        card = G(shapes.Rect(cw*(1-sclw)/2, ch*(1-sclh)/2, cw*sclw, ch*sclh, strokeWidth=l/100),
                 shapes.Rect(0, 0, cw, ch, fillOpacity=0, strokeWidth=l/100, fillColor=self.base_color))
        down = G(card)
        down.translate(-cw/2, -4.6*cw)
        cards = [G(down) for _ in range(4)]
        for i, c in enumerate(cards):
            pos = -1.8 + i*2*1.8/3
            c.translate(pos*cw, 0)

        # return G(*([arms]+cards))
        return G(*([arms, man]+cards))

    def show(self, path=None):
        if path is None: path = self.path
        print(f"Writing to {path}")
        self.canvas.save()
        os.system(f"open {path}")

def diamond_verticies():

    diamond = [
    # Tips
    (0.0, 0.0, 2.0), (0.0, 0.0, -2.0),
    (1.0, 0.0, 0.8), (0.5, 0.866, 0.8), (-0.5, 0.866, 0.8), 
    (-1.0, 0.0, 0.8), (-0.5, -0.866, 0.8), (0.5, -0.866, 0.8),
    (1.5, 0.0, 0.0), (1.299, 0.75, 0.0), (0.75, 1.299, 0.0), 
    (0.0, 1.5, 0.0), (-0.75, 1.299, 0.0), (-1.299, 0.75, 0.0),
    (-1.5, 0.0, 0.0), (-1.299, -0.75, 0.0), (-0.75, -1.299, 0.0), 
    (0.0, -1.5, 0.0), (0.75, -1.299, 0.0), (1.299, -0.75, 0.0),
    (1.0, 0.0, -0.8), (0.5, 0.866, -0.8), (-0.5, 0.866, -0.8), 
    (-1.0, 0.0, -0.8), (-0.5, -0.866, -0.8), (0.5, -0.866, -0.8)
    ]

    sl = .5
    for i, d in enumerate(diamond):
        if i in range(8, 20):
            diamond[i] = (d[0]*sl, d[1]*sl, d[2])

    # A simple tetrahedron
    test_points = [
        (0., 0., 1.),   # Point 0
        (1., 0., 0.), # Point 1
        (0., 1., 0.), # Point 2
        (1., 1., 0.)  # Point 3
    ]
    return diamond

def generate_dynamic_crystal(nring=7, height=.3, freq=3.0, w=.5, amplitude=.02):
    """
    Generates a diamond-shaped crystal with oscillating rings.
    
    Args:
        nring: Number of points per ring.
        height: Vertical distance between the two rings.
        freq: How many oscillations occur around the circle.
        amplitude: The strength of the Z-oscillation.
    """
    points = []
    
    # 1. Top and Bottom Tips
    tip_height = height + 1.0
    points.append((0, 0, tip_height))  # Index 0
    points.append((0, 0, -tip_height)) # Index 1
    
    # Angles for the points in the rings
    angles = np.linspace(0, 2 * np.pi, nring, endpoint=False)
    
    # 2. Upper Ring
    z_offset_upper = height / 2
    for theta in angles:
        # Oscillate Z based on frequency
        z = z_offset_upper + amplitude * np.sin(freq * theta)
        x = w*np.cos(theta)
        y = w*np.sin(theta)
        points.append((x, y, z))
        
    # 3. Lower Ring
    z_offset_lower = -height / 2
    for theta in angles-np.pi/nring:
        # Oscillate Z (offset by pi to make peaks/valleys alternate)
        z = z_offset_lower + amplitude * np.sin(freq * theta + np.pi)
        x = w*np.cos(theta)
        y = w*np.sin(theta)
        points.append((x, y, z))

    d = np.array(points)
    d *= 3
        
    return list(d)

def project_points(points, azimuth_deg, elevation_deg, distance, focal_length=500):
    """
    Projects 3D points onto a 2D plane based on camera position.
    
    Args:
        points: List or array of (x, y, z) tuples.
        azimuth_deg: Horizontal angle of camera in degrees.
        elevation_deg: Vertical angle of camera in degrees.
        distance: Radial distance of camera from the origin (0,0,0).
        focal_length: Determines the strength of the perspective warp.
        
    Returns:
        List of tuples: (u, v, d) where (u, v) are 2D coordinates 
        and d is the distance from the camera.
    """
    # Convert angles to radians
    az = np.radians(azimuth_deg)
    el = np.radians(elevation_deg)
    
    # 1. Calculate Camera Position (Cartesian)
    cx = distance * np.cos(el) * np.cos(az)
    cy = distance * np.cos(el) * np.sin(az)
    cz = distance * np.sin(el)
    camera_pos = np.array([cx, cy, cz])
    
    # 2. Define Camera Basis (Look-at origin)
    # Forward vector (pointing from camera to origin)
    forward = -camera_pos / np.linalg.norm(camera_pos)
    # Right vector (orthogonal to forward and world "up")
    up_world = np.array([0, 0, 1])
    right = np.cross(forward, up_world)
    if np.linalg.norm(right) < 1e-6: # Handle gimbal lock at poles
        right = np.array([1, 0, 0])
    right /= np.linalg.norm(right)
    # Re-calculate camera-up
    up = np.cross(right, forward)
    
    projected_data = []
    
    for p in points:
        # Vector from camera to point
        rel_p = np.array(p) - camera_pos
        
        # 3. Transform point to Camera Space
        # z_cam is the depth along the camera's viewing axis
        z_cam = np.dot(rel_p, forward)
        x_cam = np.dot(rel_p, right)
        y_cam = np.dot(rel_p, up)
        
        # Distance from camera
        dist_to_cam = np.linalg.norm(rel_p)
        
        # 4. Perspective Projection
        # Prevent division by zero if point is behind camera
        if z_cam > 0:
            u = (x_cam * focal_length) / z_cam
            v = (y_cam * focal_length) / z_cam
            projected_data.append((u, v, dist_to_cam))
        else:
            # Point is behind or at the camera plane
            projected_data.append((None, None, dist_to_cam))
            
    return projected_data

def rotate_crystal_randomly(points):
    """
    Applies a random 3D rotation to a list of points.
    
    Args:
        points: List of (x, y, z) tuples.
        
    Returns:
        List of (x, y, z) tuples after rotation.
    """
    # Generate random angles for each axis in radians
    # rx = 2*np.pi*np.random.random()
    # ry = 2*np.pi*np.random.random()
    # rz = 2*np.pi*np.random.random()
    rx = np.random.random()*.5 - .25
    ry = np.random.random()*.5 - .25
    rz = np.random.random()*.5 - .25

    # Rotation matrix for X-axis
    rot_x = np.array([
        [1, 0, 0],
        [0, np.cos(rx), -np.sin(rx)],
        [0, np.sin(rx), np.cos(rx)]
    ])

    # Rotation matrix for Y-axis
    rot_y = np.array([
        [np.cos(ry), 0, np.sin(ry)],
        [0, 1, 0],
        [-np.sin(ry), 0, np.cos(ry)]
    ])

    # Rotation matrix for Z-axis
    rot_z = np.array([
        [np.cos(rz), -np.sin(rz), 0],
        [np.sin(rz), np.cos(rz), 0],
        [0, 0, 1]
    ])

    # Combine rotations: R = Rz * Ry * Rx
    rotation_matrix = rot_z @ rot_y @ rot_x

    # Apply to all points
    rotated_points = [tuple(rotation_matrix @ np.array(p)) for p in points]
    
    return rotated_points

def get_visible_front_faces(points_3d, projected_results, facets, camera_pos):
    """
    Identifies faces pointing toward the camera and packages their 3D and 2D data.
    
    Args:
        points_3d: The (potentially rotated) 3D coordinates.
        projected_results: The (u, v, d) output from project_points.
        facets: List of vertex index tuples, e.g., [(0, 1, 2), (0, 2, 3)...]
        camera_pos: The (x, y, z) position of the camera in world space.
        
    Returns:
        List of dictionaries containing indices, 2D points, and depth.
    """
    visible_faces_data = []
    cam_vec = np.array(camera_pos)

    for vertex_indices in facets:
        # 1. Retrieve the 3D coordinates using the indices
        # We need at least 3 points to calculate a surface normal
        p0 = np.array(points_3d[vertex_indices[0]])
        p1 = np.array(points_3d[vertex_indices[1]])
        p2 = np.array(points_3d[vertex_indices[2]])

        # 2. Calculate the Normal Vector (Right-hand rule)
        normal = np.cross(p1 - p0, p2 - p0)
        
        # 3. Calculate Vector from face to camera
        # We use the average of the 3D points as the face center
        face_center = np.mean([points_3d[i] for i in vertex_indices], axis=0)
        view_dir = cam_vec - face_center

        # 4. Visibility Check (Back-face Culling)
        # If the dot product is positive, the face is pointing toward the camera
        if np.dot(normal, view_dir) > 0:
            
            # 5. Package 2D coordinates and depth from our projection results
            face_2d_points = []
            total_depth = 0
            
            for idx in vertex_indices:
                u, v, d = projected_results[idx]
                face_2d_points.append((u, v))
                total_depth += d
            
            # We store the 'indices' specifically so the shading function 
            # can look up the 3D normals later.
            visible_faces_data.append({
                'indices': vertex_indices,
                'points_2d': face_2d_points,
                'depth': total_depth / len(vertex_indices)
            })

    # Sort by depth (Painter's Algorithm) so furthest faces are drawn first
    visible_faces_data.sort(key=lambda x: x['depth'], reverse=True)
    return visible_faces_data

def get_ccw_simplices(points):
    hull = ConvexHull(points)
    # return hull.simplices

    ordered_simplices = []
    
    for i, simplex in enumerate(hull.simplices):
        # Current vertex coordinates for this face
        v0, v1, v2 = points[simplex]
        
        # 1. Calculated normal from current order
        calc_normal = np.cross(v1 - v0, v2 - v0)
        
        # 2. Outward normal from SciPy equations [A, B, C, D]
        outward_normal = hull.equations[i, :3]
        
        # 3. Fix order if it points inward
        if np.dot(calc_normal, outward_normal) > 0:
            # Swap indices 1 and 2 to flip winding
            ordered_simplex = [simplex[0], simplex[2], simplex[1]]
        else:
            ordered_simplex = simplex
            
        ordered_simplices.append(ordered_simplex)
        
    simp = np.array(ordered_simplices)
    return simp

def derive_facets_from_points(points_3d):
    """
    Computes the convex hull of a set of 3D points to find the surface facets.
    
    Args:
        points_3d: List or array of (x, y, z) tuples.
        
    Returns:
        List of tuples: Each tuple contains 3 indices of points forming a triangular facet.
    """
    # Convert to numpy array for processing
    pts = np.array(points_3d)
    
    # Generate the Convex Hull
    simplices = get_ccw_simplices(pts)
    
    # hull.simplices is an (N, 3) array where each row is a triangle
    facets = [tuple(simplex) for simplex in simplices]
    
    return facets

def calculate_face_shading(points_3d, visible_facets, base_color, light_source_pos):
    """
    Calculates the shaded color for each facet based on a light source.
    """
    light_pos = np.array(light_source_pos)
    shaded_faces_data = []
    
    # Base color in RGB (0-1 range for math)
    from reportlab.lib.colors import Color
    # Helper to convert ReportLab color to normalized numpy array
    def rl_to_np(rl_col):
        return np.array([rl_col.red, rl_col.green, rl_col.blue])

    base_rgb = rl_to_np(base_color)
    
    # Define Ambient Light (minimum brightness, prevents total blackness)
    ambient_intensity = 0.65
    
    for facet in visible_facets:
        # 1. Get Geometry
        pts = np.array([points_3d[i] for i in facet['indices']])
        p0, p1, p2 = pts[0], pts[1], pts[2]
        
        # 2. Calculate Face Normal (re-calculating or passing from culling)
        v1 = p1 - p0
        v2 = p2 - p0
        normal = np.cross(v1, v2)
        norm_val = np.linalg.norm(normal)
        if norm_val < 1e-9: continue # Skip degenerate triangles
        normal /= norm_val
        
        # 3. Calculate Light Vector (from face center to light)
        face_center = np.mean(pts, axis=0)
        light_vec = light_pos - face_center
        light_vec_norm = np.linalg.norm(light_vec)
        if light_vec_norm < 1e-9: continue
        light_vec /= light_vec_norm
        
        # 4. Lambertian Shading (Dot Product)
        # Intensity is the cosine of the angle between normal and light
        # np.dot(normal, light_vec) is maximized (1.0) when they align
        diffuse_intensity = max(0, np.dot(normal, light_vec))
        
        # 5. Combine Intensities and Apply to Color
        total_intensity = min(1.0, ambient_intensity + (1.0 - ambient_intensity) * diffuse_intensity)
        
        shaded_rgb = base_rgb * total_intensity
        
        # Convert back to ReportLab Color
        final_color = colors.CMYKColor(*colors.rgb2cmyk(shaded_rgb[0], shaded_rgb[1], shaded_rgb[2]), alpha=base_color.alpha)
        
        shaded_faces_data.append({
            'points_2d': facet['points_2d'], # From project_points
            'depth': facet['depth'],
            'color': final_color
        })
        
    # Sort by depth again (crucial for flat shading)
    shaded_faces_data.sort(key=lambda x: x['depth'], reverse=True)
    
    return shaded_faces_data

def draw_shaded_crystal(shaded_faces_data, base_color=TAN):
    """
    Draws the crystal using pre-calculated shaded colors for each face.
    """
    group = []# shapes.Group()
    
    for face in shaded_faces_data:
        points_2d = face['points_2d']
        fill_color = face['color']
        
        # Flatten [(x1,y1), (x2,y2)] to [x1, y1, x2, y2]
        flattened = [coord for pt in points_2d for coord in pt]
        
        # Draw the polygon with shaded fill
        poly = shapes.Polygon(
            flattened,
            # Use a slightly darker stroke than the fill for definition, or None
            strokeColor=base_color, 
            strokeWidth=.01,
            # strokeOpacity=0.0,
            fillColor=fill_color
        )
        group.append(poly)

    
    return G(*group[::-1])

def diamond_2D(random=False, base_color=TAN):

    # crystal_points = diamond_verticies()
    crystal_points = generate_dynamic_crystal()

    if random: crystal_points = rotate_crystal_randomly(crystal_points)

    facets = derive_facets_from_points(crystal_points)

    camera_pos = [0, 0, 0]
    light_pos = [5, 10, 0]
    projected = project_points(crystal_points, azimuth_deg=0, elevation_deg=0, distance=10)
    base_crystal_color = RED

    # for i, (u, v, d) in enumerate(results):
    #     if u is not None:
    #         print(f"Point {i}: 2D Position = ({u:.2f}, {v:.2f}), Distance = {d:.2f}")

    visible_facets_data = get_visible_front_faces(crystal_points, projected, facets, camera_pos)

    shaded_data = calculate_face_shading(crystal_points, visible_facets_data, base_crystal_color, light_pos)

    group = draw_shaded_crystal(shaded_data, base_color=base_color)
    return group


def generate_shape_group(heart, angel, t=0, scale=100, fill_color=RED, stroke_color=MUTED):
    """
    Converts nested Bezier path data into a ReportLab Group object.
    
    Args:
        paths_data: List of paths, each containing (start_pt, bezier_tuple) segments.
        scale: Multiplier to convert normalized coordinates to points.
        fill_color: The color to fill the paths.
        stroke_color: The color of the path outlines.
        
    Returns:
        reportlab.graphics.shapes.Group: A group containing the 3 path objects.
    """
    main_group = shapes.Group()

    lep = lambda a, b: a*(1-t) + b*t

    for he, an in zip(heart, angel):
        # Initialize a new Path object for this specific sub-path
        lp = shapes.Path(
            fillColor=fill_color,
            strokeColor=stroke_color,
            strokeOpacity=0.0 # Maintain relative line weight
        )
        
        # 1. Extract and scale the very first starting point
        first_start_xh = he[0][0][0] * scale
        first_start_yh = he[0][0][1] * scale
        first_start_xa = an[0][0][0] * scale
        first_start_ya = an[0][0][1] * scale
        lp.moveTo(lep(first_start_xh, first_start_ya) , lep(first_start_yh, first_start_ya))
        
        # 2. Iterate through segments and add cubic curves
        for (_, hbt), (_, abt) in zip(he, an):
            # Scale each coordinate in the cubic tuple: (cp1, cp2, end)
            coords = []
            for hb, ab in zip(hbt, abt):
                coords.append(lep(hb[0],ab[0]) * scale)
                coords.append(lep(hb[1],ab[1]) * scale)
                print(coords) 
            lp.curveTo(*coords)
            
        lp.closePath()
        main_group.add(lp)
        
    return main_group

def get_heart_group(t=0):

    # Constants
    Xc = 2.0  # Center X
    Y_top = 1.0
    Y_mid = 2.0
    Y_low = 3.0
    Y_bot = 3.2

    # Offsets
    W_narrow = 0.1  # For the "dip" or "robe"
    W_med    = 0.5  # For the head/inner wings
    W_wide   = 1.0  # For the outer lobes/wings

    heart_points = [
        # Path 1: Left Lobe
        [
            ((Xc, Y_top), ((Xc, 0.5), (Xc - W_wide, 0.5), (Xc - W_wide, 1.5))),
            ((Xc - W_wide, 1.5), ((Xc - W_wide, Y_mid), (Xc - W_med, 2.5), (Xc, Y_low))),
            ((Xc, Y_low), ((Xc, Y_low), (Xc, Y_low), (Xc, Y_low))) # Anchor
        ],
        # Path 2: Right Lobe (Symmetric to Path 1)
        [
            ((Xc, Y_top), ((Xc, 0.5), (Xc + W_wide, 0.5), (Xc + W_wide, 1.5))),
            ((Xc + W_wide, 1.5), ((Xc + W_wide, Y_mid), (Xc + W_med, 2.5), (Xc, Y_low))),
            ((Xc, Y_low), ((Xc, Y_low), (Xc, Y_low), (Xc, Y_low))) # Anchor
        ],
        # Path 3: Central Dip (Matching Angel Head segment count)
        [
            ((Xc, Y_top), ((Xc - W_narrow, 1.1), (Xc + W_narrow, 1.1), (Xc, Y_top))),
            ((Xc, Y_top), ((Xc, Y_top), (Xc, Y_top), (Xc, Y_top))) # Degenerate
        ]
    ]

    angel_points = [
        # Path 1: Left Wing & Robe side
        [
            ((Xc, 1.8), ((Xc - W_med, Y_top), (Xc - 1.5, 1.5), (Xc - 1.2, Y_mid))),
            ((Xc - 1.2, Y_mid), ((Xc - W_wide, 2.5), (Xc - 0.2, 2.3), (Xc, 2.5))),
            ((Xc, 2.5), ((Xc - W_narrow, 2.8), (Xc - 0.3, Y_low), (Xc, Y_bot)))
        ],
        # Path 2: Right Wing & Robe side (Symmetric to Path 1)
        [
            ((Xc, 1.8), ((Xc + W_med, Y_top), (Xc + 1.5, 1.5), (Xc + 1.2, Y_mid))),
            ((Xc + 1.2, Y_mid), ((Xc + W_wide, 2.5), (Xc + 0.2, 2.3), (Xc, 2.5))),
            ((Xc, 2.5), ((Xc + W_narrow, 2.8), (Xc + 0.3, Y_low), (Xc, Y_bot)))
        ],
        # Path 3: The Head (Two halves of a circle)
        [
            ((Xc, 1.8), ((Xc - 0.3, 1.8), (Xc - 0.3, 1.2), (Xc, 1.2))),
            ((Xc, 1.2), ((Xc + 0.3, 1.2), (Xc + 0.3, 1.8), (Xc, 1.8)))
        ]
    ]

    return generate_shape_group(heart_points, angel_points, t=t)
