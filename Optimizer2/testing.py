from Optimizer.const import *
import pulp as pl
import math


def P_1(v0, time, info, throw_ball) -> list:
    v = math.sqrt(v0**2 + 2*g*h)*e
    tc = time + (v - math.sqrt(v**2 - 2*g*h))/g
    tf = tc + info['p_r'] + info['p_i'][1] - info['p_i'][0]
    return [v, 1, 1, 0, time, tf]


def P_2(v0, time, info, throw_ball) -> list:  # terminar
    v = math.sqrt(v0**2 + 2*g*h)*e
    v1 = math.sqrt(v**2 - 2*g*h)
    tk = time - (v - v1)/g

    tc = info['t_f'] - info['p_r'] - info['p_i'][1] + info['p_i'][0]
    tf = tc + info['p_r'] + info['p_i'][1] - info['p_i'][0]
    return [v1, 1, 1, 0, tk, tf]


def move_A(bounce: list, A_Length):
    bounce[4] += A_Length
    bounce[5] += A_Length
    for i in range(len(bounce[-1])):
        bounce[-1][i] += A_Length


def fix_bounce(bounce: list, A_info, B_info, end: bool = True):
    # tc = t_f - t_i + p_r -p_i
    # [v0, c_h, b_a, c_b, ti, tf]
    if not end:
        move_A(bounce, A_info[1]-A_info[0])
    times = bounce[-1]
    info = {
        't_f': bounce[5],
        'p_r': (0 if bounce[2] == 1 or bounce[2] == 0 else times[-1]),
        'p_i': (A_info if end else B_info)
    }
    tc = info['t_f'] - info['p_r'] - info['p_i'][1] + info['p_i'][0]

    if bounce[2] == 0:
        return bounce
    elif times[0] < bounce[4]:
        if end:
            return None
        else:
            times[0] -= B_info[1]
            return bounce
    elif bounce[2] == 2 and times[1] < bounce[4]:
        if end:
            return P_1(bounce[0], times[0], info, bounce[3]).append([times[0]])
        else:
            return P_2(bounce[0], times[1], info, bounce[3]).append([times[1]])
    elif tc < bounce[4]:
        return bounce if end else None
    elif bounce[4] < tc:
        return bounce
    raise NotImplementedError("algo anda mal :v")


def gustavo_fix(bounce: list, A_info, B_info, end: bool = True):
    if bounce[2] == 1:
        return bounce
    times = bounce[-1]
    info = {
        't_f': bounce[5],
        'p_r': (0 if bounce[2] == 1 or bounce[2] == 0 else times[-1]),
        'p_i': (A_info if end else B_info)
    }
    if info['p_r'] < bounce[4]:
        bounce[5] = (bounce[4] + info['p_r']) / 2
    else:
        bounce[5] = ((bounce[4] + info['p_r'] +
                     info['p_i'][1]) / 2) % info['p_i'][1]
    bounce[5] += info['p_r'] + info['p_i'][1] - info['p_i'][0]
    return bounce


def empty_bounce(A_info, B_info, end: bool = True):
    ti = A_info[1] if end else B_info[1]
    return [0, 0, 0, 0, ti, 0, []]


def CY(brouce_1: list, brouce_2: list):
    if brouce_1[2] != 1:
        return 0
    tf = brouce_2[4]
    ti = brouce_1[-1][0]
    if tf < ti:
        return 0
    tc = (tf - ti)
    return h/tc - g*tc / 2


def CZ(brouce_1: list, brouce_2: list):
    if brouce_1[2] != 2:
        return 0
    tf = brouce_2[4]
    ti = brouce_1[-1][1]
    if tf < ti:
        return 0
    tc = (tf - ti)
    return h/tc - g*tc / 2


def P(bounce_i: list, bounce_j: list):
    if bounce_i[5] <= bounce_j[4]:
        return 1
    return 0


def V(bounce_i: list, bounce_j: list):
    times_i = bounce_i[-1]
    if bounce_i[2] != 0 and (times_i[-1] < bounce_j[4]):
        return 1
    return 0


def R(bounce_i: list):
    if bounce_i[2] == 1:
        return 1
    return 0


