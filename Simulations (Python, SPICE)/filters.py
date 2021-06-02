from scipy import signal
from matplotlib import pyplot as plt
import math
import numpy as np
import pandas as pd

def firstOrderRCLPFCoeffs(R, C, fs):
    wA = 1/(R*C)
    k = 2*fs
    wD = k*math.atan(wA/k)
    d = 1 + k/wD
    B0 = 1/d
    B1 = 1/d
    A0 = 1
    A1 = (1 - k/wD)/d
    return ([B0, B1], [A0, A1])

def firstOrderRCHPFCoeffs(R, C, fs):
    wA = 1/(R*C)
    k = 2*fs
    wD = k*math.atan(wA/k)
    d = wD + k
    B0 = k/d
    B1 = -k/d
    A0 = 1
    A1 = (wD - k)/d
    return ([B0, B1],[A0,A1])

# R1 and C1: high-pass
# R2 and C2: low-pass
def passiveRCBPFCoeffs(R1, C1, R2, C2, fs):
    wA = 1/math.sqrt(R1*C1*R2*C2)
    k = 2*fs
    wD = k*math.atan(wA/k)
    aK2 = (k**2)/(wD**2)
    bK = (C1*R1 + C2*R1 + C2*R2)*k
    gK = C1*R1*k
    d = aK2 + bK + 1
    B0 = gK/d
    B1 = 0
    B2 = -gK/d
    A0 = 1
    A1 = (2 - 2*aK2)/d
    A2 = (aK2-bK+1)/d
    return ([B0, B1, B2],[A0, A1, A2])