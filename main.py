# main.py
# Мобильное приложение "Оптические иллюзии" на Pygame
# Запуск: python main.py  (на Android через pgs4a / pygame-ce for Android)

import pygame, math, sys, os, random

pygame.init()

# ---------------- Виртуальное разрешение (9:16) ----------------
VW, VH = 540, 960

# ---------------- Палитра (тёплый "бумажный" минимализм) ----------------
BG       = (243, 237, 227)
DARK     = (38, 48, 62)
MID      = (120, 130, 145)
LIGHT    = (215, 205, 190)
ACCENT   = (195, 80, 60)
ACCENT2  = (70, 110, 150)
CARD     = (255, 252, 245)
CARD_P   = (238, 230, 215)
SHADOW   = (210, 198, 180)
WHITE    = (255, 255, 255)
BLACK    = (0, 0, 0)

# ---------------- Шрифты с поддержкой кириллицы ----------------
_font_cache = {}
_font_path  = [None]

def _find_font():
    if _font_path[0] is not None:
        return _font_path[0]
    for c in [
        '/system/fonts/Roboto-Regular.ttf',
        '/system/fonts/DroidSans.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/TTF/DejaVuSans.ttf',
        'C:/Windows/Fonts/segoeui.ttf',
        'C:/Windows/Fonts/arial.ttf',
        '/Library/Fonts/Arial.ttf',
    ]:
        if os.path.exists(c):
            _font_path[0] = c
            return c
    _font_path[0] = ''
    return ''

def F(size, bold=False):
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]
    p = _find_font()
    f = pygame.font.Font(p if p else None, size)
    f.set_bold(bold)
    _font_cache[key] = f
    return f

