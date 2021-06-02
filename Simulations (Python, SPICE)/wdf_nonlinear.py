from wdf import WDFOnePort
from math import exp, log, frexp
import numpy as np
import decimal #for handling overflow
from plots import *

def sgn(x):
  if x < 0:
    return -1
  elif x == 0:
    return 0
  else:
    return 1

# TODO: this is just an approx for log base-2
def log2_approx(x):
  alpha = 0.1640425613334452
  beta = -1.098865286222744
  gamma = 3.148297929334117
  zeta = -2.213475204444817
  return alpha*x**3 + beta*x**2 + gamma*x + zeta

def log_approx(x):
  M,E = frexp(x) # mantissa and exponent of floating point x
  e = 2.71828182846
  return (E + log2_approx(1+M))/log2_approx(e)

# TODO
def e_approx(x):
  return 0

def w_approx1(x):
  return max(0, x)

def w_approx2(x):
  x1 = -3.684303659906469
  x2 = 1.972967391708859
  alpha = 9.451797158780131e-3
  beta = 1.126446405111627e-1
  gamma = 4.451353886588814e-1
  zeta = 6.313183464296682e-1
  if (x <= x1):
    return 0
  elif (x < x2):
    return alpha*x**3 + beta*x**2 + gamma*x + zeta
  else:
    return x

def w_approx3(x):
  x1 = -3.341459552768620
  x2 = 8
  alpha = -1.314293149877800e-3
  beta = 4.775931364975583e-2
  gamma = 3.631952663804445e-1
  zeta = 6.313183464296682e-1
  if (x <= x1):
    return 0
  elif (x < x2):
    return alpha*x**3 + beta*x**2 + gamma*x + zeta
  else:
    return x-log(x)#log_approx(x)

def w_approx4(x):
  w3 = w_approx3(x)
  return w3 - (w3 - exp(x-w3))/(w3+1)#e_approx(x - w3)/(w3+1))

def w_approx_arr(arr, w_approx_func):
  num_samples = len(arr)
  out = np.ndarray((num_samples))
  for i in range(num_samples):
    out[i] = w_approx_func(arr[i])
  return out

def plot_w_approximation(ax, stop, steps, w_approx_func, label):
  x = np.linspace(0, stop, num=steps)
  y = w_approx_arr(x, w_approx_func)
  ax.plot(x, y, label=label)

def plot_w_approximations(ax, stop, steps):
  plot_w_approximation(ax, stop, steps, w_approx1, "w1(x)")
  plot_w_approximation(ax, stop, steps, w_approx2, "w2(x)")
  plot_w_approximation(ax, stop, steps, w_approx3, "w3(x)")
  plot_w_approximation(ax, stop, steps, w_approx4, "w4(x)")
  handles,labels = ax.get_legend_handles_labels()
  ax.legend(handles,labels)

class DiodeClipperPair(WDFOnePort):
  def __init__(self, R, Is=0.1e-15, Vt=26e-3):
    self.Rp = R
    self.Is = Is
    self.Vt = Vt

  def get_reflected_wave(self, a):
    self.a = a
    W = w_approx3((abs(a) + self.Rp*self.Is)/self.Vt + log(self.Rp*self.Is/self.Vt))
    self.b = sgn(a)*(abs(a) + 2*self.Rp*self.Is - 2*self.Vt*W)
    return self.b