"""Лабораторная работа № 12. Вариант 19. Ситникова Ольга Алексеевна."""
import math  # расстояния и факториал
import platform  # сведения о компьютере
import random  # случайные города и маршруты
import statistics  # среднее значение
import time  # замер времени
from itertools import permutations  # перебор маршрутов
import matplotlib.pyplot as plt  # графики и визуализация маршрутов

N_BIG, TRIALS, RUNS_SMALL, RUNS_BIG = 250, 30, 10, 50  # размерность для эвристик, число наборов, запусков 2-opt на малых и большой размерностях


def generate_cities(n, seed=42):  # n случайных городов на плоскости 100 × 100
    rng = random.Random(seed)  # генератор с фиксированным seed
    return [(rng.uniform(0, 100), rng.uniform(0, 100)) for _ in range(n)]  # список координат


def distance_matrix(cities):  # матрица евклидовых расстояний
    n = len(cities)  # число городов
    D = [[0.0] * n for _ in range(n)]  # матрица из нулей
    for i in range(n):  # перебираем пары городов
        for j in range(i + 1, n):  # только i < j (матрица симметрична)
            D[i][j] = D[j][i] = math.dist(cities[i], cities[j])  # расстояние между городами
    return D  # матрица расстояний


def tour_length(tour, D):  # длина замкнутого маршрута
    return sum(D[tour[i]][tour[(i + 1) % len(tour)]] for i in range(len(tour)))  # сумма рёбер с возвратом в начало


def brute_force(D):  # точный алгоритм: полный перебор, Θ(n!); первый город фиксирован
    best_tour, best_len = None, float("inf")  # лучший найденный маршрут
    for perm in permutations(range(1, len(D))):  # все порядки остальных городов
        tour = (0,) + perm  # маршрут начинается с города 0
        length = tour_length(tour, D)  # длина маршрута
        if length < best_len:  # найден более короткий маршрут
            best_tour, best_len = tour, length  # запоминаем его
    return list(best_tour), best_len  # оптимальный маршрут и его длина


def random_tour(n, rng):  # конструктивная эвристика: случайный маршрут, Θ(n)
    tour = list(range(n))  # города в порядке номеров
    rng.shuffle(tour)  # случайная перестановка
    return tour  # маршрут


def two_opt(tour, D, max_passes=100):  # локальный поиск в окрестности 2-opt
    n, tour = len(tour), tour[:]  # число городов и копия маршрута
    for _ in range(max_passes):  # проходы повторяются, пока есть улучшения
        improved = False  # в этом проходе улучшений пока нет
        for i in range(1, n - 1):  # начало разворачиваемого участка
            for j in range(i + 1, n):  # конец разворачиваемого участка
                delta = (D[tour[i - 1]][tour[j]] + D[tour[i]][tour[(j + 1) % n]]  # новые рёбра
                         - D[tour[i - 1]][tour[i]] - D[tour[j]][tour[(j + 1) % n]])  # минус удаляемые рёбра
                if delta < -1e-12:  # длина уменьшается
                    tour[i:j + 1] = reversed(tour[i:j + 1])  # разворачиваем участок i…j
                    improved = True  # улучшение найдено
        if not improved:  # локальный оптимум достигнут
            break  # выходим
    return tour, tour_length(tour, D)  # маршрут и его длина


def multi_start(D, runs, rng):  # 2-opt с многократным запуском из случайных начальных маршрутов
    best_tour, best_len, history, lengths = None, float("inf"), [], []  # лучший результат, история лучшей длины и длины всех запусков
    for _ in range(runs):  # несколько запусков
        tour, length = two_opt(random_tour(len(D), rng), D)  # запуск из нового случайного маршрута
        if length < best_len:  # результат лучше прежнего
            best_tour, best_len = tour, length  # запоминаем
        history.append(best_len)  # лучшая длина после очередного запуска
        lengths.append(length)  # длина результата этого запуска
    return best_tour, best_len, history, lengths  # лучший маршрут, длина, история и длины запусков


def draw(ax, cities, tour, title):  # рисунок маршрута на плоскости (М5)
    pts = [cities[c] for c in tour + [tour[0]]]  # координаты городов маршрута с возвратом в начало
    ax.plot([p[0] for p in pts], [p[1] for p in pts], "-", color="#2f5496", linewidth=0.8)  # линия маршрута
    ax.scatter([c[0] for c in cities], [c[1] for c in cities], s=8, color="#c0392b", zorder=3)  # города
    ax.set(title=title, aspect="equal", xticks=[], yticks=[])  # оформление