def wrap(text, f, max_w):
    words = text.split()
    lines, cur = [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if f.size(t)[0] <= max_w or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def text(surf, s, size, color, center=None, topleft=None, bold=False, max_w=None):
    f = F(size, bold)
    lines = wrap(s, f, max_w) if max_w else s.split('\n')
    lh = f.get_linesize()
    y0 = center[1] - lh*len(lines)//2 if center else topleft[1]
    x0 = center[0] if center else topleft[0]
    for i, ln in enumerate(lines):
        r = f.render(ln, True, color)
        if center:
            surf.blit(r, (x0 - r.get_width()//2, y0 + i*lh))
        else:
            surf.blit(r, (x0, y0 + i*lh))

# ================================================================
#                        ИЛЛЮЗИИ
# ================================================================

def _c(surf, color, pts):
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts])

# 1. Мюллер-Лайер
def ill_muller(surf, r, t):
    cx, cy = r.center
    half = int(r.width * 0.30); ah = int(r.width * 0.06)
    y1, y2 = cy - int(r.height*0.10), cy + int(r.height*0.10)
    # верхняя — стрелки наружу
    pygame.draw.line(surf, DARK, (cx-half, y1), (cx+half, y1), 4)
    pygame.draw.line(surf, DARK, (cx-half, y1), (cx-half-ah, y1-ah), 4)
    pygame.draw.line(surf, DARK, (cx-half, y1), (cx-half-ah, y1+ah), 4)
    pygame.draw.line(surf, DARK, (cx+half, y1), (cx+half+ah, y1-ah), 4)
    pygame.draw.line(surf, DARK, (cx+half, y1), (cx+half+ah, y1+ah), 4)
    # нижняя — стрелки внутрь
    pygame.draw.line(surf, DARK, (cx-half, y2), (cx+half, y2), 4)
    pygame.draw.line(surf, DARK, (cx-half, y2), (cx-half+ah, y2-ah), 4)
    pygame.draw.line(surf, DARK, (cx-half, y2), (cx-half+ah, y2+ah), 4)
    pygame.draw.line(surf, DARK, (cx+half, y2), (cx+half-ah, y2-ah), 4)
    pygame.draw.line(surf, DARK, (cx+half, y2), (cx+half-ah, y2+ah), 4)

# 2. Понцо
def ill_ponzo(surf, r, t):
    cx = r.centerx
    ty, by = r.top + int(r.height*0.10), r.bottom - int(r.height*0.10)
    tg, bg = int(r.width*0.06), int(r.width*0.32)
    pygame.draw.line(surf, DARK, (cx-tg, ty), (cx-bg, by), 4)
    pygame.draw.line(surf, DARK, (cx+tg, ty), (cx+bg, by), 4)
    bar = int(r.width*0.25)
    for yf in (0.30, 0.70):
        y = r.top + int(r.height*yf)
        pygame.draw.line(surf, ACCENT, (cx-bar, y), (cx+bar, y), 6)

# 3. Эббингауз
def ill_ebbinghaus(surf, r, t):
    cx, cy = r.center
    R = int(r.width * 0.12)
    for side, sr in ((-1, r.width*0.075), (1, r.width*0.035)):
        gc = (cx + side*int(r.width*0.22), cy)
        pygame.draw.circle(surf, DARK, gc, R)
        for i in range(6):
            a = i*math.pi/3
            d = R + r.width*0.09
            x = gc[0] + int(d*math.cos(a))
            y = gc[1] + int(d*math.sin(a))
            pygame.draw.circle(surf, DARK, (x, y), int(sr))

# 4. Сетка Германа
def ill_hermann(surf, r, t):
    N = 8
    s = min(r.width, r.height)//N
    ox = r.centerx - s*N//2; oy = r.centery - s*N//2
    for i in range(N):
        for j in range(N):
            pygame.draw.rect(surf, DARK, (ox+i*s+3, oy+j*s+3, s-6, s-6))

# 5. Поггендорф
def ill_poggendorff(surf, r, t):
    cx, cy = r.center
    x1, y1 = cx - int(r.width*0.35), cy + int(r.height*0.30)
    x2, y2 = cx + int(r.width*0.35), cy - int(r.height*0.30)
    pygame.draw.line(surf, DARK, (x1, y1), (x2, y2), 5)
    bw, bh = int(r.width*0.18), int(r.height*0.70)
    pygame.draw.rect(surf, DARK, (cx-bw//2, cy-bh//2, bw, bh))

# 6. Цёлльнер
def ill_zollner(surf, r, t):
    cx, cy = r.center
    sp = int(r.width*0.14); lh = int(r.height*0.70)
    top = cy - lh//2
    for i in range(5):
        x = cx - sp*2 + i*sp
        pygame.draw.line(surf, DARK, (x, top), (x, top+lh), 3)
        for j in range(1, 14):
            y = top + j*lh//14
            if i % 2 == 0:
                pygame.draw.line(surf, DARK, (x-10, y+10), (x+10, y-10), 2)
            else:
                pygame.draw.line(surf, DARK, (x-10, y-10), (x+10, y+10), 2)

# 7. Ястров
def ill_jastrow(surf, r, t):
    cx, cy = r.center
    R = int(r.width*0.22); th = int(r.width*0.09)
    def arc(yc):
        pts = []
        for i in range(41):
            a = -math.pi*0.15 + math.pi*0.55 * i/40
            pts.append((cx + R*math.cos(a), yc + R*math.sin(a)*0.6))
        pygame.draw.lines(surf, DARK, False, pts, th)
    arc(cy - int(r.height*0.10))
    arc(cy + int(r.height*0.10))

# 8. Вундт
def ill_wundt(surf, r, t):
    cx, cy = r.center
    ln = int(r.width*0.65); gap = int(r.height*0.10); ah = int(r.width*0.07)
    for y in (cy-gap, cy+gap):
        x1, x2 = cx-ln//2, cx+ln//2
        pygame.draw.line(surf, DARK, (x1, y), (x2, y), 4)
        pygame.draw.line(surf, DARK, (x1, y), (x1-ah, y+ah), 4)
        pygame.draw.line(surf, DARK, (x2, y), (x2+ah, y+ah), 4)

# 9. Геринг
def ill_hering(surf, r, t):
    cx, cy = r.center
    R = max(r.width, r.height)
    for i in range(24):
        a = i*2*math.pi/24
        pygame.draw.line(surf, MID, (cx, cy),
                         (cx+R*math.cos(a), cy+R*math.sin(a)), 2)
    gap = int(r.height*0.14); w = int(r.width*0.36)
    for y in (cy-gap, cy+gap):
        pygame.draw.line(surf, DARK, (cx-w, y), (cx+w, y), 5)

# 10. Треугольник Канижа
def ill_kanizsa(surf, r, t):
    cx, cy = r.center
    side = min(r.width, r.height)*0.36
    verts = [(cx, cy-side),
             (cx - side*math.sqrt(3)/2, cy + side/2),
             (cx + side*math.sqrt(3)/2, cy + side/2)]
    pr = int(side*0.32)
    for v in verts:
        pygame.draw.circle(surf, DARK, (int(v[0]), int(v[1])), pr)
        ang = math.atan2(cy-v[1], cx-v[0])
        a1, a2 = ang-math.pi/6, ang+math.pi/6
        pts = [v]
        for i in range(21):
            a = a1 + (a2-a1)*i/20
            pts.append((v[0]+pr*math.cos(a), v[1]+pr*math.sin(a)))
        _c(surf, WHITE, pts)

# 11. Комната Эймса (2D)
def ill_ames_room(surf, r, t):
    cx, cy = r.center
    W, H = int(r.width*0.85), int(r.height*0.70)
    tl = (cx-W//2, cy-H//2); tr = (cx+W//3, cy-H//2 + H//8)
    bl = (cx-W//2, cy+H//2); br = (cx+W//3, cy+H//2 - H//8)
    _c(surf, (200, 190, 175), [bl, br, tr, tl])
    for i in range(1, 6):
        f = i/6
        xt = tl[0] + (tr[0]-tl[0])*f; yt = tl[1] + (tr[1]-tl[1])*f
        xb = bl[0] + (br[0]-bl[0])*f; yb = bl[1] + (br[1]-bl[1])*f
        pygame.draw.line(surf, (170, 158, 140), (xt, yt), (xb, yb), 1)
    fh = int(H*0.5); fw = max(8, fh//4)
    lx = cx - W//4; ly = cy + H//2 - int(H*0.15) - fh
    rx = cx + W//6; ry = cy + H//2 - int(H*0.15) - fh
    for fx, fy in ((lx, ly), (rx, ry)):
        pygame.draw.ellipse(surf, DARK, (fx-fw//2, fy, fw, fh))

# 12. Иллюзия Оубисона
def ill_oubison(surf, r, t):
    cx, cy = r.center
    for i in range(-12, 12):
        y = cy + i*16
        pygame.draw.line(surf, LIGHT, (cx-220, y-110), (cx+220, y+110), 2)
    s = int(r.width*0.24); n = 12
    pts = []
    for i in range(n):   # верх
        pts.append((cx-s + 2*s*i/n, cy-s + 8*math.sin(math.pi*i/n)))
    for i in range(n):   # право
        pts.append((cx+s - 8*math.sin(math.pi*i/n), cy-s + 2*s*i/n))
    for i in range(n):   # низ
        pts.append((cx+s - 2*s*i/n, cy+s - 8*math.sin(math.pi*i/n)))
    for i in range(n):   # лево
        pts.append((cx-s + 8*math.sin(math.pi*i/n), cy+s - 2*s*i/n))
    _c(surf, DARK, pts)

# 13. Вращающийся силуэт (каркасный куб)
def ill_rotating_silhouette(surf, r, t):
    cx, cy = r.center
    ang = t*0.7
    size = min(r.width, r.height)*0.16
    verts = [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
             (-1,-1, 1),(1,-1, 1),(1,1, 1),(-1,1, 1)]
    c, s = math.cos(ang), math.sin(ang)
    ry = [(x*c - z*s, y, x*s + z*c) for x,y,z in verts]
    c2, s2 = math.cos(0.35), math.sin(0.35)
    rx = [(x, y*c2 - z*s2, y*s2 + z*c2) for x,y,z in ry]
    pts = []
    for x,y,z in rx:
        f = 3.0/(3.0+z)
        pts.append((cx + x*size*f, cy + y*size*f))
    for a,b in [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),
                (0,4),(1,5),(2,6),(3,7)]:
        pygame.draw.line(surf, DARK, pts[a], pts[b], 4)

# 14. Движущиеся круги Китаоки
def ill_kitaoka(surf, r, t):
    cx, cy = r.center
    NR, NS = 8, 12
    maxr = min(r.width, r.height)*0.42
    for i in range(NR):
        r1 = int(maxr*i/NR); r2 = int(maxr*(i+1)/NR)
        if r2 <= r1: continue
        dirn = 1 if i % 2 == 0 else -1
        off = t*dirn*1.4
        for j in range(NS):
            a1 = j*2*math.pi/NS + off
            a2 = (j+1)*2*math.pi/NS + off
            col = (60,60,60) if j % 2 == 0 else (225,225,225)
            pts = []
            for k in range(6):
                a = a1 + (a2-a1)*k/5
                pts.append((cx + r2*math.cos(a), cy + r2*math.sin(a)))
            for k in range(6):
                a = a2 - (a2-a1)*k/5
                pts.append((cx + r1*math.cos(a), cy + r1*math.sin(a)))
            _c(surf, col, pts)

# 15. Эффект Трокслера
_troxler = None
def _troxler_dots():
    global _troxler
    if _troxler is None:
        rnd = random.Random(42)
        _troxler = []
        for i in range(36):
            ang = rnd.random()*2*math.pi
            dist = 0.18 + rnd.random()*0.32
            rad = 10 + rnd.random()*18
            col = rnd.choice([(140,80,80),(80,140,140),(140,140,80)])
            _troxler.append((ang, dist, rad, col))
    return _troxler

def ill_troxler(surf, r, t):
    cx, cy = r.center
    for ang, dist, rad, col in _troxler_dots():
        x = cx + r.width*dist*math.cos(ang)
        y = cy + r.width*dist*math.sin(ang)
        s = pygame.Surface((int(rad*2), int(rad*2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*col, 110), (int(rad), int(rad)), int(rad))
        surf.blit(s, (x-rad, y-rad))
    pygame.draw.line(surf, DARK, (cx-15, cy), (cx+15, cy), 3)
    pygame.draw.line(surf, DARK, (cx, cy-15), (cx, cy+15), 3)

# 16. Стена кафе
def ill_cafe_wall(surf, r, t):
    cx, cy = r.center
    bw = int(r.width/8); bh = int(r.height/11)
    mo = 2
    rows, cols = 11, 11
    ox = cx - cols*bw//2
    oy = cy - rows*bh//2
    for row in range(rows):
        off = (bw//2) if row % 2 else 0
        for col in range(cols+2):
            x = ox + (col-1)*bw + off
            y = oy + row*bh
            col_ = (28,28,28) if (col+row) % 2 == 0 else (240,240,240)
            pygame.draw.rect(surf, col_, (x+mo, y+mo, bw-2*mo, bh-2*mo))

# 17. Шевелящиеся змеи (статично, но кажется движущимся)
def ill_snakes(surf, r, t):
    cx, cy = r.center
    R = min(r.width, r.height)*0.42
    NS = 8
    for i in range(NS):
        base = i*2*math.pi/NS
        for j in range(18):
            rr1 = R*j/18*0.85; rr2 = R*(j+1)/18*0.85
            a1, a2 = base-0.28, base+0.28
            col = (30,30,30) if j % 2 == 0 else (245,245,245)
            pts = []
            for k in range(6):
                a = a1 + (a2-a1)*k/5
                pts.append((cx+rr2*math.cos(a), cy+rr2*math.sin(a)))
            for k in range(6):
                a = a2 - (a2-a1)*k/5
                pts.append((cx+rr1*math.cos(a), cy+rr1*math.sin(a)))
            _c(surf, col, pts)
    colors = [(230,120,90),(100,140,220),(140,210,110)]
    for i in range(NS):
        base = (i+0.5)*2*math.pi/NS
        for j in range(18):
            rr = R*j/18*0.85
            x = cx+rr*math.cos(base); y = cy+rr*math.sin(base)
            pygame.draw.circle(surf, colors[j%3], (int(x), int(y)), 4)

# 18. Окна Эймса
def ill_ames_window(surf, r, t):
    cx, cy = r.center
    ang = t*0.9
    W = min(r.width, r.height)*0.22
    H = W*1.6
    top_w, bot_w = W*0.7, W*1.0
    corners = [(-top_w/2, -H/2), (top_w/2, -H/2),
               (bot_w/2, H/2),  (-bot_w/2, H/2)]
    c, s = math.cos(ang), math.sin(ang)
    rot = [(x*c, y, x*s) for x, y in corners]
    outer, inner = [], []
    for x, y, z in rot:
        f = 3.0/(3.0+z)
        outer.append((cx + x*f, cy + y*f))
        inner.append((cx + x*f*0.78, cy + y*f*0.78))
    _c(surf, DARK, outer)
    _c(surf, WHITE, inner)
    for i in range(4):
        pygame.draw.line(surf, DARK, outer[i], outer[(i+1)%4], 3)
    pygame.draw.line(surf, DARK, outer[0], outer[2], 3)
    pygame.draw.line(surf, DARK, outer[1], outer[3], 3)

# 19. Иллюзия белого цвета
def ill_white(surf, r, t):
    cx, cy = r.center
    n = 6
    sh = int(r.height*0.6/n); sw = int(r.width*0.8)
    ox = cx - sw//2; oy = cy - n*sh//2
    for i in range(n):
        col = DARK if i % 2 == 0 else WHITE
        pygame.draw.rect(surf, col, (ox, oy+i*sh, sw, sh))
    gray = (140, 140, 140)
    bw = int(sw*0.14)
    pygame.draw.rect(surf, gray, (ox + int(sw*0.10), oy, bw, n*sh))
    pygame.draw.rect(surf, gray, (ox + int(sw*0.76), oy, bw, n*sh))

# 20. Эффект Мак-Коллаха
def ill_mccollough(surf, r, t):
    cx, cy = r.center
    hw = r.width//2; hh = r.height//2
    stripe = 12
    # слева: красные горизонтальные
    for i in range(0, r.height, stripe*2):
        y = cy - hh + i
        if y >= cy - hh and y < cy + hh:
            pygame.draw.rect(surf, (200, 30, 30), (cx-hw, y, hw, stripe))
            pygame.draw.rect(surf, BLACK, (cx-hw, y+stripe, hw, stripe))
    # справа: зелёные вертикальные
    for i in range(0, hw, stripe*2):
        x = cx + i
        pygame.draw.rect(surf, (30, 190, 30), (x, cy-hh, stripe, hh*2))
        pygame.draw.rect(surf, BLACK, (x+stripe, cy-hh, stripe, hh*2))

# ---------------- Каталог иллюзий ----------------
ILLUSIONS = [
    {"name": "Иллюзия Мюллера-Лайера",
     "desc": "Две горизонтальные линии одинаковой длины кажутся разными из-за направленных наружу или внутрь стрелок.",
     "render": ill_muller},
    {"name": "Иллюзия Понцо",
     "desc": "Сходящиеся вертикальные линии создают иллюзию глубины: верхняя горизонтальная полоса кажется длиннее нижней, хотя они равны.",
     "render": ill_ponzo},
    {"name": "Иллюзия Эббингауза",
     "desc": "Одинаковые центральные круги кажутся разного размера из-за разного размера окружающих их кругов.",
     "render": ill_ebbinghaus},
    {"name": "Сетка Германа",
     "desc": "На пересечениях белых линий между чёрными квадратами появляются призрачные серые пятна.",
     "render": ill_hermann},
    {"name": "Иллюзия Поггендорфа",
     "desc": "Диагональная линия, перекрытая прямоугольником, кажется разорванной и смещённой, хотя она прямая.",
     "render": ill_poggendorff},
    {"name": "Иллюзия Цёлльнера",
     "desc": "Параллельные прямые с диагональной штриховкой воспринимаются как наклонные.",
     "render": ill_zollner},
    {"name": "Иллюзия Ястрова",
     "desc": "Две одинаковые изогнутые фигуры, одна под другой, кажутся разными по размеру.",
     "render": ill_jastrow},
    {"name": "Иллюзия Вундта",
     "desc": "Две параллельные горизонтальные линии со стрелками-хвостами на концах кажутся изогнутыми.",
     "render": ill_wundt},
    {"name": "Иллюзия Геринга",
     "desc": "Две параллельные прямые на фоне радиального узора кажутся выпуклыми.",
     "render": ill_hering},
    {"name": "Треугольник Канижа",
     "desc": "Мозг достраивает белый треугольник поверх трёх кругов с вырезами, хотя контуров нет.",
     "render": ill_kanizsa},
    {"name": "Комната Эймса (2D)",
     "desc": "Искажённая трапеция воспринимается как прямоугольная комната, и две одинаковые фигуры в ней кажутся разного роста.",
     "render": ill_ames_room},
    {"name": "Иллюзия Оубисона",
     "desc": "Квадрат с немного изогнутыми внутрь сторонами на фоне диагональной штриховки кажется идеальным квадратом.",
     "render": ill_oubison},
    {"name": "Вращающийся силуэт",
     "desc": "Каркасный куб может восприниматься вращающимся в любую сторону — мозг сам выбирает направление.",
     "render": ill_rotating_silhouette},
    {"name": "Движущиеся круги Китаоки",
     "desc": "Кольца с сегментами разных цветов вращаются в разных направлениях, создавая эффект движения.",
     "render": ill_kitaoka},
    {"name": "Эффект Трокслера",
     "desc": "Если зафиксировать взгляд на кресте, объекты на периферии исчезают.",
     "render": ill_troxler},
    {"name": "Иллюзия «Стена кафе»",
     "desc": "Горизонтальные линии между сдвинутыми рядами чёрно-белых кирпичей кажутся наклонными.",
     "render": ill_cafe_wall},
    {"name": "Шевелящиеся змеи",
     "desc": "Статичный узор из спиралей кажется движущимся при перемещении взгляда по картинке.",
     "render": ill_snakes},
    {"name": "Окна Эймса",
     "desc": "Вращающаяся трапеция выглядит как прямоугольное окно, которое покачивается, а не вращается.",
     "render": ill_ames_window},
    {"name": "Иллюзия белого цвета",
     "desc": "Серые полосы на чёрно-белом фоне кажутся разного оттенка в зависимости от расположения полос.",
     "render": ill_white},
    {"name": "Эффект Мак-Коллаха",
     "desc": "Продолжительный просмотр цветных решёток изменяет восприятие чёрно-белых полос — возникает цветной последовательный образ.",
     "render": ill_mccollough},
]

def render_illusion(surf, ill, rect, tm):
    surf.set_clip(rect)
    try:
        ill["render"](surf, rect, tm)
    except Exception as e:
        surf.set_clip(None)
        text(surf, f"Ошибка: {e}", 12, BLACK, center=rect.center)
    surf.set_clip(None)

# ================================================================
#                        UI
# ================================================================

class Button:
    def __init__(self, rect, label, action, color=ACCENT, size=22, fg=WHITE):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.action = action
        self.color = color
        self.size = size
        self.fg = fg
        self.pressed = False

    def handle(self, ev):
        if ev["type"] == "down" and self.rect.collidepoint(ev["pos"]):
            self.pressed = True
        elif ev["type"] == "up":
            was = self.pressed
            self.pressed = False
            if was and self.rect.collidepoint(ev["pos"]):
                self.action()
                return True
        return False

    def draw(self, surf):
        col = tuple(max(0, c-30) for c in self.color) if self.pressed else self.color
        pygame.draw.rect(surf, SHADOW, self.rect.move(0, 4), border_radius=12)
        pygame.draw.rect(surf, col, self.rect, border_radius=12)
        text(surf, self.label, self.size, self.fg, center=self.rect.center, bold=True)

class Screen:
    def __init__(self, app): self.app = app
    def handle(self, ev): pass
    def update(self, dt): pass
    def draw(self, surf): pass

# ---------------- Главное меню ----------------
class MainMenu(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.buttons = [
            Button((60, 620, VW-120, 84), "Начать", self.start, ACCENT, 26),
            Button((60, 720, VW-120, 68), "О приложении", self.about, ACCENT2, 20),
        ]
        self.about_open = False

    def start(self): self.app.push(IllusionList(self.app))
    def about(self): self.about_open = not self.about_open

    def handle(self, ev):
        if self.about_open:
            if ev["type"] == "up":
                self.about_open = False
            return
        for b in self.buttons:
            if b.handle(ev): return

    def draw(self, surf):
        # Декоративная "иллюзия" сверху
        cx, cy = VW//2, 300
        pygame.draw.circle(surf, ACCENT, (cx-50, cy), 70, 4)
        pygame.draw.circle(surf, ACCENT2, (cx+50, cy), 70, 4)
        pygame.draw.circle(surf, DARK, (cx, cy), 5)

        text(surf, "Оптические", 44, DARK, center=(VW//2, 440), bold=True)
        text(surf, "иллюзии", 44, DARK, center=(VW//2, 490), bold=True)
        text(surf, "20 классических обманов зрения", 17, MID,
             center=(VW//2, 550))

        for b in self.buttons:
            b.draw(surf)

        text(surf, "v1.0 · Pygame", 12, MID, center=(VW//2, VH-30))

        if self.about_open:
            ov = pygame.Surface((VW, VH), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 160))
            surf.blit(ov, (0, 0))
            r = pygame.Rect(40, 200, VW-80, 560)
            pygame.draw.rect(surf, CARD, r, border_radius=16)
            pygame.draw.rect(surf, ACCENT, (r.left, r.top, r.width, 64),
                             border_top_left_radius=16, border_top_right_radius=16)
            text(surf, "О приложении", 24, WHITE,
                 center=(r.centerx, r.top+32), bold=True)
            about = ("Коллекция классических оптических иллюзий. "
                     "Каждая иллюстрация нарисована процедурно. "
                     "Коснитесь иллюзии в просмотре, чтобы открыть "
                     "полноэкранный режим.\n\n"
                     "Кнопка «?» показывает описание.\n"
                     "Кнопка «←» — возврат назад.\n"
                     "Системная кнопка «Назад» также работает.")
            text(surf, about, 17, DARK, topleft=(r.left+24, r.top+90),
                 max_w=r.width-48)
            text(surf, "Коснитесь вне окна, чтобы закрыть", 13, MID,
                 center=(r.centerx, r.bottom-30))

# ---------------- Список иллюзий ----------------
class IllusionList(Screen):
    ITEM_H = 88
    GAP    = 10
    TOP    = 120

    def __init__(self, app):
        super().__init__(app)
        self.scroll = 0
        self.max_scroll = max(
            0,
            len(ILLUSIONS)*(self.ITEM_H + self.GAP) - (VH - self.TOP - 40)
        )
        self.drag_start = None
        self.drag_scroll = 0
        self.moved = False
        self.btns = [Button((20, 26, 56, 56), "←", app.pop, MID, 26)]
        self.item_rects = []

    def handle(self, ev):
        for b in self.btns:
            if b.handle(ev): return
        if ev["type"] == "down":
            self.drag_start = ev["pos"]
            self.drag_scroll = self.scroll
            self.moved = False
        elif ev["type"] == "move" and self.drag_start:
            dy = ev["pos"][1] - self.drag_start[1]
            if abs(dy) > 8: self.moved = True
            self.scroll = max(0, min(self.max_scroll, self.drag_scroll - dy))
        elif ev["type"] == "up":
            if not self.moved and self.drag_start:
                for i, rc in enumerate(self.item_rects):
                    if rc.collidepoint(ev["pos"]):
                        self.app.push(IllusionView(self.app, i))
                        break
            self.drag_start = None

    def draw(self, surf):
        pygame.draw.rect(surf, CARD, (0, 0, VW, 100))
        pygame.draw.line(surf, LIGHT, (0, 100), (VW, 100), 2)
        text(surf, "Иллюзии", 28, DARK, center=(VW//2, 54), bold=True)
        for b in self.btns: b.draw(surf)

        self.item_rects = []
        top = self.TOP - self.scroll
        for i, ill in enumerate(ILLUSIONS):
            y = top + i*(self.ITEM_H + self.GAP)
            rc = pygame.Rect(20, y, VW-40, self.ITEM_H)
            self.item_rects.append(rc)
            if rc.bottom < 100 or rc.top > VH: continue
            pygame.draw.rect(surf, SHADOW, rc.move(0, 3), border_radius=14)
            pygame.draw.rect(surf, CARD, rc, border_radius=14)
            pygame.draw.circle(surf, ACCENT, (rc.left+40, rc.centery), 24)
            text(surf, str(i+1), 22, WHITE,
                 center=(rc.left+40, rc.centery), bold=True)
            text(surf, ill["name"], 18, DARK,
                 topleft=(rc.left+82, rc.centery-12), bold=True)

        # Скроллбар
        if self.max_scroll > 0:
            track_h = VH - self.TOP - 40
            thumb_h = max(40, int(track_h*track_h/(track_h+self.max_scroll)))
            thumb_y = self.TOP + int((track_h-thumb_h)*self.scroll/self.max_scroll)
            pygame.draw.rect(surf, LIGHT, (VW-8, self.TOP, 4, track_h),
                             border_radius=2)
            pygame.draw.rect(surf, MID, (VW-8, thumb_y, 4, thumb_h),
                             border_radius=2)

# ---------------- Просмотр иллюзии ----------------
class IllusionView(Screen):
    def __init__(self, app, idx):
        super().__init__(app)
        self.idx = idx
        self.ill = ILLUSIONS[idx]
        self.show_info = False
        self.fullscreen = False
        self.btns = [
            Button((20, 26, 56, 56), "←", app.pop, MID, 26),
            Button((VW-76, 26, 56, 56), "?", self.toggle_info, ACCENT2, 26),
        ]

    def toggle_info(self):
        self.show_info = not self.show_info

    def _ill_rect(self):
        return pygame.Rect(20, 104, VW-40, VH-224)

    def _info_rect(self):
        return pygame.Rect(30, 150, VW-60, VH-300)

    def handle(self, ev):
        if self.fullscreen:
            if ev["type"] == "up":
                self.fullscreen = False
            return

        for b in self.btns:
            if b.handle(ev):
                return

        if ev["type"] == "up":
            if self.show_info:
                if not self._info_rect().collidepoint(ev["pos"]):
                    self.show_info = False
            else:
                if self._ill_rect().collidepoint(ev["pos"]):
                    self.fullscreen = True

    def draw(self, surf):
        if self.fullscreen:
            surf.fill(WHITE)
            render_illusion(surf, self.ill,
                            pygame.Rect(0, 0, VW, VH), self.app.time)
            text(surf, "Коснитесь, чтобы выйти", 14, (200, 200, 200),
                 center=(VW//2, VH-28))
            return

        # Верхняя панель
        pygame.draw.rect(surf, CARD, (0, 0, VW, 100))
        pygame.draw.line(surf, LIGHT, (0, 100), (VW, 100), 2)
        for b in self.btns: b.draw(surf)

        # Название (обрезаем, если длинное)
        name = self.ill["name"]
        f = F(20, True)
        while f.size(name)[0] > VW-170 and len(name) > 4:
            name = name[:-2] + "…"
        text(surf, name, 20, DARK, center=(VW//2, 54), bold=True)

        # Область иллюзии
        ir = self._ill_rect()
        pygame.draw.rect(surf, WHITE, ir, border_radius=12)
        pygame.draw.rect(surf, LIGHT, ir, 2, border_radius=12)
        render_illusion(surf, self.ill, ir.inflate(-24, -24), self.app.time)

        text(surf, "Коснитесь иллюзии для полного экрана",
             13, MID, center=(VW//2, ir.bottom + 36))

        # Модальное окно описания
        if self.show_info:
            ov = pygame.Surface((VW, VH), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 155))
            surf.blit(ov, (0, 0))
            rr = self._info_rect()
            pygame.draw.rect(surf, CARD, rr, border_radius=16)
            pygame.draw.rect(surf, ACCENT,
                             (rr.left, rr.top, rr.width, 62),
                             border_top_left_radius=16,
                             border_top_right_radius=16)
            text(surf, "Описание", 22, WHITE,
                 center=(rr.centerx, rr.top+31), bold=True)
            text(surf, self.ill["desc"], 17, DARK,
                 topleft=(rr.left+24, rr.top+88),
                 max_w=rr.width-48)
            text(surf, "Коснитесь вне окна, чтобы закрыть",
                 13, MID, center=(rr.centerx, rr.bottom-30))

# ================================================================
#                          APP
# ================================================================

class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Оптические иллюзии")
        self.rw, self.rh = self.screen.get_size()
        self.virt = pygame.Surface((VW, VH))
        self.clock = pygame.time.Clock()
        self.running = True
        self.time = 0.0
        self.stack = []
        self._recalc()
        self.use_finger = False

    def _recalc(self):
        self.scale = min(self.rw/VW, self.rh/VH)
        self.nw = int(VW*self.scale); self.nh = int(VH*self.scale)
        self.ox = (self.rw - self.nw)//2
        self.oy = (self.rh - self.nh)//2

    def to_virt(self, p):
        return (int((p[0]-self.ox)/self.scale),
                int((p[1]-self.oy)/self.scale))

    def push(self, s): self.stack.append(s)
    def pop(self):
        if len(self.stack) > 1:
            self.stack.pop()

    def run(self):
        FINGER_DOWN = getattr(pygame, "FINGERDOWN", -1)
        FINGER_UP   = getattr(pygame, "FINGERUP", -1)
        FINGER_MOV  = getattr(pygame, "FINGERMOTION", -1)

        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.time += dt

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.running = False
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    if len(self.stack) > 1:
                        self.pop()
                    else:
                        self.running = False
                elif ev.type == pygame.MOUSEBUTTONDOWN and not self.use_finger:
                    self.stack[-1].handle({"type": "down",
                                           "pos": self.to_virt(ev.pos)})
                elif ev.type == pygame.MOUSEBUTTONUP and not self.use_finger:
                    self.stack[-1].handle({"type": "up",
                                           "pos": self.to_virt(ev.pos)})
                elif ev.type == pygame.MOUSEMOTION and not self.use_finger:
                    self.stack[-1].handle({"type": "move",
                                           "pos": self.to_virt(ev.pos)})
                elif ev.type == FINGER_DOWN:
                    self.use_finger = True
                    p = (int(ev.x*self.rw), int(ev.y*self.rh))
                    self.stack[-1].handle({"type": "down",
                                           "pos": self.to_virt(p)})
                elif ev.type == FINGER_UP:
                    p = (int(ev.x*self.rw), int(ev.y*self.rh))
                    self.stack[-1].handle({"type": "up",
                                           "pos": self.to_virt(p)})
                elif ev.type == FINGER_MOV:
                    p = (int(ev.x*self.rw), int(ev.y*self.rh))
                    self.stack[-1].handle({"type": "move",
                                           "pos": self.to_virt(p)})

            if not self.stack: break
            self.stack[-1].update(dt)
            self.virt.fill(BG)
            self.stack[-1].draw(self.virt)

            self.screen.fill((0, 0, 0))
            scaled = pygame.transform.scale(self.virt, (self.nw, self.nh))
            self.screen.blit(scaled, (self.ox, self.oy))
            pygame.display.flip()

# ================================================================
#                         MAIN
# ================================================================

def main():
    try:
        app = App()
        app.push(MainMenu(app))
        app.run()
    except Exception:
        import traceback; traceback.print_exc()
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()