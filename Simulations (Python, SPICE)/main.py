import random
from wdf import *
from wdf_nonlinear import *
from filters import *
from zplots import *
from friedman import *
from wdf_test_circuits import *
from matplotlib import pyplot as plt
import os

csv_dir = "./Friedman/data/"
plots_dir = "./Friedman/plots/"
bass_subdir = "bass/"
tight_subdir = "tight/"

def prepare_plots(plot_phase=False):
  fig = plt.figure()
  if plot_phase:
    ax_mag = fig.add_subplot(121)
    ax_phase = fig.add_subplot(122)
    ax_phase.set_ylim([-180, 180])
    ax_phase.set_ylabel("Phase (degrees)")
    axes = [ax_mag, ax_phase]
  else:
    ax_mag = fig.add_subplot(111)
    axes = [ax_mag]
  ax_mag.set_ylabel("Magnitude (dB)")
  ax_mag.set_ylim([0.0, 60.0])
  for ax in axes:
      ax.spines["left"].set_visible(False)
      ax.spines["right"].set_visible(False)
      ax.spines["top"].set_visible(False)
      ax.spines["bottom"].set_visible(False)
      ax.yaxis.set_ticks_position('left')
      ax.xaxis.set_ticks_position('bottom')
      ax.set_xlim([20.0, 1000.0])#20000.0])
      ax.set_xlabel("Frequency (Hz)")
  return fig, axes

def create_plot_from_csv_file(csv_dir, plots_dir, subdir, filename, vout_key='V(vout)', zTransform_func=None, wdf_func=None, fs=44100, parameterized=False):
  csv_file = csv_dir + subdir + filename
  img_filename = filename.split('.')[0]
  if parameterized:
    param = int(img_filename) # get value before '.csv' in name
  fig, axes = prepare_plots()
  plot_ltspice_freq_z(axes, csv_file, vout_key=vout_key)
  if zTransform_func is not None:
    if parameterized:
      b,a = zTransform_func(param, fs)
    else:
      b,a = zTransform_func(fs)
    plot_transf_freq_z(axes, b, a, fs)
  if wdf_func is not None:
    if parameterized:
      x = wdf_func(param, fs)
    else:
      x = wdf_func(fs)
    plot_wdf_freq_z(axes, x, fs)
  # get legend info from ax_mag since legend is repeated in ax_phase
  handles,labels = axes[0].get_legend_handles_labels()
  fig.legend(handles,labels)
  fig.suptitle("Rx = " + str(param) + r'$\Omega$') #TODO
  img_filename += '.png' # save as png file
  fig.savefig(os.path.join(plots_dir, subdir, img_filename))

def create_plots_from_csv_subdir(csv_dir, plots_dir, subdir, vout_key='V(vout)', zTransform_func=None, wdf_func=None, fs=44100, parameterized=True):
  csv_subdir = csv_dir + subdir
  for _, _, files in os.walk(csv_subdir):
    # filter out non-csv files
    files = [file for file in files if file.endswith(".csv")]
    for file in files:
      print(file)
      create_plot_from_csv_file(csv_dir, plots_dir, subdir, file, vout_key=vout_key,zTransform_func=zTransform_func, wdf_func=wdf_func, fs=fs, parameterized=parameterized)

def create_lone_wdf_plot(plots_dir, subdir, wdf_func, fs=44100, img_name="test"):
  fig, axes = prepare_plots()
  x = wdf_func(fs)
  plot_wdf_freq_z(axes, x, fs)
  img_name += ".png"
  fig.savefig(os.path.join(plots_dir, subdir, img_name))

# just a dumb loop-hole
def RC_zTest(R, fs):
  return firstOrderRCLPFCoeffs(R, C=3.5e-5, fs=fs)

def RC_wdfTest(R, fs):
  return RCLPF(R, C=3.5e-5, Rs=1, fs=fs)

def printFriedmanBassSMatrix(Rx, fs):
  S = Friedman_BeOd_bassWDFScatteringMatrix(Rx, fs, True)
  print(S)

if __name__ == "__main__":
    fs = 44100
    steps = 800
    #fig = plt.figure()
    #ax = fig.add_subplot(111)
    #plot_w_approximations(ax, 10.0, steps)
    #plt.show()
    for i in range(5):
      x = random.random()
      exact = log(x)
      approx = log_approx(x)
      print(str(x) + ": Exact: " + str(exact) + " Approx: " + str(approx))