def model(A, B, A_all_sol, B_all_sol, balls=2):
    A_info = A[0], A[-1]
    B_info = B[0], B[-1]

    Cy = [0] * balls*balls
    Cz = [0] * balls*balls

    A_balls_last_bounce = []
    B_balls_first_bounce = []

    for b in range(balls):
        last_bounce = A_all_sol[b].pop() if len(
            A_all_sol[b]) != 0 else empty_bounce(A_info, B_info, end=True)
        first_bounce = B_all_sol[b].pop(0) if len(
            B_all_sol[b]) != 0 else empty_bounce(A_info, B_info, end=False)

        last_bounce = gustavo_fix(last_bounce, A_info, B_info, end=True)
        first_bounce = gustavo_fix(first_bounce, A_info, B_info, end=False)

        fix_last_bounce = fix_bounce(last_bounce, A_info, B_info, end=True)
        fix_first_bounce = fix_bounce(first_bounce, A_info, B_info, end=False)

        fix_last_bounce = fix_last_bounce if fix_last_bounce else (
            last_bounce if len(A_all_sol[b]) == 0 else A_all_sol[b].pop()
        )
        fix_first_bounce = fix_first_bounce if fix_first_bounce else (
            first_bounce if len(B_all_sol[b]) == 0 else B_all_sol[b].pop(0)
        )

        A_balls_last_bounce.append(fix_last_bounce)
        B_balls_first_bounce.append(fix_first_bounce)

    for Ab in range(balls):
        if A_balls_last_bounce[Ab][2] != 2:
            continue
        for Bb in range(balls):
            if B_balls_first_bounce[Bb][2] != 2:
                continue
            Cy[Ab * balls + Bb] = CY(A_balls_last_bounce[Ab],
                                     B_balls_first_bounce[Bb])
            Cz[Ab * balls + Bb] = CZ(A_balls_last_bounce[Ab],
                                     B_balls_first_bounce[Bb])

    prob = pl.LpProblem("Problem", pl.LpMinimize)

    X = pl.LpVariable.dicts("X", range(balls*balls), cat=pl.LpBinary)
    Y = pl.LpVariable.dicts("Y", range(balls*balls), cat=pl.LpBinary)
    Z = pl.LpVariable.dicts("Z", range(balls*balls), cat=pl.LpBinary)

    OB = pl.LpAffineExpression(
        [(Y[i*balls + j], Cy[i*balls + j]) for i in range(balls) for j in range(balls)] +
        [(Z[i*balls + j], Cz[i*balls + j]) for i in range(balls) for j in range(balls)])

    for i in range(balls):
        sum_bi = []
        for j in range(balls):
            sum_bi.append(X[i*balls + j] + Y[i*balls + j] + Z[i*balls + j])
        prob += pl.LpConstraint(sum(sum_bi) - 1, sense=pl.LpConstraintEQ)

    for j in range(balls):
        sum_bj = []
        for i in range(balls):
            sum_bj.append(X[i*balls + j] + Y[i*balls + j] + Z[i*balls + j])
        prob += pl.LpConstraint(sum(sum_bj) - 1, sense=pl.LpConstraintEQ)

    for i in range(balls):
        for j in range(balls):
            prob += pl.LpConstraint(X[i*balls + j] -
                                    P(A_balls_last_bounce[i], B_balls_first_bounce[j]), sense=pl.LpConstraintLE)
            prob += pl.LpConstraint(Y[i*balls + j] -
                                    V(A_balls_last_bounce[i], B_balls_first_bounce[j]) *
                                    R(A_balls_last_bounce[i]) *
                                    (1 - P(A_balls_last_bounce[i], B_balls_first_bounce[j])), sense=pl.LpConstraintLE)
            prob += pl.LpConstraint(Z[i*balls + j] -
                                    V(A_balls_last_bounce[i], B_balls_first_bounce[j]) *
                                    (1 - R(A_balls_last_bounce[i])) *
                                    (1 - P(A_balls_last_bounce[i], B_balls_first_bounce[j])), sense=pl.LpConstraintLE)

    print(f"RESULT: {prob.solve()}")

    print(f"X : {[(x, int(index / balls), index % balls, 'A: ' + ('doble' if A_balls_last_bounce[int(index / balls)][2] == 2 else 'simple') + f', {A_balls_last_bounce[int(index / balls)][5]}') for (index, x) in X.items() if x.varValue > 0]}")

    print(f"Y : {[(x, int(index / balls), index % balls, 'A: ' + ('doble' if A_balls_last_bounce[int(index / balls)][2] == 2 else 'simple') + f', {A_balls_last_bounce[int(index / balls)][5]}') for (index, x) in Y.items() if x.varValue > 0]}")

    print(f"Z : {[(x, int(index / balls), index % balls, 'A: ' + ('doble' if A_balls_last_bounce[int(index / balls)][2] == 2 else 'simple') + f', {A_balls_last_bounce[int(index / balls)][5]}') for (index, x) in Z.items() if x.varValue > 0]}")
