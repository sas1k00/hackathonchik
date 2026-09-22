"""Сборка презентации Tamyr: py docs/build_deck.py  →  docs/Tamyr_VentureHack2026.pptx"""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

HERE = Path(__file__).parent
IMG = HERE / 'img'
OUT = HERE / 'Tamyr_VentureHack2026.pptx'

DARK = RGBColor(0x14, 0x2B, 0x25)
GREEN = RGBColor(0x1F, 0x6F, 0x5C)
GREEN_SOFT = RGBColor(0xDC, 0xEF, 0xE8)
OK = RGBColor(0x2E, 0x8B, 0x57)
RED = RGBColor(0xD9, 0x53, 0x4F)
RED_SOFT = RGBColor(0xF8, 0xD7, 0xD5)
AMBER = RGBColor(0xE9, 0xA2, 0x3B)
AMBER_SOFT = RGBColor(0xFB, 0xE8, 0xC8)
INK = RGBColor(0x1D, 0x1F, 0x1C)
INK2 = RGBColor(0x5B, 0x5F, 0x58)
LIGHT = RGBColor(0xF3, 0xF5, 0xF2)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MINT = RGBColor(0x9F, 0xD9, 0xC4)

HEAD = 'Cambria'
BODY = 'Calibri'

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def bg(slide, color):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = color


def text(slide, x, y, w, h, runs, size=16, color=INK, font=BODY, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, spacing=None, italic=False):
    """runs: str | list of paragraphs; paragraph = str | list of (text, {opts})"""
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
            r.font.size = Pt(o.get('size', size))
            r.font.bold = o.get('bold', bold)
            r.font.italic = o.get('italic', italic)
            r.font.color.rgb = o.get('color', color)
    return tb


def box(slide, x, y, w, h, fill, line=None, radius=0.12, shape=MSO_SHAPE.ROUNDED_RECTANGLE, dash=False):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(2)
        if dash:
            s.line.dash_style = 4  # dash
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    s.shadow.inherit = False
    s.text_frame.margin_left = s.text_frame.margin_right = Inches(0.12)
    return s


def label(shape, t, size=14, color=INK, bold=True, align=PP_ALIGN.CENTER):
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = t
    r.font.name = BODY
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color


def arrow(slide, x1, y1, x2, y2, color=INK2, width=2, dash=False):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    if dash:
        c.line.dash_style = 4
    ln = c.line._get_or_add_ln()
    tail = ln.makeelement(qn('a:tailEnd'), {'type': 'triangle', 'w': 'med', 'len': 'med'})
    ln.append(tail)
    return c


def title(slide, t, kicker=None, color=INK, kcolor=GREEN):
    if kicker:
        text(slide, 0.7, 0.55, 11.9, 0.35, kicker.upper(), size=12, color=kcolor, bold=True)
    text(slide, 0.7, 0.9, 11.9, 0.9, t, size=36, color=color, font=HEAD, bold=True)


def picture(slide, path, x, y, w, crop_bottom=0.0):
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(w))
    if crop_bottom:
        h = pic.height
        pic.crop_bottom = crop_bottom
        pic.height = int(h * (1 - crop_bottom))
    pic.line.color.rgb = RGBColor(0xDD, 0xDD, 0xD5)
    pic.line.width = Pt(1)
    return pic


def root_icon(slide, x, y, s, color):
    """Мотив «корень»: стебель и ветви корня из линий."""
    cx = x + s / 2
    pts = [((cx, y), (cx, y + s * 0.45)), ((cx, y + s * 0.45), (x + s * 0.12, y + s)),
           ((cx, y + s * 0.45), (x + s * 0.88, y + s)), ((cx, y + s * 0.45), (cx, y + s)),
           ((cx, y + s * 0.2), (x + s * 0.2, y)), ((cx, y + s * 0.2), (x + s * 0.8, y))]
    for (a, b) in pts:
        c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(a[0]), Inches(a[1]), Inches(b[0]), Inches(b[1]))
        c.line.color.rgb = color
        c.line.width = Pt(max(2, s * 5))


