import math
from .const import *

# region Funciones Auxiliares

def P_aux(ti, h, throw_ball, current_time):
    v0 = (math.sqrt(2*g*h*(1-math.pow(e, 2)))/e)  if throw_ball else (math.sqrt(2*g*h)/math.pow(e, 2))
    tk = ti - (((v0 + math.sqrt(2*g*(h + (v0**2/(2*g)))))/g) if throw_ball else ((v0 - math.sqrt(v0**2 - 2*g*h))/g))

    vy = 0
    if throw_ball:
        current_h = h + ((v0*v0)/(2*g))
        vy = math.sqrt(2*g*current_h)*e
    else:
        vy = (-v0 if v0 > 0 else v0)*e
    
    # print(vy*vy,  2*g*h)
    tf = abs((vy + math.sqrt(abs(vy*vy - 2*g*h)))/(g))
    
    return [-v0 if throw_ball else v0, 1, 1, 0, tk, ti+tf]

def Q_aux(ti, tj, h, throw_ball, current_time):
    v0 =math.sqrt(((g*g)*(tj - ti)**2)/(4*(e*e)) - 2*g *h) if throw_ball else ((g*(tj - ti))/(2*e))    
    tk =  ti - (((v0 + math.sqrt(2*g*(h + (v0**2/(2*g)))))/g) if throw_ball else ((v0 - math.sqrt(v0**2 - 2*g*h))/g))


    vy = 0
    if throw_ball:
        current_h = h + ((v0*v0)/(2*g))
        vy = math.sqrt(2*g*current_h)*(e**2)
    else:
        vy = (-v0 if v0 > 0 else v0)*(e**2)
    
    # print(vy*vy,  2*g*h)
    tf = abs((vy + math.sqrt(abs(vy*vy - 2*g*h)))/(g))

    return [-v0 if throw_ball else v0, 1, 2, 0, tk, tj+tf]

# 0.22039287762738288
# endregion

# region Funciones

# posiblidad de lanzar una pelota y rebote en el instante de tiempo ti
def P(ti, h, throw_ball, v0=None, current_time=0):  # throw_ball = 1 (lanzamiento hacia arriba)
    if v0 is None:
        v0 = (math.sqrt(2*g*h*(1-e**2))/e) if throw_ball else (math.sqrt(2*g*h)/e**2)

    if v0 < 0 or not ((v0 >= (math.sqrt(2*g*h*(1 - e*e))/e)) if throw_ball else (v0 >= (math.sqrt(2*g*h)/g))):
        return False

    if throw_ball and v0 > 4.5:
        return False
    
    if not throw_ball and v0 > 7:
        return False

    try:
        return ti - current_time >= (((v0 + math.sqrt(2*g*(h + (v0**2/(2*g)))))/g) if throw_ball else ((v0 - math.sqrt(v0**2 - 2*g*h))/g))
    except Exception:
        return False

# posibilidad de lanzar una pelota y rebotar en los instantes de tiempo ti y tj, sin internvencion


def Q(ti, tj, h, throw_ball, current_time=0):  # throw_ball = 1 (lanzamiento hacia arriba)
    try:
        v0 = math.sqrt(((g*g)*((tj - ti)**2))/(4*(e*e)) - 2*g *h) if throw_ball else (g*(tj - ti))/(2*e)
        
        # print(ti, tj, v0, math.sqrt(2*g*h)/e**2, (v0 >= (math.sqrt(2*g*h*(1/e**4 - 1)) if throw_ball else math.sqrt(2*g*h)/e**2)))
        
        return P(ti, h, throw_ball, v0=v0, current_time=current_time) and (v0 >= (math.sqrt(2*g*h*(1/e**4 - 1)) if throw_ball else math.sqrt(2*g*h)/e**2))
    except:
        return False

# posibilidad de lanzar una pelota y rebote en el instente de tiempo ti, tj y...
# sea capturada por el malabarista y vuelva ser rebotada en el instante tk


def S(ti, tj, tk, h, throw_ball):
    if Q(ti, tj, h, throw_ball):
        v0 = math.sqrt(((g*g)*((tj - ti)**2))/(4*(e*e)) - 2*g*h) if throw_ball else (g*(tj - ti))/(2*e)
        vf = e*e*(math.sqrt(2*g*(h + (v0*v0)/(2*g)))) if throw_ball else e*e*v0
        total_time = (vf - math.sqrt(vf*vf - 2*g*h))/(g) + tj  # ! NO SE TIENE EN CUENTA LA FORMA DE CAPTURA DE LA PELOTA, SE ASUME QUE SIEMPRE SE CAPTURA POR DEBAJO
        if total_time + epsilon_time < tk:
            return P(tk, h, throw_ball, current_time=total_time + epsilon_time)
    return False

# posibilidad de lanzar una pelota y rebote en el instente de tiempo ti, tj y...
# sea capturada por el malabarista y vuelva ser rebotada en el instante tk y tm


def SS(ti, tj, tk, tm, h, throw_ball):
    if Q(ti, tj, h, throw_ball):
        try:
            v0 = math.sqrt(((g*g)*(tj - ti)**2)/(4*(e*e)) - 2*g*h) if throw_ball else (g*(tj - ti))/2*e
            vf = e*e*(math.sqrt(2*g*(h + (v0*v0)/(2*g)))) if throw_ball else e*e*v0
            total_time = (vf - math.sqrt(vf*vf - 2*g*h))/(g) + tj  # ! NO SE TIENE EN CUENTA LA FORMA DE CAPTURA DE LA PELOTA, SE ASUME QUE SIEMPRE SE CAPTURA POR DEBAJO
            if total_time + epsilon_time < tk:
                return Q(tk, tm, h, throw_ball, current_time=total_time + epsilon_time)
        except:
            return False
    return False

# posibilidad de lanzar una pelota y rebote en el instante de tiempo ti y
# sea capturada por el malabarista y vuelva ser rebotada en el instante tj


def R(ti, tj, h, throw_ball):
    if P(ti, h, throw_ball):
        try:
            v0 = ((g*(ti))/2 - h/(ti)) if throw_ball else (h/(ti) + (g*(ti))/2)
            vf = e*(math.sqrt(2*g*(h + (v0*v0)/(2*g)))) if throw_ball else e*v0
            total_time = (vf - math.sqrt(vf*vf - 2*g*h))/(g) + ti
            if total_time + epsilon_time < tj:
                return P(tj, h, throw_ball, current_time=total_time + epsilon_time)
        except:
            return False
    return False

# posibilidad de lanzar una pelota y rebote en el instente de tiempo ti y
# sea capturada por el malabarista y vuelva ser rebotada en el instante tj y tk


def RR(ti, tj, tk, h, throw_ball):
    if P(ti, h, throw_ball):
        try:
            v0 = ((g*(ti))/2 - h/(ti)) if throw_ball else (h/(ti) + (g*(ti))/2)
            vf = e*(math.sqrt(2*g*(h + (v0*v0)/(2*g)))) if throw_ball else e*v0
            total_time = (vf - math.sqrt(vf*vf - 2*g*h))/(g) + ti
            if total_time + epsilon_time < tj:
                return Q(tj, tk, h, throw_ball, current_time=total_time + epsilon_time)
        except:
            return False
    return False

# endregion
