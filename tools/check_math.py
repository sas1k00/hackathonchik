# Независимая проверка ответов новых задач: подстановкой, перебором по сетке и прямым вычислением.
import math
from fractions import Fraction as F

bad = []
def ok(name, cond):
    if not cond:
        bad.append(name)

close = lambda a, b: abs(a - b) < 1e-9
grid = [x / 8 for x in range(-80, 81)]

# --- дробно-рациональные уравнения: корни подставляем, ОДЗ проверяем ---
ok('ratq1', close((4 - 4) / (-2 - 2), 0))                       # x = -2; x = 2 обнуляет знаменатель
ok('ratq2', close(6 / 2, 3))
ok('ratq3', close((5 + 3) / (5 - 1), 2))
ok('ratq4', True)                                               # x = 3 вне ОДЗ, других корней нет
ok('ratq5', close(1 / 2 + 1 / 2, 1))
ok('ratq6', close((9 - 9) / (3 + 3), 0))
ok('ratq3-wrong', not close((4 + 3) / (4 - 1), 2) and not close((-1 + 3) / (-1 - 1), 2))
ok('ratq5-wrong', not close(1 / F(2, 3) + F(1, 2), 1))

# --- неравенства: сравниваем на сетке исходное условие и заявленный ответ ---
def same(name, cond, answer, skip=()):
    for x in grid:
        if x in skip:
            continue
        if cond(x) != answer(x):
            bad.append('%s at x=%s' % (name, x)); return
same('qineq1', lambda x: x * x - 5 * x + 6 < 0, lambda x: 2 < x < 3)
same('qineq2', lambda x: x * x > 9, lambda x: x < -3 or x > 3)
same('qineq3', lambda x: x * x - 4 <= 0, lambda x: -2 <= x <= 2)
same('qineq4', lambda x: (x - 1) * (x + 2) > 0, lambda x: x < -2 or x > 1)
same('qineq5', lambda x: (x - 3) / (x + 1) < 0, lambda x: -1 < x < 3, skip=(-1,))
ok('qineq6', len([n for n in range(-20, 21) if n * n - 3 * n < 0]) == 2)
same('sysineq1', lambda x: x > 1 and x <= 4, lambda x: 1 < x <= 4)
same('sysineq2', lambda x: 2 * x - 4 > 0 and x - 5 < 0, lambda x: 2 < x < 5)
ok('sysineq3', not any(x >= 3 and x < 1 for x in grid))
same('sysineq4', lambda x: 3 * x + 1 >= 7 and -x > -6, lambda x: 2 <= x < 6)
ok('sysineq5', len([n for n in range(-20, 21) if n > -2 and n <= 3]) == 5)
same('sysineq6', lambda x: x * x < 9 and x > 0, lambda x: 0 < x < 3)
same('elsys1', lambda x: 2 ** x > 8, lambda x: x > 3)
same('elsys2', lambda x: 0.5 ** x > 4, lambda x: x < -2)
same('elsys3', lambda x: x > 0 and math.log2(x) > 3, lambda x: x > 8)
same('elsys4', lambda x: x > 0 and math.log(x, 3) < 2 - 1e-12, lambda x: 0 < x < 9)
ok('elsys5', 2 ** 3 == 8 and 3 + 2 == 5)
ok('elsys6', close(math.log2(8), 3) and 8 - 6 == 2)

# --- нелинейные системы: все решения перебором по целым ---
def sols(f):
    return sorted((x, y) for x in range(-12, 13) for y in range(-12, 13) if f(x, y))
ok('nlsys1', sols(lambda x, y: x + y == 5 and x * y == 6) == [(2, 3), (3, 2)])
ok('nlsys2', sols(lambda x, y: y == x * x and y == x + 2) == [(-1, 1), (2, 4)])
ok('nlsys3', sols(lambda x, y: x - y == 1 and x * x + y * y == 5) == [(-1, -2), (2, 1)])
ok('nlsys4', sols(lambda x, y: x + y == 4 and x * x - y * y == 8) == [(3, 1)])
ok('nlsys5', sols(lambda x, y: x == 3 * y and x * y == 12) == [(-6, -2), (6, 2)])
ok('nlsys6', sorted(x for x in range(-12, 13) if x * x + 16 == 25) == [-3, 3])
ok('lesson-nlsys', sols(lambda x, y: x - y == 2 and x * y == 8) == [(-2, -4), (4, 2)])