if __name__ == "__main__":  # запуск только при прямом старте файла
    print(platform.platform(), "|", platform.processor() or platform.machine(), "| Python", platform.python_version())  # система
    print("\n   n | маршрутов (n-1)! | полный перебор, с")  # заголовок таблицы
    ns, times = [], []  # размеры и времена для графика
    for n in range(5, 12):  # размерности, доступные полному перебору
        D = distance_matrix(generate_cities(n))  # случайные города
        t0 = time.perf_counter()  # начало замера
        brute_force(D)  # полный перебор
        times.append(time.perf_counter() - t0)  # время перебора
        ns.append(n)  # размер
        print(f"{n:>4} | {math.factorial(n - 1):>16} | {times[-1]:>17.4f}")  # строка таблицы
    c = times[-1] / math.factorial(ns[-1] - 1)  # время на один маршрут (по последнему измерению)
    for n in (12, 13, 15, 20):  # оценка времени для больших n
        print(f"{n:>4} | {math.factorial(n - 1):>16} | оценка {c * math.factorial(n - 1):.3e} с")  # экстраполяция
    print(f"\nОтклонение от оптимума по {TRIALS} наборам (2-opt: один запуск и {RUNS_SMALL} запусков)")  # заголовок
    print("   n | случайный, % | 2-opt, % (оптимум) | многократный, % (оптимум)")  # заголовок таблицы
    dev_table = {}  # отклонения для графика
    for n in range(6, 11):  # малые размерности
        dev, hits = {"rand": [], "one": [], "multi": []}, {"one": 0, "multi": 0}  # отклонения и число попаданий в оптимум
        for trial in range(TRIALS):  # серия наборов данных
            D, rng = distance_matrix(generate_cities(n, seed=100 + trial)), random.Random(trial)  # набор и свой генератор
            opt = brute_force(D)[1]  # точный оптимум
            start = random_tour(n, rng)  # случайный маршрут
            l_one = two_opt(start, D)[1]  # 2-opt из этого маршрута
            l_multi = multi_start(D, RUNS_SMALL, rng)[1]  # многократный запуск
            for key, length in (("rand", tour_length(start, D)), ("one", l_one), ("multi", l_multi)):  # три метода
                dev[key].append((length - opt) / opt * 100)  # отклонение в процентах
            hits["one"] += abs(l_one - opt) < 1e-9  # 2-opt достиг оптимума
            hits["multi"] += abs(l_multi - opt) < 1e-9  # многократный запуск достиг оптимума
        dev_table[n] = [statistics.mean(dev[k]) for k in ("rand", "one", "multi")]  # средние отклонения
        print(f"{n:>4} | {dev_table[n][0]:>12.2f} | {dev_table[n][1]:>8.2f} ({hits['one'] / TRIALS * 100:>4.0f} %) | {dev_table[n][2]:>10.2f} ({hits['multi'] / TRIALS * 100:>4.0f} %)")  # строка
    cities, rng = generate_cities(N_BIG), random.Random(0)  # города и генератор для большой размерности
    D = distance_matrix(cities)  # матрица расстояний
    start = random_tour(N_BIG, rng)  # случайный маршрут
    t0 = time.perf_counter()  # начало замера одного запуска
    tour_one, l_one = two_opt(start, D)  # 2-opt из случайного маршрута
    t_one = time.perf_counter() - t0  # время одного запуска
    t0 = time.perf_counter()  # начало замера многократного запуска
    tour_multi, l_multi, history, lengths = multi_start(D, RUNS_BIG, rng)  # многократный запуск
    t_multi = time.perf_counter() - t0  # время многократного запуска
    print(f"\nN = {N_BIG} городов:")  # заголовок большой размерности
    print(f"  случайный маршрут: длина {tour_length(start, D):9.1f}")  # длина случайного маршрута
    print(f"  2-opt (1 запуск):  длина {l_one:9.1f}, время {t_one:.4f} с")  # один запуск
    print(f"  2-opt ({RUNS_BIG} запусков): длина {l_multi:9.1f}, время {t_multi:.4f} с")  # многократный запуск
    print("  лучшая длина после запусков 1, 5, 10, 25, 50:", [round(history[k - 1], 1) for k in (1, 5, 10, 25, 50)])  # история
    print(f"  длины {RUNS_BIG} одиночных запусков: среднее {statistics.mean(lengths):.1f}, минимум {min(lengths):.1f}, максимум {max(lengths):.1f}")  # разброс запусков
    lg = math.lgamma(N_BIG) / math.log(10)  # log10((N-1)!) — само число не помещается в float
    print(f"  число маршрутов полного перебора (N-1)! ≈ {10 ** (lg % 1):.2f} · 10^{int(lg)}")  # размер пространства поиска
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))  # два графика рядом
    ax1.plot(ns, times, "o-")  # время полного перебора
    ax1.set(xlabel="n", ylabel="Время, с", title="Полный перебор: рост времени", yscale="log")  # оформление
    xs = list(dev_table)  # размерности
    for k, (label, off) in enumerate((("Случайный маршрут", -0.27), ("2-opt, 1 запуск", 0), (f"2-opt, {RUNS_SMALL} запусков", 0.27))):  # три набора столбцов
        ax2.bar([x + off for x in xs], [dev_table[x][k] for x in xs], 0.27, label=label)  # столбцы отклонений
    ax2.set(xlabel="n", ylabel="Среднее отклонение от оптимума, %", title=f"Качество эвристик ({TRIALS} наборов)", yscale="log")  # оформление
    for ax in (ax1, ax2):  # общее оформление
        ax.grid(True, alpha=0.3, which="both")  # сетка
    ax2.legend()  # легенда
    plt.tight_layout()  # убираем наложение подписей
    plt.savefig("lab12_graphs.png", dpi=150)  # сохраняем графики для отчёта
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))  # визуализация маршрутов (М5)
    draw(axes[0], cities, start, f"Случайный маршрут: {tour_length(start, D):.0f}")  # до локального поиска
    draw(axes[1], cities, tour_one, f"2-opt, 1 запуск: {l_one:.0f}")  # после одного запуска
    draw(axes[2], cities, tour_multi, f"2-opt, {RUNS_BIG} запусков: {l_multi:.0f}")  # после многократного запуска
    plt.tight_layout(rect=[0, 0, 1, 0.94])  # оставляем место под заголовки рисунков
    plt.savefig("lab12_routes.png", dpi=130)  # сохраняем рисунок маршрутов
    plt.show()  # показываем графики на экране