# ---------- 1. Титул ----------
s = prs.slides.add_slide(BLANK)
bg(s, DARK)
root_icon(s, 0.75, 0.8, 0.9, MINT)
text(s, 0.7, 2.2, 11, 1.4, 'Tamyr', size=80, color=WHITE, font=HEAD, bold=True)
text(s, 0.7, 3.55, 11, 1.0, 'Находим не ошибку, а её корень', size=30, color=MINT, font=HEAD)
text(s, 0.7, 4.5, 10.5, 0.9, 'Адаптивная диагностика по математике для подготовки к ЕНТ: за один тест показывает базовую тему, из-за которой «сыпятся» все следующие.',
     size=18, color=RGBColor(0xD8, 0xE6, 0xE0))
text(s, 0.7, 6.45, 12, 0.4, [[('VentureHack 2026  ·  ', {}), ('Трек 2 — EduTech и образование будущего', {'bold': True}), ('  ·  тамыр (каз.) — корень', {})]],
     size=14, color=RGBColor(0xB5, 0xCC, 0xC3))
s.notes_slide.notes_text_frame.text = 'Tamyr — по-казахски «корень». Мы в треке EduTech. Мы находим не ошибку, а её причину.'

# ---------- 2. Проблема ----------
s = prs.slides.add_slide(BLANK)
bg(s, WHITE)
title(s, 'Ученик повторяет не ту тему', 'Проблема')
text(s, 0.7, 2.0, 5.6, 3.8, [
    [('Айгерим готовится к ЕНТ и ошибается в квадратных уравнениях.', {'bold': True})],
    'Пробник советует: «Повторите квадратные уравнения». Она повторяет, а ошибки остаются.',
    [('Настоящая причина лежит на три темы ниже: ', {}), ('она неверно складывает дроби', {'bold': True, 'color': RED}), (' — это материал 6 класса.', {})],
    'Тест показывает симптом, но не диагноз.',
], size=18, color=INK, spacing=14)
# цепочка
chain = [('Квадратные уравнения', 'ошибка видна здесь', RED_SOFT, RED, INK),
         ('Линейные уравнения', 'ошибка тянется отсюда', RED_SOFT, RED, INK),
         ('Действия с дробями', 'корень проблемы', RED, RED, WHITE)]
for i, (t, sub, fill, line, fc) in enumerate(chain):
    y = 2.0 + i * 1.55
    b = box(s, 7.3, y, 4.9, 0.95, fill, line)
    label(b, t, size=20, color=fc)
    text(s, 7.3, y + 1.0, 4.9, 0.3, sub, size=12, color=INK2, align=PP_ALIGN.CENTER, italic=True)
    if i < 2:
        arrow(s, 9.75, y + 1.3, 9.75, y + 1.55, RED, 2.5)
s.notes_slide.notes_text_frame.text = 'Пример проблемы. Ученица повторяет квадратные уравнения, но корень — в дробях 6 класса.'

# ---------- 3. Почему ----------
s = prs.slides.add_slide(BLANK)
bg(s, LIGHT)
title(s, 'Почему это происходит', 'Причины')
cards = [('Математика кумулятивна', 'Каждая тема держится на предыдущих. Пробел 5–6 класса всплывает через 2–4 года в другой теме.', GREEN),
         ('Тесты измеряют балл', 'Пробники и контрольные говорят, где ошибка произошла, но не почему. Выбранный неверный вариант не анализируется.', RED),
         ('У учителя нет времени', 'В классе 25–30 учеников. Индивидуально проверить каждого по всем темам с 5 по 9 класс невозможно.', AMBER)]
for i, (h, b, c) in enumerate(cards):
    x = 0.7 + i * 4.1
    card = box(s, x, 2.2, 3.8, 3.7, WHITE, radius=0.06)
    dot = box(s, x + 0.35, 2.55, 0.6, 0.6, c, shape=MSO_SHAPE.OVAL)
    label(dot, str(i + 1), size=20, color=WHITE)
    text(s, x + 0.35, 3.35, 3.1, 0.8, h, size=21, font=HEAD, bold=True)
    text(s, x + 0.35, 4.35, 3.1, 1.5, b, size=15, color=INK2)
text(s, 0.7, 6.2, 11.9, 0.6, [[('Место для вашей цифры из опроса: ', {'bold': True, 'color': RED}),
                              ('«__% учеников не понимают, почему ошиблись в пробнике» (n = __). Заполните по docs/validation-plan.md или удалите строку.', {'color': INK2})]], size=14)