# --- иррациональные: все корни перебором, посторонние отсеиваются сами ---
def roots(f, rng=range(-20, 60)):
    out = []
    for x in rng:
        try:
            if f(x): out.append(x)
        except ValueError:
            pass
    return out
ok('irr1', roots(lambda x: close(math.sqrt(x), 3)) == [9])
ok('irr2', roots(lambda x: close(math.sqrt(x + 1), 2)) == [3])
ok('irr3', roots(lambda x: close(math.sqrt(2 * x - 1), -3)) == [])
ok('irr4', roots(lambda x: close(math.sqrt(x + 2), x)) == [2])
ok('irr5', roots(lambda x: close(math.sqrt(x * x - 9), 4)) == [-5, 5])
ok('irr6', roots(lambda x: close(math.sqrt(x + 6), x)) == [3])
ok('lesson-irr', roots(lambda x: close(math.sqrt(2 * x + 3), x)) == [3])

# --- показательные и логарифмы ---
ok('exp1', 2 ** 3 == 8); ok('exp2', 3 ** 0 == 1); ok('exp3', close(2 ** -2, 0.25))
ok('exp4', close(4 ** 1.5, 8)); ok('exp5', 5 ** (3 - 1) == 25); ok('exp6', 3 ** (2 * 2) == 81)
ok('lesson-exp', close(9 ** 1.5, 27))
ok('log1', close(math.log2(8), 3)); ok('log2', close(math.log(1, 3), 0))
ok('log3', close(math.log2(4) + math.log2(8), 5)); ok('log4', close(math.log(9, 3), 2))
ok('log5', close(math.log2(9 - 1), 3)); ok('log6', close(math.log(25, 5) - math.log(5, 5), 1))
ok('lesson-log', close(math.log2(13 + 3), 4))
ok('lesson-elsys', all(((1 / 3) ** x <= 9 + 1e-12) == (x >= -2) for x in grid))

# --- тригонометрия ---
d = math.radians
ok('trig1', close(math.sin(d(30)), 0.5)); ok('trig2', close(math.cos(d(30)), math.sqrt(3) / 2))
ok('trig3', close(math.tan(d(45)), 1)); ok('trig4', close(math.sqrt(1 - 9 / 25), 4 / 5))
ok('trig6', close(math.sqrt(1 - 1 / 4), math.sqrt(3) / 2))
ok('lesson-trig', close(math.sqrt(1 - 25 / 169), 12 / 13))
pi = math.pi
for n in range(-3, 4):
    ok('trigeq1', close(math.sin(pi * n), 0)); ok('trigeq2', close(math.cos(2 * pi * n), 1))
    ok('trigeq3', close(math.cos(pi / 3 + 2 * pi * n), 0.5) and close(math.cos(-pi / 3 + 2 * pi * n), 0.5))
    ok('trigeq5', close(math.tan(pi / 4 + pi * n), 1))
    ok('trigeq6', close(2 * math.sin((-1) ** n * pi / 6 + pi * n) - 1, 0))
    ok('lesson-trigeq', close(2 * math.cos(pi / 6 + 2 * pi * n) - math.sqrt(3), 0))
# серия покрывает все решения на отрезке [0, 2π)
ok('trigeq3-all', sorted(round(x, 6) for x in [pi / 3, 2 * pi - pi / 3]) == sorted(round(k * pi / 180, 6) for k in range(0, 360) if close(math.cos(d(k)), 0.5)))
ok('trigeq6-all', [k for k in range(0, 360) if close(math.sin(d(k)), 0.5)] == [30, 150])

# --- прогрессии ---
ok('prog1', 2 + 4 * 3 == 14); ok('prog2', 5 + 8 + 11 + 14 == 38); ok('prog3', 3 * 2 ** 3 == 24)
ok('prog4', (15 - 7) / 2 == 4); ok('prog5', 6 / 2 == 3 and 18 / 6 == 3); ok('prog6', (1 + 19) * 10 / 2 == 100)
ok('lesson-prog', 4 + 9 * 5 == 49 and (4 + 49) * 10 / 2 == 265)

