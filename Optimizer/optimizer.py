import pulp as pl
import numpy as np
import math, itertools
import time
from .functions import (
    P, Q, S, SS, R, RR,
    P_aux, Q_aux
)
from .const import *
from .utils import (
    get_interval,
    get_positions,
    check_init,
    get_internal_interval
)

class Optimizer:
    def __init__(self, sequence_times, balls, loop=False, throw_type=0) -> None:
        self.times = sequence_times
        self.__original_length = len(sequence_times) - 1
        self.balls = balls
        self.loop = loop
        self.throw_type = throw_type
        self.d = None

        if not loop:
            s = 0.8 if throw_type else 0.25
            for i in range(len(self.times)):
                self.times[i] += s
        
        if self.loop:
            a = 0; b = 1
            while b < self.__original_length:
                self.times.append(self.times[-1] + (self.times[b] - self.times[a]))
                a += 1
                b += 1
        
        self.prob = None #pl.LpProblem("Problem", pl.LpMinimize)

        self.X = None #pl.LpVariable.dicts("X", range(self.balls*len(self.times)), cat=pl.LpBinary)
        self.Y = None #pl.LpVariable.dicts("Y", range(self.balls*len(self.times)*len(self.times)), cat=pl.LpBinary)
        
        self.result = None
    
    def default_preconditions(self) -> None:
        for b in range(self.balls):
            for i in range(len(self.times)):
                for j in range(i + 1, len(self.times)):
                    self.prob += pl.LpConstraint(self.X[b*len(self.times) + i] + self.X[b*len(self.times) + j] - 1 - R(self.times[i], self.times[j], h, self.throw_type), sense=pl.LpConstraintLE, name=f"X{b}{i} X{b}{j} <= 1 R{b}{i}{j}")

                    self.prob += pl.LpConstraint(self.Y[b*len(self.times)**2 + i*len(self.times) + j] - Q(self.times[i], self.times[j], h, self.throw_type), sense=pl.LpConstraintLE, name=f"Y{b}{i}{j} <= Q{b}{i}{j}")

                    for k in range(j + 1, len(self.times)):
                        self.prob += pl.LpConstraint(self.X[b*len(self.times) + i] + self.Y[b*len(self.times)**2 + j*len(self.times) + k] - 1 - RR(self.times[i], self.times[j], self.times[k], h, self.throw_type), sense=pl.LpConstraintLE, name=f"X{b}{i} Y{b}{j}{k} <= 1 RR{b}{i}{j}{k}")

                        self.prob += pl.LpConstraint(self.Y[b*len(self.times)**2 + i*len(self.times) + j] + self.X[b*len(self.times) + k] - 1 - S(self.times[i], self.times[j], self.times[k], h, self.throw_type), sense=pl.LpConstraintLE, name=f"Y{b}{i}{j} X{b}{k} <= 1 S{b}{i}{j}{k}")

                        for m in range(k + 1, len(self.times)):
                            self.prob += pl.LpConstraint(self.Y[b*len(self.times)**2 + i*len(self.times) + j] + self.Y[b*len(self.times)**2 + k*len(self.times) + m] - 1 - SS(self.times[i], self.times[j], self.times[k], self.times[m], h, self.throw_type), sense=pl.LpConstraintLE, name=f"Y{b}{i}{j} Y{b}{k}{m} <= 1 S{b}{i}{j}{k}{m}")

                    sum_Xk = []
                    sum_Ykm = []
                    sum_YdK = []
                    for k in range(i + 1, j):
                        sum_Xk.append(self.X[b*len(self.times) + k])
                        
                        for m in range(k + 1, len(self.times)):
                            sum_Ykm.append(self.Y[b*len(self.times)**2 + k*len(self.times) + m])
                            
                        for d in range(k):
                            sum_YdK.append(self.Y[b*len(self.times)**2 + d*len(self.times) + k])

                    self.prob += pl.LpConstraint(sum(sum_Xk) + sum(sum_Ykm) + sum(sum_YdK) - (1 - self.Y[b*len(self.times)**2 + i*len(self.times) + j])*len(self.times), sense=pl.LpConstraintLE)

        for i in range(len(self.times)):
            sum_ti = []
            for b in range(self.balls):
                sum_ti.append(self.X[b*len(self.times) + i])

            for j in range(i + 1, len(self.times)):
                for b in range(self.balls):
                    sum_ti.append(self.Y[b*len(self.times)**2 + i*len(self.times) + j])

            for k in range(0, i):
                for b in range(self.balls):
                    sum_ti.append(self.Y[b*len(self.times)**2 + k*len(self.times) + i])

            self.prob += pl.LpConstraint(sum(sum_ti) - 1, sense=pl.LpConstraintEQ, name=f"Sum t{i}")

    
    def loop_preconditions(self) -> None:
        for b in  range(self.balls):
            for i in  range(self.__original_length):
                for j in range(self.__original_length):
                    if i != j:
                        position = get_positions(len=self.__original_length, i=i, j=j)
                        
                        self.prob += pl.LpConstraint(self.X[b*self.__original_length + i] + self.X[b*self.__original_length + j] - 1 - R(self.times[position['i']], self.times[position['j']], h, self.throw_type), sense=pl.LpConstraintLE)
                        self.prob += pl.LpConstraint(self.Y[b*self.__original_length**2 + i*self.__original_length + j] - Q(self.times[position['i']], self.times[position['j']], h, self.throw_type), sense=pl.LpConstraintLE)

                        inter1 = get_interval(i, j, self.__original_length) 
                        for k in inter1:
                            if k != j:
                                position = get_positions(len=self.__original_length, i=i, j=j, k=k)
                                self.prob += pl.LpConstraint(self.X[b*self.__original_length + i] + self.Y[b*self.__original_length**2 + j*self.__original_length + k] - 1 - RR(self.times[position['i']], self.times[position['j']], self.times[position['k']], h, self.throw_type), sense=pl.LpConstraintLE)

                                self.prob += pl.LpConstraint(self.Y[b*self.__original_length**2 + i*self.__original_length + j] + self.X[b*self.__original_length + k] - 1 - S(self.times[position['i']], self.times[position['j']], self.times[position['k']], h, self.throw_type), sense=pl.LpConstraintLE)
                                
                                
                                inter2 = get_interval(i, k, self.__original_length) 
                                for m in inter2:
                                    if k != m:
                                        position = get_positions(len=self.__original_length - 1, i=i, j=j, k=k, m=m)
                                        self.prob += pl.LpConstraint(self.Y[b*self.__original_length**2 + i*self.__original_length + j] + self.Y[b*self.__original_length**2 + k*self.__original_length + m] - 1 - SS(self.times[position['i']], self.times[position['j']], self.times[position['k']], self.times[position['m']], h, self.throw_type), sense=pl.LpConstraintLE)
                        
                        sum_Xk = []
                        sum_Ykm = []
                        sum_YdK = []
                        inter3 = get_internal_interval(i, j, self.__original_length)
                        for k in inter3:
                            sum_Xk.append(self.X[b*self.__original_length + k])
                            
                            inter4 = get_interval(k, k + 1, self.__original_length) + ([k + 1] if k + 1 < self.__original_length else [])
                            for m in inter4: #range(k + 1, self.__original_length):
                                sum_Ykm.append(self.Y[b*self.__original_length**2 + k*self.__original_length + m])
                                sum_YdK.append(self.Y[b*self.__original_length**2 + m*self.__original_length + k])
                            
                            self.prob += pl.LpConstraint(sum(sum_Xk) + sum(sum_Ykm) + sum(sum_YdK) - (1 - self.Y[b*self.__original_length**2 + i*self.__original_length + j])*self.__original_length, sense=pl.LpConstraintLE)
                                    
        for i in range(self.__original_length):
            sum_ti = []
            for b in range(self.balls):
                sum_ti.append(self.X[b*self.__original_length + i])

            for j in range(self.__original_length):
                for b in range(self.balls):
                    if i != j and check_init(i, j, end=self.__original_length - 1):
                        sum_ti.append(self.Y[b*self.__original_length**2 + i*self.__original_length + j])

            for k in range(self.__original_length):
                for b in range(self.balls):
                    if k != i and check_init(i, k, end=self.__original_length - 1):
                        sum_ti.append(self.Y[b*self.__original_length**2 + k*self.__original_length + i])

            self.prob += pl.LpConstraint(sum(sum_ti) - 1, sense=pl.LpConstraintEQ)

    def solve(self) -> int:
        self.__get_problem()   
        self.result = self.prob.solve()
        # np.set_printoptions(threshold=np.inf)
        # if self.loop:            
        #     print(np.array([self.X[i].varValue for i in range(self.balls*self.__original_length)]).reshape((self.balls, self.__original_length)).astype('int'))
        #     print(np.array([self.Y[i].varValue for i in range(self.balls*self.__original_length*self.__original_length)]).reshape((self.balls, self.__original_length, self.__original_length)))
        # else:
        #     print(np.array([self.X[i].varValue for i in range(self.balls*len(self.times))]).reshape((self.balls, len(self.times))).astype('int'))
        #     print(np.array([self.Y[i].varValue for i in range(self.balls*len(self.times)*len(self.times))]).reshape((self.balls, len(self.times), len(self.times))))
        # print(self.prob)
        return self.result
        
    def get_solution(self):
        if self.result == 1:
            if self.loop:
                print(f"X : {[(x, int(index / self.__original_length), index % self.__original_length) for (index, x) in self.X.items() if x.varValue and x.varValue > 0]}")
                print(f"Y : {[(x, int(index / self.__original_length), index % self.__original_length) for (index, x) in self.Y.items() if x.varValue and x.varValue > 0]}")
                return self.__get_loop_solutions()
            else:
                return self.__get_default_solutions()

        raise Exception('Something went wrong! :/')
    
    
    def __get_default_solutions(self):
        list_throw_balls = [[] for _ in range(self.balls)]
        list_total_times_balls = [0 for _ in range(self.balls)]

        for b in range(self.balls):
            for i in range(len(self.times)):
                if self.X[b*len(self.times) + i].varValue == 1:
                    _t = [self.times[i]]
                    _sol = P_aux(self.times[i], h, throw_ball=self.throw_type, current_time=list_total_times_balls[b])
                    _sol.append(_t)
                    list_throw_balls[b].append(_sol)
                    list_total_times_balls[b] += list_throw_balls[b][-1][-2]

                for j in range(i+1,len(self.times)):
                    if self.Y[b*len(self.times)**2 + i*len(self.times) + j].varValue == 1:
                        _t = [self.times[i], self.times[j]]
                        _sol = Q_aux(self.times[i], self.times[j], h, self.throw_type, current_time=list_total_times_balls[b])
                        _sol.append(_t)
                        list_throw_balls[b].append(_sol)
                        list_total_times_balls[b] += list_throw_balls[b][-1][-2]

            list_throw_balls[b].sort(key=lambda x: x[4])
            
        return list_throw_balls
    
    def __get_loop_solutions(self):
        list_throw_balls = [[] for _ in range(self.balls)]
        list_total_times_balls = [0 for _ in range(self.balls)]

        for b in range(self.balls):
            for i in range(self.__original_length):
                if self.X[b*self.__original_length + i].varValue == 1:
                    _t = [self.times[i]]
                    _sol = P_aux(self.times[i], h, throw_ball=self.throw_type, current_time=list_total_times_balls[b])
                    _sol.append(_t)
                    list_throw_balls[b].append(_sol)
                    list_total_times_balls[b] += list_throw_balls[b][-1][-2]

                for j in range(self.__original_length):
                        if self.Y[b*self.__original_length**2 + i*self.__original_length + j].varValue == 1:
                            _t = [self.times[i], self.times[j]]
                            # _t.sort()
                            position = get_positions(len=self.__original_length, i=i, j=j)
                            _sol = Q_aux(self.times[position['i']], self.times[position['j']], h, self.throw_type, current_time=list_total_times_balls[b])
                            _sol.append(_t)
                            list_throw_balls[b].append(_sol)
                            list_total_times_balls[b] += list_throw_balls[b][-1][-2]

            list_throw_balls[b].sort(key=lambda x: x[4])

        return list_throw_balls
    
    def __get_problem(self):
        if self.loop:
            self.prob = pl.LpProblem("Problem", pl.LpMinimize)

            self.X = pl.LpVariable.dicts("X", range(self.balls*self.__original_length), cat=pl.LpBinary)
            self.Y = pl.LpVariable.dicts("Y", range(self.balls*self.__original_length*self.__original_length), cat=pl.LpBinary)
            
            self.loop_preconditions()
        else:
            self.prob = pl.LpProblem("Problem", pl.LpMinimize)

            self.X = pl.LpVariable.dicts("X", range(self.balls*len(self.times)), cat=pl.LpBinary)
            self.Y = pl.LpVariable.dicts("Y", range(self.balls*len(self.times)*len(self.times)), cat=pl.LpBinary)
            
            self.default_preconditions()
        return self.prob
    
    def __get_variables(self, length):
        _var = []
        for b in range(self.balls):
            for i in range(length):
                if self.X[b*length + i].varValue == 1:
                    _var.append(self.X[b*length + i])

                for j in range(length):
                    if self.Y[b*length**2 + i*length + j].varValue == 1:
                        _var.append(self.Y[b*length**2 + i*length + j])
        return _var
    
    def get_all_solutions(self):
        solutions = []
        import time
        self.__get_problem()
        temp = 0 
        count = 0
        while self.prob.solve() == 1:# and len(solutions) < 10:
            temp_sol = self.__get_variables(self.__original_length if self.loop else len(self.times))
            # print("Variables", temp_sol)
            if self.loop:            
                X = np.array([self.X[i].varValue for i in range(self.balls*self.__original_length)]).reshape((self.balls, self.__original_length)).astype('int')
                Y = np.array([self.Y[i].varValue for i in range(self.balls*self.__original_length*self.__original_length)]).reshape((self.balls, self.__original_length, self.__original_length))
            else:
                X = np.array([self.X[i].varValue for i in range(self.balls*len(self.times))]).reshape((self.balls, len(self.times))).astype('int')
                Y = np.array([self.Y[i].varValue for i in range(self.balls*len(self.times)*len(self.times) )]).reshape((self.balls, len(self.times), len(self.times)))
            
            
            solutions.append([temp_sol, (X, Y), self.__get_loop_solutions() if self.loop else self.__get_default_solutions()])
            
        #     # self.get_all_permutation_solution(temp_sol)
            _solutions = self.get_all_permutation_solution(temp_sol)
        #     # print('#'*100)
            for s in _solutions:
        #         # print(s)
                self.prob += pl.LpConstraint(sum(s) - (len(s) - 1), sense=pl.LpConstraintLE)
        #     # print('#'*100)
        # # print("Tiempo TODAS:", time.time() - t)
        return solutions


    def get_all_permutation_solution(self, solution):
        permutation = itertools.permutations(range(self.balls), self.balls)
        _sol = []
        l = len(self.times) if not self.loop else self.__original_length

        for p in permutation:
            temp_sol = []
            for v in range(len(solution)):
                v_type, v_index = solution[v].name.split('_')
                b, ti, tj = self.get_throw(v_type, int(v_index))
                temp_sol.append(self.X[p[b]*l + ti] if v_type == "X" else self.Y[p[b]*l**2 + ti*l + tj])
            _sol.append(temp_sol)
        return _sol
            # self.prob += pl.LpConstraint(sum(temp_sol) - (len(temp_sol) - 1), sense=pl.LpConstraintLE)
    
    def get_throw(self, v_type, v_index):
        if v_type == "X":
            return math.floor(v_index/(len(self.times) if not self.loop else self.__original_length)), v_index % (len(self.times) if not self.loop else self.__original_length), None

        elif v_type == "Y":
            return math.floor(v_index/(len(self.times) if not self.loop else self.__original_length)**2),\
                    math.floor(v_index/(len(self.times) if not self.loop else self.__original_length))%(len(self.times) if not self.loop else self.__original_length),\
                    v_index%(len(self.times) if not self.loop else self.__original_length)
        
        return NotImplementedError()