s.notes_slide.notes_text_frame.text = 'Три причины. Если провели опрос, назовите реальную цифру; если нет, удалите нижнюю строку.'

# ---------- 4. Решение ----------
s = prs.slides.add_slide(BLANK)
bg(s, WHITE)
title(s, 'Три шага: найти корень → показать → починить', 'Решение')
steps = [('Адаптивная диагностика', 'Начинаем со сложной темы. При ошибке спускаемся по графу из 17 тем. Примерно вдвое меньше вопросов, чем в полном тесте.'),
         ('Карта знаний', 'Корневой пробел, цепочки «ошибка в X → корень в Y» и ошибки мышления по выбранным неверным ответам.'),
         ('План снизу вверх', 'Правило, пример, разбор своей ошибки и 2 проверочные задачи. Следующая тема откроется после корня.'),
         ('Панель учителя', 'Корни всего класса, частые ошибки, готовые мини-группы, тепловая карта и CSV.')]
for i, (h, b) in enumerate(steps):
    x = 0.7 + i * 3.08
    c = GREEN if i < 3 else DARK
    num = box(s, x, 2.3, 0.75, 0.75, c, shape=MSO_SHAPE.OVAL)
    label(num, str(i + 1) if i < 3 else '+', size=22, color=WHITE)
    if i < 2:
        arrow(s, x + 0.9, 2.675, x + 2.95, 2.675, GREEN_SOFT, 3)
    text(s, x, 3.35, 2.8, 0.8, h, size=21, font=HEAD, bold=True)
    text(s, x, 4.4, 2.8, 2.0, b, size=15, color=INK2)
box(s, 0.7, 6.25, 11.9, 0.65, GREEN_SOFT)
text(s, 0.95, 6.33, 11.4, 0.5, 'Работает в браузере на любом телефоне, без установки, регистрации и сервера.', size=16, color=GREEN, bold=True, anchor=MSO_ANCHOR.MIDDLE)

# ---------- 5. Как работает ----------
s = prs.slides.add_slide(BLANK)
bg(s, WHITE)
title(s, 'Как Tamyr ищет корень', 'Алгоритм')
# мини-граф слева
nodes = {'quad': (2.6, 2.1, 'Кв. уравнения', RED_SOFT, RED, INK), 'fact': (0.7, 3.35, 'Разложение', OK, OK, WHITE),
         'lin': (2.6, 3.35, 'Лин. уравнения', RED_SOFT, RED, INK), 'root': (4.5, 3.35, 'Корни', OK, OK, WHITE),
         'expr': (1.65, 4.6, 'Выражения', OK, OK, WHITE), 'frac': (3.55, 4.6, 'Дроби', RED, RED, WHITE),
         'arith': (3.55, 5.85, 'Арифметика', OK, OK, WHITE)}
W_, H_ = 1.7, 0.6
edges = [('quad', 'fact'), ('quad', 'lin'), ('quad', 'root'), ('lin', 'expr'), ('lin', 'frac'), ('frac', 'arith')]
for a, b in edges:
    ax, ay = nodes[a][0] + W_ / 2, nodes[a][1] + H_
    bx, by = nodes[b][0] + W_ / 2, nodes[b][1]
    bad = (a, b) in [('quad', 'lin'), ('lin', 'frac')]
    arrow(s, ax, ay, bx, by, RED if bad else RGBColor(0xC8, 0xC8, 0xC0), 2.5 if bad else 1.5)
for k, (x, y, t, f, l, fc) in nodes.items():
    b = box(s, x, y, W_, H_, f, l)
    label(b, t, size=13, color=fc)
text(s, 0.7, 6.65, 5.6, 0.4, 'Зелёный — освоено, красный — пробел, насыщенный красный — корень', size=12, color=INK2, italic=True)
# правила справа
rules = [('Решил тему без ошибок', '→ всё, на чём она держится, засчитано без вопросов', OK),
         ('Ошибся дважды', '→ спускаемся к непроверенным пререквизитам', RED),
         ('Неверный вариант с меткой', '→ сначала проверяем «домашнюю» тему этой ошибки', AMBER),
         ('Корень', '= пробел, под которым пробелов нет', DARK)]
