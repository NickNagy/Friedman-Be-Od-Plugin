from matplotlib import pyplot as plt
import numpy as np
from zplots import *

# expects Y to be shape (num_samples, num_lines), and x of shape (num_samples), if provided
def plot_samples(axis, samples, labels=None, title="", x=None):
  num_lines = np.shape(samples)[1] #couldn't think of a better variable name
  if x is None:
    x = range(len(samples[0]))
  print(np.shape(x))
  print(np.shape(samples[:,0]))
  if labels is not None:
    for i in range(num_lines):
      axis.plot(x, samples[:,i], label=labels[i])
  else:
    for i in range(num_lines):
      axis.plot(x, samples[:,i])
  handles,labels = axis.get_legend_handles_labels()
  axis.legend(handles,labels)