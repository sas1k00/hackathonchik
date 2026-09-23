"""Сборка презентации Tamyr: py docs/build_deck.py  →  docs/Tamyr_VentureHack2026.pptx
Стиль: светлый фон, королевский синий + чёрный, широкие заглавные заголовки, мотив шестиугольников, синие точки и «схемные» линии.
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

HERE = Path(__file__).parent
IMG = HERE / 'img'
OUT = HERE / 'Tamyr_VentureHack2026.pptx'

BLUE = RGBColor(0x0B, 0x4D, 0xA2)
BLUE_DARK = RGBColor(0x08, 0x2F, 0x66)
BLUE_MID = RGBColor(0x5B, 0x8F, 0xD6)
BLUE_LIGHT = RGBColor(0xB9, 0xCF, 0xEE)
BLUE_PALE = RGBColor(0xEA, 0xF1, 0xFB)
INK = RGBColor(0x11, 0x11, 0x11)
GRAY = RGBColor(0x4A, 0x4F, 0x57)
MUTED = RGBColor(0x7A, 0x80, 0x8A)
LINE = RGBColor(0xD5, 0xDD, 0xE8)
BG = RGBColor(0xF6, 0xF8, 0xFB)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
RED = RGBColor(0xE0, 0x47, 0x3E)
RED_PALE = RGBColor(0xFB, 0xE3, 0xE1)

DISPLAY = 'Arial Black'
BODY = 'Arial Black'
BODY_SCALE = 0.88  # Arial Black шире Calibri — обычный текст чуть мельче, чтобы не вылезал
FOOTER = 'VentureHack 2026  ·  Трек 2 — EduTech'

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
SW, SH = 13.333, 7.5


# ---------- фон «тоннель» для титула ----------
def make_tunnel(path, w=2000, h=1125):
    img = Image.new('RGB', (w, h), (246, 248, 251))
    d = ImageDraw.Draw(img)
    for y in range(h):  # мягкий вертикальный градиент
        c = int(246 + 8 * y / h)
        d.line([(0, y), (w, y)], fill=(c, min(255, c + 2), 255))
    vx, vy = int(w * 0.66), int(h * 0.47)

    def hexpts(r):
        return [(vx + r * math.cos(math.radians(a)), vy + r * 0.72 * math.sin(math.radians(a))) for a in range(0, 360, 60)]
    radii = [60 * 1.33 ** k for k in range(14)]
    for i, r in enumerate(radii):
        if i % 2 == 0 and i + 1 < len(radii):  # чередующиеся панели
            outer, inner = hexpts(radii[i + 1]), hexpts(r)
            for j in range(6):
                poly = [inner[j], inner[(j + 1) % 6], outer[(j + 1) % 6], outer[j]]
                shade = 238 + (j % 3) * 4
                d.polygon(poly, fill=(shade, shade + 3, 252))
    for r in radii:
        d.polygon(hexpts(r), outline=(214, 222, 234), width=3)
    for p in hexpts(radii[-1]):
        d.line([(vx, vy), p], fill=(222, 229, 240), width=3)
    # «свет» в центре тоннеля
    glow = Image.new('L', (w, h), 0)
    gd = ImageDraw.Draw(glow)
    for k in range(40, 0, -1):
        gd.ellipse([vx - k * 12, vy - k * 8, vx + k * 12, vy + k * 8], fill=int(255 * (1 - k / 40) ** 0.6))
    img = Image.composite(Image.new('RGB', (w, h), (255, 255, 255)), img, glow)
    img.save(path)


TUNNEL = HERE / 'img' / '_tunnel.png'
make_tunnel(TUNNEL)


# ---------- примитивы ----------
def bg(slide, color):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = color


def text(slide, x, y, w, h, runs, size=16, color=INK, font=BODY, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, spacing=None, italic=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    paras = runs if isinstance(runs, list) else [runs]
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = align
        if spacing:
            para.space_after = Pt(spacing)
        parts = p if isinstance(p, list) else [(p, {})]
        for t, o in parts:
            r = para.add_run()
            r.text = t
            r.font.name = o.get('font', font)
            sz = o.get('size', size)
            r.font.size = Pt(sz if sz >= 22 else round(sz * BODY_SCALE))
            r.font.bold = False
            r.font.italic = o.get('italic', italic)
            r.font.color.rgb = o.get('color', color)
    return tb


def shape(slide, kind, x, y, w, h, fill=None, line=None, lw=2, dash=False):
    s = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(lw)
        if dash:
            s.line.dash_style = 4
    s.shadow.inherit = False
    tf = s.text_frame
    tf.margin_left = tf.margin_right = Inches(0.08)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    return s


def hexagon(slide, x, y, w, fill=None, line=None, lw=2, h=None, dash=False):
    """Шестиугольник с плоским верхом; без h — правильный."""
    h = h if h is not None else w * 0.866
    s = shape(slide, MSO_SHAPE.HEXAGON, x, y, w, h, fill, line, lw, dash)
    s.adjustments[0] = min(0.5, (w / 4) / min(w, h))
    return s


def label(s, t, size=14, color=WHITE, bold=True, font=BODY, align=PP_ALIGN.CENTER):
    tf = s.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for i, ln in enumerate(t.split('\n')):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = ln
        r.font.name = font
        r.font.size = Pt(size if size >= 22 else round(size * BODY_SCALE))
        r.font.bold = False
        r.font.color.rgb = color


def line(slide, x1, y1, x2, y2, color=BLUE_LIGHT, width=1.5, arrow=False, dash=False):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    if dash:
        c.line.dash_style = 4
    if arrow:
        ln = c.line._get_or_add_ln()
        ln.append(ln.makeelement(qn('a:tailEnd'), {'type': 'triangle', 'w': 'med', 'len': 'med'}))
    return c


def dot(slide, x, y, d=0.16, color=BLUE):
    return shape(slide, MSO_SHAPE.OVAL, x - d / 2, y - d / 2, d, d, color)


def circuit(slide, x, y, segments, color=BLUE_LIGHT, dotcolor=BLUE):
    """«Схемная» ломаная с кружками на концах."""
    px, py = x, y
    for dx, dy in segments:
        line(slide, px, py, px + dx, py + dy, color, 1.25)
        px, py = px + dx, py + dy
    dot(slide, x, y, 0.09, dotcolor)
    dot(slide, px, py, 0.09, dotcolor)


def root_glyph(slide, x, y, s, color=WHITE, width=None):
    cx = x + s / 2
    segs = [((cx, y), (cx, y + s * 0.45)), ((cx, y + s * 0.45), (x + s * 0.12, y + s)),
            ((cx, y + s * 0.45), (x + s * 0.88, y + s)), ((cx, y + s * 0.45), (cx, y + s)),
            ((cx, y + s * 0.2), (x + s * 0.2, y)), ((cx, y + s * 0.2), (x + s * 0.8, y))]
    for a, b in segs:
        line(slide, a[0], a[1], b[0], b[1], color, width or max(1.5, s * 5))


def brand(slide, right=True):
    x = SW - 2.05 if right else 0.6
    hexagon(slide, x, 0.42, 0.42, BLUE)
    root_glyph(slide, x + 0.11, 0.48, 0.2, WHITE, 1.25)
    text(slide, x + 0.52, 0.44, 1.5, 0.4, 'Tamyr', size=16, bold=True, color=BLUE, anchor=MSO_ANCHOR.MIDDLE)


def footer(slide):
    text(slide, SW - 5.1, SH - 0.55, 4.5, 0.3, FOOTER, size=11, bold=True, color=MUTED, align=PP_ALIGN.RIGHT)


def heading(slide, big, sub, x=0.7, y=0.95, w=11.9, big_size=44, sub_size=22):
    text(slide, x, y, w, 0.85, big, size=big_size, font=DISPLAY, color=BLUE)
    text(slide, x, y + 0.82, w, 0.9, sub, size=sub_size, font=DISPLAY, color=INK)


def button(slide, x, y, w, t, h=0.5):
    b = shape(slide, MSO_SHAPE.RECTANGLE, x, y, w, h, BLUE)
    label(b, t, size=14, color=WHITE)
    return b


def picture(slide, path, x, y, w, crop_bottom=0.0):
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(w))
    if crop_bottom:
        h = pic.height
        pic.crop_bottom = crop_bottom
        pic.height = int(h * (1 - crop_bottom))
    pic.line.color.rgb = LINE
    pic.line.width = Pt(1)
    return pic


def backdrop_hex(slide, cx, cy, w, color=BLUE_PALE):
    """Большой бледный шестиугольник-подложка (может выходить за край слайда)."""
    return hexagon(slide, cx - w / 2, cy - w * 0.866 / 2, w, color)


def dots_cluster(slide, pts, color=BLUE):
    for (x, y, d) in pts:
        dot(slide, x, y, d, color)


def bullets(tb, indent=0.22):
    for p in tb.text_frame.paragraphs:
        pPr = p._p.get_or_add_pPr()
        pPr.set('marL', str(Inches(indent)))
        pPr.set('indent', str(-Inches(indent)))
        pPr.append(pPr.makeelement(qn('a:buChar'), {'char': '•'}))


def notes(slide, t):
    slide.notes_slide.notes_text_frame.text = t


# =====================================================================
# 1. Титул
# =====================================================================
s = prs.slides.add_slide(BLANK)
s.shapes.add_picture(str(TUNNEL), 0, 0, width=prs.slide_width, height=prs.slide_height)
dots_cluster(s, [(1.55, 0.3, 0.2), (0.55, 1.05, 0.2), (3.55, 1.05, 0.2), (4.35, 0.55, 0.2), (4.35, 1.55, 0.2)])
brand(s)
HW = 1.75
HH = HW * 0.866
cx, cy = 2.95, 4.05
cells = [((0, -1), 'Кв.\nуравнения', BLUE, WHITE), ((-1, -0.5), 'Лин.\nуравнения', BLUE_MID, WHITE), ((1, -0.5), 'Корни', BLUE, WHITE),
         ((0, 0), 'Дроби', RED, WHITE), ((-1, 0.5), 'Проценты', BLUE_LIGHT, BLUE_DARK), ((1, 0.5), 'Степени', BLUE, WHITE),
         ((0, 1), 'Арифметика', BLUE_LIGHT, BLUE_DARK)]
shape(s, MSO_SHAPE.OVAL, cx - 2.45, cy + 1.95, 4.9, 0.75, BLUE_DARK)
shape(s, MSO_SHAPE.OVAL, cx - 2.3, cy + 1.88, 4.6, 0.6, RGBColor(0x1A, 0x1F, 0x2A), BLUE_MID, 2.5)
for (i, j), t, f, fc in cells:
    h = hexagon(s, cx + i * 0.75 * HW - HW / 2, cy + j * HH - HH / 2, HW, f, WHITE, 3)
    label(h, t, size=11 if len(t) > 9 else 14, color=fc)
tag = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, cx - 0.62, cy + 0.26, 1.24, 0.3, WHITE)
tag.adjustments[0] = 0.5
label(tag, 'КОРЕНЬ', size=10, color=RED)
circuit(s, 0.35, 6.95, [(0.6, 0), (0.3, -0.25), (0.7, 0)])
circuit(s, 8.6, 6.55, [(0.8, 0), (0.3, -0.3), (1.1, 0)])
dots_cluster(s, [(10.95, 5.75, 0.1), (11.55, 6.05, 0.1), (12.3, 6.15, 0.1), (11.1, 6.45, 0.1), (12.7, 5.85, 0.1)])
text(s, 6.45, 1.95, 6.5, 1.2, 'TAMYR', size=66, font=DISPLAY, color=BLUE)
text(s, 6.5, 3.05, 6.5, 0.6, 'НАХОДИМ КОРЕНЬ ОШИБКИ', size=26, font=DISPLAY, color=INK)
text(s, 6.5, 3.9, 6.2, 0.4, 'Адаптивная диагностика по математике для ЕНТ', size=17, bold=True, color=BLUE)
text(s, 6.5, 4.35, 6.1, 1.0, 'За один тест показывает базовую тему, из-за которой «сыпятся» все следующие. Тамыр (каз.) — корень.', size=16, color=GRAY)
button(s, 6.5, 5.45, 2.9, 'Трек 2 · EduTech')
text(s, SW - 5.1, SH - 0.55, 4.5, 0.3, 'VentureHack 2026', size=12, bold=True, color=MUTED, align=PP_ALIGN.RIGHT)
notes(s, 'Tamyr — по-казахски «корень». Мы в треке EduTech. Мы находим не ошибку, а её причину.')

# =====================================================================
# 2. Проблема
# =====================================================================
s = prs.slides.add_slide(BLANK)
bg(s, WHITE)
backdrop_hex(s, 10.6, 3.95, 7.4)
brand(s, right=False)
heading(s, 'ПРОБЛЕМА', 'УЧЕНИК ПОВТОРЯЕТ\nНЕ ТУ ТЕМУ', w=6.4)
text(s, 0.7, 3.25, 6.0, 3.4, [
    [('Пример: ', {'bold': True, 'color': BLUE}), ('ученица готовится к ЕНТ и ошибается в квадратных уравнениях.', {'bold': True})],
    'Пробник советует: «Повторите квадратные уравнения». Она повторяет, а ошибки остаются.',
    [('Настоящая причина лежит на три темы ниже: ', {}), ('она неверно складывает дроби', {'bold': True, 'color': RED}), (' — это материал 6 класса.', {})],
    [('Тест показывает симптом, но не диагноз.', {'bold': True, 'color': BLUE})],
], size=17, color=GRAY, spacing=12)
chain = [('Квадратные уравнения', 'ошибка видна здесь', WHITE, BLUE, BLUE),
         ('Линейные уравнения', 'ошибка тянется отсюда', WHITE, BLUE, BLUE),
         ('Действия с дробями', 'корень проблемы', RED, RED, WHITE)]
for i, (t, sub, f, l, fc) in enumerate(chain):
    y = 1.75 + i * 1.6
    h = hexagon(s, 8.2, y, 4.6, f, l, 2.5, h=0.95)
    label(h, t, size=19, color=fc)
    text(s, 8.2, y + 1.0, 4.6, 0.3, sub, size=12, color=GRAY, align=PP_ALIGN.CENTER, italic=True)
    if i < 2:
        line(s, 10.5, y + 1.3, 10.5, y + 1.58, RED, 2.5, arrow=True)
footer(s)
notes(s, 'Пример проблемы. Ученица повторяет квадратные уравнения, но корень — в дробях 6 класса.')

# =====================================================================
# 3. Масштаб и причины
# =====================================================================
s = prs.slides.add_slide(BLANK)
bg(s, BG)
brand(s)
heading(s, 'МАСШТАБ', 'ПРОБЛЕМА МАССОВАЯ, А ТЕСТ ЛЕЧИТ СИМПТОМ')
stats3 = [('50%', 'школьников Казахстана\nдостигли мин. уровня\nпо математике (ОЭСР — 69%)', 'PISA 2022'),
          ('216 тыс.', 'абитуриентов ЕНТ\nв 2025 году', 'НЦТ / Вечерняя Астана'),
          ('64/140', 'средний балл ЕНТ-2025\nпо пяти предметам', 'Вечерняя Астана, 02.06.2025')]
for i, (n, l, src) in enumerate(stats3):
    y = 2.55 + i * 1.3
    h = hexagon(s, 0.6, y, 2.45, WHITE, BLUE, 3, h=1.1)
    label(h, n, size=22, font=DISPLAY, color=BLUE)
    text(s, 3.2, y + 0.05, 3.1, 0.8, l, size=14, color=INK)
    text(s, 3.2, y + 0.82, 3.1, 0.25, src, size=10, color=MUTED)
reasons = [('Математика кумулятивна', 'Пробел в базовой теме всплывает позже — в теме, которая на ней держится.'),
           ('Тест измеряет балл', 'Пробник говорит, где ошибка произошла, но не почему. Выбранный неверный вариант не анализируется.'),
           ('У учителя нет времени', '25–30 учеников в классе: проверить каждого по всем темам 5–9 классов невозможно.')]
shape(s, MSO_SHAPE.RECTANGLE, 6.55, 2.5, 6.05, 3.85, WHITE, LINE, 1)
for i, (h_, b) in enumerate(reasons):
    y = 2.72 + i * 1.2
    hx = hexagon(s, 6.8, y, 0.62, BLUE, WHITE, 2)
    label(hx, str(i + 1), size=14, font=DISPLAY)
    text(s, 7.6, y - 0.02, 4.8, 0.4, h_, size=17, bold=True, color=BLUE)
    text(s, 7.6, y + 0.36, 4.8, 0.75, b, size=13, color=GRAY)
text(s, 0.7, 6.55, 11.9, 0.5, [[('Место для вашей цифры из опроса: ', {'bold': True, 'color': RED}),
                              ('«__% учеников не понимают, почему ошиблись в пробнике» (n = __). Заполните по docs/validation-plan.md или удалите строку.', {'color': GRAY})]], size=12)
notes(s, 'Цифры проверены по первоисточникам (README → «Источники»): OECD PISA 2022 Country Note: Kazakhstan; ЕНТ-2025 — Вечерняя Астана, 02.06.2025. Если провели опрос, назовите свою цифру; если нет, удалите нижнюю строку.')

# =====================================================================
# 4. Решение
# =====================================================================
s = prs.slides.add_slide(BLANK)
bg(s, WHITE)
backdrop_hex(s, -0.9, 7.2, 4.2)
brand(s)
heading(s, 'РЕШЕНИЕ', 'НАЙТИ КОРЕНЬ → ПОКАЗАТЬ → ПОЧИНИТЬ')
steps = [('Адаптивная диагностика', 'Начинаем со сложной темы и спускаемся по графу из 17 тем только там, где есть ошибки. Без пробелов — около 10 вопросов.'),
         ('Карта знаний', 'Корневой пробел, цепочки «ошибка в X → корень в Y» и ошибки мышления по выбранным неверным ответам.'),
         ('План снизу вверх', 'Правило, пример, разбор своей ошибки и 2 новые проверочные задачи. Следующая тема — после корня.'),
         ('Панель учителя', 'Корни всего класса, частые ошибки, готовые мини-группы, тепловая карта и CSV.')]
for i, (h_, b) in enumerate(steps):
    x = 0.9 + i * 3.05
    if i < 3:
        line(s, x + 1.05, 3.02, x + 3.0, 3.02, BLUE_LIGHT, 2, dash=True)
    hx = hexagon(s, x, 2.55, 1.05, BLUE if i < 3 else INK, WHITE, 3)
    label(hx, str(i + 1) if i < 3 else '+', size=22, font=DISPLAY)
    text(s, x, 3.75, 2.75, 0.8, h_, size=19, bold=True, color=BLUE if i < 3 else INK)
    text(s, x, 4.55, 2.75, 1.9, b, size=15, color=GRAY)
button(s, 3.9, 6.35, 8.4, 'Работает в браузере на любом телефоне — без установки, регистрации и сервера')
footer(s)

# =====================================================================
# 5. Алгоритм
# =====================================================================
s = prs.slides.add_slide(BLANK)
bg(s, WHITE)
brand(s)
heading(s, 'АЛГОРИТМ', 'КАК TAMYR ИЩЕТ КОРЕНЬ')
NW_, NH_ = 1.75, 0.62
nodes = {'quad': (2.55, 2.55, 'Кв. уравнения', RED_PALE, RED, INK), 'fact': (0.6, 3.75, 'Разложение', BLUE, BLUE, WHITE),
         'lin': (2.55, 3.75, 'Лин. уравнения', RED_PALE, RED, INK), 'root': (4.5, 3.75, 'Корни', BLUE, BLUE, WHITE),
         'expr': (1.55, 4.95, 'Выражения', BLUE, BLUE, WHITE), 'frac': (3.55, 4.95, 'Дроби', RED, RED, WHITE),
         'arith': (3.55, 6.15, 'Арифметика', BLUE_LIGHT, BLUE_LIGHT, BLUE_DARK)}
for a, b in [('quad', 'fact'), ('quad', 'lin'), ('quad', 'root'), ('lin', 'expr'), ('lin', 'frac'), ('frac', 'arith')]:
    bad = (a, b) in [('quad', 'lin'), ('lin', 'frac')]
    line(s, nodes[a][0] + NW_ / 2, nodes[a][1] + NH_, nodes[b][0] + NW_ / 2, nodes[b][1], RED if bad else LINE, 2.5 if bad else 1.5, arrow=True)
for k, (x, y, t, f, l, fc) in nodes.items():
    h = hexagon(s, x, y, NW_, f, l, 2, h=NH_)
    label(h, t, size=11, color=fc)
text(s, 0.6, 6.95, 6.0, 0.3, 'Синий — освоено, красный — пробел, насыщенный красный — корень', size=11, color=MUTED, italic=True)
rules = [('Решил тему без ошибок', 'всё, на чём она держится, засчитано без вопросов', BLUE),
         ('Ошибся дважды', 'спускаемся к непроверенным пререквизитам', RED),
         ('Неверный вариант с меткой', 'сначала проверяем «домашнюю» тему этой ошибки', BLUE_MID),
         ('Корень', '= пробел, под которым пробелов нет', INK)]
for i, (h_, b, c) in enumerate(rules):
    y = 2.6 + i * 0.88
    hexagon(s, 6.9, y + 0.05, 0.42, c)
    text(s, 7.5, y, 5.3, 0.4, h_, size=17, bold=True, color=INK)
    text(s, 7.5, y + 0.38, 5.3, 0.4, b, size=14, color=GRAY)
shape(s, MSO_SHAPE.RECTANGLE, 6.9, 6.2, 5.8, 0.95, BLUE_PALE)
text(s, 7.15, 6.28, 5.4, 0.8, [[('1/2 + 1/3 = 2/5', {'bold': True, 'color': RED, 'size': 17}), ('  →  «складывает числители и знаменатели»', {'color': INK, 'bold': True})],
                              [('Такой ответ сразу отправляет проверку в тему «Дроби».', {'color': GRAY})]], size=13)
notes(s, 'Объясните правила движка. Ключевая особенность: неверный вариант ответа говорит, какая именно это ошибка.')

# =====================================================================
# 6. Демо
# =====================================================================
s = prs.slides.add_slide(BLANK)
bg(s, WHITE)
backdrop_hex(s, 4.6, 4.4, 8.6, BLUE_LIGHT)
brand(s)
heading(s, 'ДЕМО', 'КАРТА ЗНАНИЙ УЧЕНИКА')
picture(s, IMG / 'demo.png', 0.7, 2.55, 7.3, crop_bottom=0.2)
pts = [('14 вопросов', 'по теме «Квадратные уравнения» и всем её основам'),
       ('Корень — «Дроби»', 'хотя ошибки видны в квадратных и линейных уравнениях'),
       ('Ошибки мышления', 'по выбранным вариантам, с правилом исправления'),
       ('План', '«Разобрать» → урок → 2 новые задачи → следующая тема')]
for i, (h_, b) in enumerate(pts):
    y = 2.5 + i * 0.98
    hexagon(s, 8.55, y + 0.06, 0.3, BLUE)
    text(s, 9.0, y, 3.9, 0.4, h_, size=18, bold=True, color=BLUE)
    text(s, 9.0, y + 0.38, 3.8, 0.55, b, size=13, color=GRAY)
button(s, 9.0, 6.55, 3.1, 'Открыть: index.html#demo', h=0.45)
notes(s, 'Живое демо: #setup → «Квадратные уравнения» → отвечать как ученик с пробелом в дробях. Запасной вариант: #demo.')

# =====================================================================
# 7. Учитель
# =====================================================================
s = prs.slides.add_slide(BLANK)
bg(s, WHITE)
backdrop_hex(s, 9.2, 4.5, 8.6, BLUE_LIGHT)
brand(s, right=False)
heading(s, 'УЧИТЕЛЮ', 'КОРНИ ВСЕГО КЛАССА', w=5.2)
picture(s, IMG / 'teacher.png', 5.35, 1.35, 7.3, crop_bottom=0.12)
pts = [('Корневые пробелы класса', 'какие базовые темы тянут класс вниз'),
       ('Мини-группы', 'кого с кем посадить на 15-минутный разбор'),
       ('Тепловая карта и CSV', 'ученик × тема, выгрузка в Excel'),
       ('Без сервера', 'ученик передаёт результат кодом')]
for i, (h_, b) in enumerate(pts):
    y = 2.9 + i * 0.9
    hexagon(s, 0.7, y + 0.06, 0.3, BLUE)
    text(s, 1.15, y, 3.9, 0.4, h_, size=18, bold=True, color=BLUE)
    text(s, 1.15, y + 0.38, 3.9, 0.45, b, size=13, color=GRAY)
text(s, 5.35, 6.95, 7.3, 0.3, 'Демо-класс: 24 виртуальных ученика (симуляция, не реальные данные).', size=11, color=GRAY, italic=True)

# =====================================================================
# 8. Конкуренты
# =====================================================================
s = prs.slides.add_slide(BLANK)
bg(s, BG)
brand(s)
heading(s, 'КОНКУРЕНТЫ', 'ИДЕЯ НЕ НОВАЯ — НОВОЕ В СВЯЗКЕ')
rows = [('ALEKS', 'McGraw Hill', 'Адаптивная оценка по «пространству знаний». Платная, программы США.', 'Программа и формат ЕНТ, бесплатно для ученика, офлайн без регистрации'),
        ('Eedi', 'Великобритания', 'Диагностические вопросы: неверный вариант указывает на ошибку мышления.', 'Метка ошибки сразу ведёт в её домашнюю тему и дальше вниз, к корню'),
        ('Khan Academy', 'США', 'Бесплатные курсы и система освоения по темам.', 'Не курс, а 10–20 минут диагностики: с чего начать'),
        ('Пробники ЕНТ', 'Казахстан', 'Балл и разбор по темам, где произошла ошибка.', 'Причина, а не балл; учителю — корни класса и группы')]
text(s, 3.35, 2.45, 4.3, 0.3, 'ЧТО ДЕЛАЕТ', size=11, color=MUTED, bold=True)
text(s, 8.0, 2.45, 4.6, 0.3, 'ЧЕМ ОТЛИЧАЕТСЯ TAMYR', size=11, color=BLUE, bold=True)
for i, (n, org, what, diff) in enumerate(rows):
    y = 2.8 + i * 0.88
    shape(s, MSO_SHAPE.RECTANGLE, 0.7, y, 11.9, 0.78, WHITE, LINE, 1)
    hexagon(s, 0.9, y + 0.24, 0.34, BLUE)
    text(s, 1.4, y + 0.1, 1.9, 0.35, n, size=16, bold=True)
    text(s, 1.4, y + 0.44, 1.9, 0.3, org, size=11, color=MUTED)
    text(s, 3.35, y + 0.06, 4.4, 0.66, what, size=13, color=GRAY, anchor=MSO_ANCHOR.MIDDLE)
    shape(s, MSO_SHAPE.RECTANGLE, 7.85, y, 4.75, 0.78, BLUE_PALE)
    text(s, 8.0, y + 0.06, 4.5, 0.66, diff, size=13, color=BLUE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
button(s, 0.7, 6.45, 11.9, 'Неверный вариант → домашняя тема ошибки → проверка корня  ·  под ЕНТ, офлайн, с панелью учителя', h=0.5)
notes(s, 'Не утверждайте, что идея уникальна: жюри может знать ALEKS и Eedi. Перед защитой проверьте актуальные описания конкурентов на их сайтах.')

# =====================================================================
# 9. Валидация
# =====================================================================
s = prs.slides.add_slide(BLANK)
bg(s, WHITE)
brand(s)
heading(s, 'ВАЛИДАЦИЯ', 'ЧТО УЖЕ ПРОВЕРЕНО')
stats = [('90%', 'настоящих корней найдено\n(полнота)'), ('85%', 'найденных корней верны\n(точность)'),
         ('7/18', 'тем спецификации ЕНТ\nпокрыто (алгебра)'), ('20/20', 'юнит-тестов\nпроходят')]
for i, (n, l) in enumerate(stats):
    x = 0.85 + i * 3.05
    h = hexagon(s, x, 2.45, 2.45, WHITE, BLUE, 3)
    label(h, n, size=28, font=DISPLAY, color=BLUE)
    text(s, x - 0.15, 4.65, 2.75, 0.7, l, size=13, color=GRAY, align=PP_ALIGN.CENTER)
text(s, 0.7, 5.45, 11.9, 0.55, 'Полнота и точность — контрольная симуляция: 1000 новых виртуальных учеников, не использованных при доработке (было 79% и 72% до правила «перевес в 2»). Модель ученика наша, поэтому это оценка сверху. Покрытие — сверка 17 тем с официальной спецификацией НЦТ (с 2026 г.).',
     size=12, color=MUTED)
shape(s, MSO_SHAPE.RECTANGLE, 0.7, 6.1, 11.9, 0.85, BLUE_PALE, BLUE, 1.5, dash=True)
text(s, 0.95, 6.18, 11.4, 0.7, [[('Проверка на людях — заполните реальными данными: ', {'bold': True, 'color': BLUE}),
                               ('опрос учеников (n = __), интервью с учителями (__ чел.), мини-пилот: совпадение корня с мнением учителя __ из __. Шаблоны: docs/validation-plan.md', {'color': INK})]], size=13)
notes(s, 'Говорите честно: это симуляция. Затем назовите то, что проверили на людях. Если ничего не успели, скажите, что пилот запланирован, и удалите пустые поля.')

# =====================================================================
# 10. Рынок и внедрение
# =====================================================================
s = prs.slides.add_slide(BLANK)
bg(s, BG)
brand(s)
heading(s, 'РЫНОК', 'КОМУ, СКОЛЬКО СТОИТ, КАК ЗАПУСТИТЬ')
cols = [('Аудитория', ['216 тыс. абитуриентов ЕНТ-2025', '≈184 тыс. сдают обязательную мат. грамотность (наша оценка: без творческих специальностей)', '72% сдают ЕНТ на казахском → казахская версия — шаг №1']),
        ('Затраты', ['Хостинг: 0 ₸ (GitHub Pages)', 'Нет серверов и персональных данных', 'Основное: время учителей на проверку заданий и перевод']),
        ('Деньги (гипотезы)', ['Ученик: диагностика бесплатно, платные банки тем', 'Учебные центры: входная диагностика и панель по подписке', 'Школы: бесплатно для учителя ради охвата'])]
for i, (h_, items) in enumerate(cols):
    x = 0.7 + i * 4.1
    shape(s, MSO_SHAPE.RECTANGLE, x, 3.0, 3.8, 3.75, WHITE, LINE, 1)
    hx = hexagon(s, x + 0.3, 2.62, 0.8, BLUE, WHITE, 3)
    if i == 0:
        root_glyph(s, x + 0.53, 2.79, 0.34, WHITE, 1.5)
    else:
        label(hx, ['', '₸', '✓'][i], size=22)
    text(s, x + 0.3, 3.6, 3.2, 0.45, h_, size=19, bold=True, color=BLUE)
    tb = text(s, x + 0.3, 4.15, 3.25, 2.5, items, size=14, color=GRAY, spacing=8)
    bullets(tb)
text(s, 0.7, 6.9, 7.0, 0.3, 'Источники: НЦТ (формат ЕНТ); Вечерняя Астана, 02.06.2025', size=10, color=MUTED)
footer(s)
notes(s, 'Цены — гипотезы, их надо проверить на интервью (docs/validation-plan.md, вопрос 5 для учителей). 184 тыс. — оценка: 216 тыс. минус около 15% творческих специальностей.')

# =====================================================================
# 11. Дорожная карта и команда
# =====================================================================
s = prs.slides.add_slide(BLANK)
s.shapes.add_picture(str(TUNNEL), 0, 0, width=prs.slide_width, height=prs.slide_height)
brand(s)
dots_cluster(s, [(0.55, 0.45, 0.2), (1.35, 0.9, 0.16), (2.3, 0.45, 0.2)])
heading(s, 'ДАЛЬШЕ', 'ОТ ПРОТОТИПА К КЛАССУ', y=1.25)
road = [('Сейчас', 'MVP: 17 тем, 102 задания, 43 ошибки мышления, панель учителя'), ('1 месяц', 'Казахская версия, пилот в 2–3 классах'),
        ('3 месяца', 'Проверка заданий учителями, 10+ вопросов на тему'), ('6 месяцев', 'Тригонометрия, логарифмы, геометрия по спецификации ЕНТ')]
line(s, 1.2, 3.85, 10.4, 3.85, BLUE_LIGHT, 3)
for i, (h_, b) in enumerate(road):
    x = 0.8 + i * 3.1
    hx = hexagon(s, x, 3.42, 0.95, BLUE if i == 0 else WHITE, BLUE, 3)
    label(hx, str(i + 1), size=18, font=DISPLAY, color=WHITE if i == 0 else BLUE)
    text(s, x, 4.55, 2.8, 0.4, h_, size=18, bold=True, color=BLUE)
    text(s, x, 4.98, 2.75, 1.0, b, size=14, color=GRAY)
text(s, 0.8, 6.15, 8.5, 0.4, 'Команда: Bolatbay Yersultan · Zharkynuly Eren · Kydyrkhan Olzhas', size=16, bold=True, color=INK)
text(s, 0.8, 6.6, 8.5, 0.35, 'GitHub: github.com/sas1k00/hackathonchik   ·   Демо: sas1k00.github.io/hackathonchik', size=13, color=GRAY)
button(s, 10.15, 6.25, 2.5, 'Спасибо!')

prs.save(OUT)
print('saved', OUT)