for i, (h, b, c) in enumerate(rules):
    y = 2.1 + i * 0.95
    d = box(s, 6.9, y + 0.08, 0.32, 0.32, c, shape=MSO_SHAPE.OVAL)
    text(s, 7.4, y, 5.3, 0.4, h, size=17, bold=True)
    text(s, 7.4, y + 0.38, 5.3, 0.4, b, size=15, color=INK2)
box(s, 6.9, 5.95, 5.7, 1.05, LIGHT)
text(s, 7.15, 6.03, 5.3, 0.9, [[('1/2 + 1/3 = 2/5', {'bold': True, 'color': RED, 'size': 18}), ('   значит', {'color': INK2})],
                              [('«складывает числители с числителями, знаменатели со знаменателями» → тема «Дроби»', {'color': INK})]], size=14)
s.notes_slide.notes_text_frame.text = 'Объясните правила движка. Ключевая особенность: неверный вариант ответа говорит, какая именно это ошибка.'

# ---------- 6. Демо: ученик ----------
s = prs.slides.add_slide(BLANK)
bg(s, LIGHT)
title(s, 'Демо: карта знаний ученика', 'Продукт')
picture(s, IMG / 'demo.png', 0.7, 1.95, 7.6, crop_bottom=0.2)
pts = [('14 вопросов', 'на тему «Квадратные уравнения» и все её основы'),
       ('Корень — «Дроби»', 'хотя ошибки видны в квадратных и линейных уравнениях'),
       ('Ошибки мышления', 'по выбранным вариантам с правилом исправления'),
       ('План', '«Разобрать» → урок → 2 задачи → следующая тема')]
for i, (h, b) in enumerate(pts):
    y = 2.0 + i * 1.18
    text(s, 8.75, y, 3.9, 0.4, h, size=19, bold=True, color=GREEN)
    text(s, 8.75, y + 0.42, 3.9, 0.7, b, size=14, color=INK2)
s.notes_slide.notes_text_frame.text = 'Живое демо: #setup → «Квадратные уравнения» → отвечать как ученик с пробелом в дробях. Запасной вариант: #demo.'

# ---------- 7. Учитель ----------
s = prs.slides.add_slide(BLANK)
bg(s, WHITE)
title(s, 'Учитель видит корни всего класса', 'Панель учителя')
picture(s, IMG / 'teacher.png', 5.0, 1.95, 7.6, crop_bottom=0.12)
pts = [('Корневые пробелы класса', 'какие базовые темы тянут класс вниз'),
       ('Мини-группы', 'кого с кем посадить на 15-минутный разбор'),
       ('Тепловая карта и CSV', 'ученик × тема, выгрузка в журнал или Excel'),
       ('Без сервера', 'ученик передаёт результат кодом')]
for i, (h, b) in enumerate(pts):
    y = 2.0 + i * 1.18
    text(s, 0.7, y, 4.0, 0.4, h, size=19, bold=True, color=GREEN)
    text(s, 0.7, y + 0.42, 4.0, 0.7, b, size=14, color=INK2)
text(s, 0.7, 6.85, 12, 0.35, 'Демо-класс на скриншоте — 24 виртуальных ученика, прогнанных через тот же движок (симуляция, не реальные данные).', size=11, color=INK2, italic=True)

# ---------- 8. Доказательства ----------
s = prs.slides.add_slide(BLANK)
bg(s, DARK)
title(s, 'Что уже проверено', 'Валидация', color=WHITE, kcolor=MINT)
stats = [('81%', 'настоящих корней\nнайдено (полнота)'), ('75%', 'найденных корней\nверны (точность)'), ('25 / 51', 'вопросов в среднем\nвместо полного теста'), ('13 / 13', 'юнит-тестов\nдвижка проходят')]
for i, (n, l) in enumerate(stats):
    x = 0.7 + i * 3.1
    text(s, x, 2.15, 2.9, 1.0, n, size=48, font=HEAD, bold=True, color=MINT)
    text(s, x, 3.2, 2.9, 0.9, l, size=15, color=RGBColor(0xD8, 0xE6, 0xE0))
text(s, 0.7, 4.35, 11.9, 0.7, 'Симуляция 1000 учеников с известными пробелами: угадывание 20%, ошибки в знакомых темах 8%. Без шума алгоритм находит 100% корней. Точность ограничена угадыванием при 4 вариантах.',
     size=14, color=RGBColor(0xB5, 0xCC, 0xC3))