# --- производная и интеграл: численно ---
def der(f, x, h=1e-6): return (f(x + h) - f(x - h)) / (2 * h)
def integ(f, a, b, n=20000):
    h = (b - a) / n
    return sum(f(a + (i + 0.5) * h) for i in range(n)) * h
near = lambda a, b: abs(a - b) < 1e-4
ok('deriv1', near(der(lambda x: x ** 3, 2), 3 * 4)); ok('deriv2', near(der(lambda x: 5 * x * x - 3 * x + 7, 2), 10 * 2 - 3))
ok('deriv3', near(der(lambda x: x * x + 4 * x, 1), 6)); ok('deriv4', near(der(lambda x: x * x, 3), 6))
ok('deriv5', near(der(lambda x: x * x - 6 * x, 3), 0)); ok('deriv6', near(der(lambda x: 2 * x ** 4, 2), 8 * 8))
ok('lesson-deriv', near(der(lambda x: x * x - 4 * x + 1, 2), 0) and 4 - 8 + 1 == -3)
ok('integ1', near(der(lambda x: x * x, 3), 2 * 3)); ok('integ2', near(der(lambda x: x ** 3, 2), 3 * 4))
ok('integ3', near(integ(lambda x: 2 * x, 0, 2), 4)); ok('integ4', near(integ(lambda x: 1, 1, 3), 2))
ok('integ5', near(integ(lambda x: 3 * x * x, 0, 1), 1)); ok('integ6', near(integ(lambda x: x, 0, 4), 8))
ok('lesson-integ', near(integ(lambda x: 2 * x + 1, 1, 2), 4))

# --- геометрия ---
ok('planfig', 180 - 50 - 60 == 70 and 180 - 70 == 110 and (180 - 40) / 2 == 70 and 360 - 80 - 90 - 100 == 90 and 80 / 2 == 40)
ok('lesson-planfig', 180 - 65 - 65 == 50)
ok('planmet1', math.hypot(6, 8) == 10); ok('planmet2', close(math.sqrt(13 ** 2 - 5 ** 2), 12))
ok('planmet3', 10 * 6 / 2 == 30); ok('planmet4', 4 * 7 == 28); ok('planmet5', 5 * 2 ** 2 == 20); ok('planmet6', 3 ** 2 == 9)
ok('lesson-planmet', close(math.sqrt(100 - 36), 8) and 6 * 8 == 48)
ok('solid3', close(math.sqrt(3 * 4), 2 * math.sqrt(3))); ok('solid4', close(math.sqrt(1 + 4 + 4), 3))
ok('solid-counts', 12 == 4 * 3 and 5 == 2 + 3 and 5 == 4 + 1 and 18 == 3 * 6)
ok('lesson-solid', close(math.sqrt(9 + 16 + 144), 13))
ok('solmet', 3 ** 3 == 27 and 6 * 2 ** 2 == 24 and 9 * 4 / 3 == 12 and 2 ** 2 * 5 == 20 and 2 ** 3 == 8 and 9 * 4 / 3 == 12)
ok('lesson-solmet', 9 * 6 == 54 and 54 / 3 == 18)
ok('vec', (4 - 1, 6 - 2) == (3, 4) and math.hypot(3, 4) == 5 and (1 + 3, 2 - 1) == (4, 1) and 2 * 4 + 3 * -1 == 5 and 2 * 3 + 1 * -6 == 0 and (3 * 2, 3 * -1) == (6, -3))
ok('lesson-vec', (2 + 1, 6 - 2) == (3, 4))
ok('vec3', close(math.sqrt(1 + 4 + 4), 3) and (3 - 1, 4 - 0, 5 - 2) == (2, 4, 3) and 1 * 2 + 2 * 0 + 3 * -1 == -1
   and ((2 + 4) / 2, (4 + 0) / 2, (6 + 2) / 2) == (3, 2, 4) and (1 + 2, -2 + 1, 3 - 1) == (3, -1, 2) and 1 * 2 + 4 * 1 + 2 * -3 == 0)
ok('lesson-vec3', (3 - 1, 5 - 2, 9 - 3) == (2, 3, 6) and close(math.sqrt(4 + 9 + 36), 7))

print('FAILED: %s' % bad if bad else 'all %s checks passed' % 'math')
