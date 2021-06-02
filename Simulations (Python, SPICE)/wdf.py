'''source: https://github.com/multivac61/wave_digital_notebook/blob/master/WDFs_in_circuit_emulation.ipynb'''

import numpy as np
import pandas as pd
from scipy import signal
#from sympy import *
import matplotlib.pyplot as plt

#One-port
class WDFOnePort(object):
    def __init__(self):
        self.a, self.b = 0, 0

    # v = (a + b)/2
    def wave_to_voltage(self):
        voltage = (self.a + self.b)/2
        return voltage

#Resistor
class Resistor(WDFOnePort):
    def __init__(self, R):
        WDFOnePort.__init__(self)
        self.Rp = R

    def get_reflected_wave(self, a):
        self.a = a
        self.b = 0 # to avoid delay-free loop, reflected wave is always zero
        return self.b

class RootResistor(WDFOnePort):
  def __init__(self, R, Rp):
    WDFOnePort.__init__(self)
    self.R = R
    self.Rp = Rp

  # instantaneous reflection permitted
  def get_reflected_wave(self, a):
    self.b = a*(self.R - self.Rp)/(self.R + self.Rp)
    self.a = a
    return self.b

# Capacitor
class Capacitor(WDFOnePort):
    def __init__(self, C, fs=44100):
        WDFOnePort.__init__(self)
        self.Rp = 1/(2*fs*C)

    def get_reflected_wave(self, a):
        self.b = self.a
        self.a = a
        return self.b

    def set_incident_wave(self, a):
        self.a = a

# Inductor
class Inductor(WDFOnePort):
    def __init__(self, L, fs=44100):
        WDFOnePort.__init__(self)
        self.Rp = (2*fs*L)

    def get_reflected_wave(self, a):
        self.b = self.a
        self.a = a
        return -self.b

    def set_incident_wave(self, a):
        self.a = a

# Short Circuit
class ShortCircuit(WDFOnePort):
    def __init__(self):
        WDFOnePort.__init__(self)

    def get_reflected_wave(self, a):
        self.a = a
        self.b = -a
        return self.b

# Open Circuit
class OpenCircuit(WDFOnePort):
    def __init__(self):
        WDFOnePort.__init__(self)

    def get_reflected_wave(self, a):
        self.a = a
        self.b = b
        return self.b

# Switch
class Switch(WDFOnePort):
    def __init__(self):
        WDFOnePort.__init__(self)
        __state = False

    def get_reflected_wave(self, a):
        if __state: # switch closed
            self.a = a
            self.b = -a
        else:
            self.a = a
            self.b = a
        return self.b

    def change_state(self, state):
        __state = state

# Ideal Voltage Source
class IdealVoltageSource(WDFOnePort):
    def __init__(self):
        WDFOnePort.__init__(self)

    def get_reflected_wave(self, a, vs=0):
        self.a = a
        self.b = 2*vs - a
        return self.b

# Ideal Current Source
class IdealCurrentSource(WDFOnePort):
    def __init__(self):
        WDFOnePort.__init__(self)

    def get_reflected_wave(self, a, i_s=0):
        self.a = a
        self.b = a - 2*self.Rp*i_s
        return self.b

# Resistive Voltage Source
class ResistiveVoltageSource(WDFOnePort):
    def __init__(self, Rs):
        WDFOnePort.__init__(self)
        self.Rp = Rs

    def get_reflected_wave(self, a, vs=0):
        self.a = a
        self.b = vs
        return self.b

# Resistive Current Source
class ResistiveCurrentSource(WDFOnePort):
    def __init__(self, Rs):
        WDFOnePort.__init__(self)
        self.Rp = Rs

    def get_reflected_wave(self, a, i_s = 0):
        self.a = a
        self.b = self.Rp*i_s
        return self.b