b = box(s, 0.7, 5.3, 11.9, 1.5, RGBColor(0x1F, 0x3D, 0x35), MINT, dash=True)
text(s, 1.0, 5.45, 11.3, 1.25, [[('Проверка на людях — заполните реальными данными:', {'bold': True, 'color': WHITE})],
                               [('опрос учеников (n = __), интервью с учителями (__ чел.), мини-пилот: совпадение корня с мнением учителя __ из __. Шаблоны: docs/validation-plan.md', {'color': RGBColor(0xD8, 0xE6, 0xE0)})]], size=15, spacing=6)
s.notes_slide.notes_text_frame.text = 'Говорите честно: это симуляция. Затем назовите то, что проверили на людях. Если ничего не успели, скажите, что пилот запланирован, и удалите пустые поля.'

# ---------- 9. Реализуемость и модель ----------
s = prs.slides.add_slide(BLANK)
bg(s, WHITE)
title(s, 'Реализуемо уже сейчас', 'Внедрение и модель')
cols = [('Технологии', ['HTML/CSS/JS без зависимостей', 'Работает офлайн на любом телефоне', 'Граф и банк заданий — данные: новый предмет = новый файл', 'Персональные данные остаются на устройстве']),
        ('Кому и за сколько', ['Ученикам: бесплатная диагностика, платные банки (геометрия, мат. грамотность)', 'Школам: панель учителя, подписка за класс', 'Учебным центрам: входная диагностика новых учеников']),
        ('Для запуска', ['Проверка графа 2–3 учителями', 'Банк 5–6 вопросов на тему', 'Казахская версия', 'Пилот в 2–3 классах'])]
for i, (h, items) in enumerate(cols):
    x = 0.7 + i * 4.1
    card = box(s, x, 2.1, 3.8, 4.5, LIGHT, radius=0.05)
    text(s, x + 0.3, 2.35, 3.2, 0.5, h, size=21, font=HEAD, bold=True, color=GREEN)
    tb = text(s, x + 0.3, 3.0, 3.25, 3.5, items, size=15, color=INK, spacing=10)
    for p in tb.text_frame.paragraphs:
        pPr = p._p.get_or_add_pPr()
        pPr.set('marL', str(Inches(0.22)))
        pPr.set('indent', str(-Inches(0.22)))
        bu = pPr.makeelement(qn('a:buChar'), {'char': '•'})
        pPr.append(bu)

# ---------- 10. Дорожная карта и команда ----------
s = prs.slides.add_slide(BLANK)
bg(s, DARK)
root_icon(s, 0.75, 0.6, 0.7, MINT)
text(s, 0.7, 1.55, 11.9, 0.9, 'Дальше — от прототипа к классу', size=36, font=HEAD, bold=True, color=WHITE)
road = [('Сейчас', 'MVP: 17 тем, 52 задания, 43 ошибки мышления, панель учителя'), ('1 месяц', 'Пилот в 2–3 классах, казахский язык'),
        ('3 месяца', 'Байесовская модель освоения, 5–6 вопросов на тему'), ('6 месяцев', 'Геометрия и мат. грамотность ЕНТ, вход по коду класса')]
for i, (h, b) in enumerate(road):
    x = 0.7 + i * 3.1
    dot = box(s, x, 2.85, 0.4, 0.4, MINT if i == 0 else RGBColor(0x3A, 0x6B, 0x5E), shape=MSO_SHAPE.OVAL)
    if i < 3:
        c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x + 0.5), Inches(3.05), Inches(x + 3.0), Inches(3.05))
        c.line.color.rgb = RGBColor(0x3A, 0x6B, 0x5E)
        c.line.width = Pt(2)
    text(s, x, 3.45, 2.8, 0.4, h, size=18, bold=True, color=MINT)
    text(s, x, 3.9, 2.8, 1.2, b, size=14, color=RGBColor(0xD8, 0xE6, 0xE0))
text(s, 0.7, 5.5, 11.9, 0.45, 'Команда: [Имя — роль] · [Имя — роль] · [Имя — роль]', size=18, color=WHITE, bold=True)
text(s, 0.7, 6.05, 11.9, 0.45, 'GitHub: [ссылка на репозиторий]   ·   Демо: [ссылка на GitHub Pages]', size=16, color=RGBColor(0xB5, 0xCC, 0xC3))

prs.save(OUT)
print('saved', OUT)
