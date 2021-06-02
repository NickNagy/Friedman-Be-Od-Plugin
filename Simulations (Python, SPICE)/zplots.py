import numpy as np
import pandas as pd
from scipy import signal
from matplotlib import pyplot as plt

# src: https://github.com/multivac61/wave_digital_notebook/blob/master/WDFs_in_circuit_emulation.ipynb
def plot_ltspice_freq_z(axes, filename, title="Frequency response", vout_key='V(vout)'):
    plot_phase = False
    if len(axes) > 1:
      plot_phase = True
      ax_phase = axes[1]
    ax_mag = axes[0]
    def imag_to_mag(z):
        a, b = map(float, z.strip('\"').split(','))
        return 20*np.log10(np.sqrt(a*a+b*b))
    def imag_to_phase(z):
        a, b = map(float, z.strip('\"').split(','))
        return np.arctan((b/a))
    x = pd.read_csv(filename)
    x['H_dB'] = x[vout_key].apply(imag_to_mag)
    f = np.array(x['Freq.'])
    H_db = np.array(x['H_dB'])
    ax_mag.semilogx(f, H_db, label="LTspice")
    if plot_phase:
      x['Phase'] = x[vout_key].apply(imag_to_phase)*180/np.pi
      Phase = np.array(x['Phase'])
      ax_phase.semilogx(f, Phase, label="LTspice")

def plot_from_freq_z(axes, f, h, label):
  plot_phase = False
  if len(axes) > 1:
    plot_phase = True
    ax_phase = axes[1]
  ax_mag = axes[0]
  H = 20*np.log10(np.abs(h))
  ax_mag.semilogx(f, H, label=label)
  if plot_phase:
    phase = np.unwrap(np.angle(h, deg=True))#*180/np.pi
    ax_phase.semilogx(f, phase, label=label)

def plot_wdf_freq_z(axes, x, fs):
    f, h = signal.freqz(x, 1, worN=4096, fs=fs)
    plot_from_freq_z(axes, f, h, label="Wave digital")

def plot_transf_freq_z(axes, b, a, fs):
    f, h = signal.freqz(b, a, worN=4096, fs=fs)
    plot_from_freq_z(axes, f, h, label="Direct transfer function")