# Two - port adaptors
def parallel_adaptor2(a1, Rp1, a2, Rp2):
    gamma = (Rp1 - Rp2)/(Rp1 + Rp2)
    S = np.array(((gamma, 1 - gamma), (1-gamma, gamma)))
    b1, b2 = np.dot(S, np.array((a1, a2)))
    return b1, b2

def series_adaptor2(a1, Rp1, a2, Rp2):
    gamma = (Rp1 - Rp2) / (Rp1 + Rp2)
    S = np.array(((gamma, 1-gamma), (1-gamma, gamma)))
    b1, b2 = np.dot(S, np.array((a1, a2)))
    return b1, b2

# N-port adaptors
def series_adaptor(A, R):
    Rsum = np.sum(R)
    Asum = np.sum(A)
    return[a - 2*r/Rsum*Asum for a, r in zip(A, R)]

def parallel_adaptor(A, R):
    G = [1/r for r in R]
    Gsum = np.sum(G)
    Gamma = [2*g / Gsum for g in G]
    aDotGamma = np.dot(A, Gamma)
    return [aDotGamma - a for a in A]

''' SPQR trees:
leaves represent components and adaptors
branches represent connections
root: I'm less clear on

1. collect waves from "root-facing" leaf nodes
2. wave-up: propagate waves up through adaptor nodes
3. calculate reflected wave at root
4. wave-down: propagate reflected wave down tree
5. gather outputs and store states

'''
# RC First Order Low-pass Filter
def RCLPF(R=10, C=3.5e-5, Rs=1, fs=44100, N=2**14):
    input = np.zeros(N)
    input[0] = 1 # delta function
    output = np.zeros(input.size)
    steps = np.arange(N)

    V1 = ResistiveVoltageSource(Rs)
    C1 = Capacitor(C, fs=fs)
    R1 = Resistor(R)

    # port resistances
    Rp1, Rp2, Rp3 = C1.Rp, R1.Rp, V1.Rp

    # simulation loop
    b1, b2, b3 = 0, 0, 0
    for i in steps:
        # 1. collect waves from "root-facing" leaf nodes
        a1 = C1.get_reflected_wave(b1) # not sure why this is different from R1 or V1
        a2 = R1.get_reflected_wave(0) # might be b/c reflected wave of resistor is always 0
        a3 = V1.get_reflected_wave(0, input[i]) # read input signal off voltage source (ie, treat vs like input signal)

        # 2. wave-up
        A = (a1, a2, a3)
        RP = (Rp1, Rp2, Rp3)

        # 3. calculate reflected wave at root / 4. wave-down
        b1, b2, b3 = series_adaptor(A, RP)

        # 5. gather outputs
        output[i] = C1.wave_to_voltage() # output is voltage across C1
        C1.set_incident_wave(b1) # store new input incide C1

    return output

'''my code'''

# notes on diode clipper (src: Simulating Guitar Distortion Circuits Using Wave Digital and Nonlinear State-space Formulations, David Yeh & Julius Smith)
# v = (a+b)/2 , i = (a-b)/(2*Rp)
# for two reverse-polarity diodes in parallel, current through is defined Id(v) = 2Is*sinh(v/Vt) = 2Is*sinh((a+b)/2Vt)
# nonlinear equation to solve: Id(v) - i = 0 --> 2Is*sinh((a+b)/2Vt) - (a-b)/(2*Rp) = 0
# solve for b....... somehow...

# Diode
#class Diode(WDFOnePort): # not actually sure if one-port or not
#    def __init__(self):

class ReversePolarityParallelDiodes(WDFOnePort):
    '''
    V = (a+b)/2
    i = (a - b) / (2*Rp)
    Id(V) = 2Is*sinh(V/Vt) = 2Is*sinh((a+b)/2Vt)

    '''
    def __init__(self, Is = 2.52e-9, Vt = 45.3e-3):
        self.Is = Is
        self.Vt = Vt
        WDFOnePort.__init__(self)

    def get_reflected_wave(self, a):
        self.a = a
        #self.b = TODO
        return self.b