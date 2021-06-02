import numpy as np
from wdf import *
from wdf_nonlinear import DiodeClipperPair

#https://www.electronics-tutorials.ws/filter/filter_5.html
def lowpassOpAmp_WDF(fs=44100, steps=2**14):
  input = np.zeros(steps)
  output = np.zeros(steps)
  input[0] = 1

  # feedback network
  Is = ResistiveCurrentSource(91e+3)
  a_f = 0
  b_f = 0

  # positive input
  Vin = ResistiveVoltageSource(10e+3)
  C = Capacitor(100e-9, fs)
  Rp_pos = [Vin.Rp, C.Rp]
  b_pos = [0, 0]
  a_pos = [0, 0]

  # negative input
  V_neg = ResistiveVoltageSource(1e+3)
  a_neg = 0
  b_neg = 0

  for i in range(steps):
    a_pos[1] = C.get_reflected_wave(b_pos[1])
    a_pos[0] = Vin.get_reflected_wave(b_pos[0], input[i])

    v_C = C.wave_to_voltage()

    b_pos = parallel_adaptor(a_pos, Rp_pos)

    a_neg = V_neg.get_reflected_wave(0, v_C) # there's not even any circuit here?
    
    i_neg = (V_neg.a - V_neg.b)/(2*V_neg.Rp)

    #b_neg = 

    a_f = Is.get_reflected_wave(0, i_neg)

    output[i] = Is.wave_to_voltage() + v_C

    C.set_incident_wave(b_pos[1])
  return output

def capacitiveOpAmp_WDF(fs = 44100, steps=2**14):
  input = np.zeros(steps)
  output = np.zeros(steps)
  input[0] = 1

  # feedback network
  C_f = Capacitor(51e-12, fs)
  Is = ResistiveCurrentSource(500000) #500K-ohm feedback resistance Rf
  Rp_f = [Is.Rp, C_f.Rp]
  a_f = [0, 0]
  b_f = [0, 0]
  
  # positive input
  V_pos = ResistiveVoltageSource(10000)
  C_pos = Capacitor(1e-6, fs)
  Rp_pos = [V_pos.Rp, C_pos.Rp]
  a_pos = [0, 0]
  b_pos = [0, 0]

  # negative input
  C_neg = Capacitor(47e-9, fs)
  V_neg = ResistiveVoltageSource(4.7e+3)
  Rp_neg = [V_neg.Rp, C_neg.Rp]
  a_neg = [0, 0]
  b_neg = [0, 0]

  for i in range(steps):
    '''V+ terminal'''
    a_pos[1] = C_pos.get_reflected_wave(b_pos[1])
    a_pos[0] = V_pos.get_reflected_wave(b_pos[0], input[i])

    # send to V- (and also op amp output)
    v_C_pos = C_pos.wave_to_voltage() + input[i]

    # reflection
    b_pos = series_adaptor(a_pos, Rp_pos)

    '''V- terminal'''
    a_neg[1] = C_neg.get_reflected_wave(b_neg[1])
    a_neg[0] = V_neg.get_reflected_wave(b_neg[0], v_C_pos)

    i_neg = (V_neg.a - V_neg.b)/(2*V_neg.Rp)

    # reflection
    b_neg = series_adaptor(a_neg, Rp_neg)

    '''feedback network'''
    a_f[1] = C_f.get_reflected_wave(b_f[1])
    a_f[0] = Is.get_reflected_wave(b_f[0], i_neg)

    output[i] = v_C_pos + Is.wave_to_voltage()

    # reflection
    b_f = parallel_adaptor(a_f, Rp_f)

    C_f.set_incident_wave(b_f[1])
    C_neg.set_incident_wave(b_neg[1])
    C_pos.set_incident_wave(b_pos[1])

  return output

def nullorBasedBridgedTResonator_WDF(fs=44100, steps=2**14):
  input = np.zeros(steps)
  input[0] = 0.01
  output = np.zeros(steps)

  print("Reminder: scattering matrix is derived specifically from a sample frequency 44.1kHz!")
  fs = 44100

  #https://pureadmin.qub.ac.uk/ws/portalfiles/portal/158209014/1570255463.pdf
  S = np.array([[1.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00],
 [1.00000000e+00, -1.13122172e-03, -1.00000000e+00, 1.13122172e-03,
  -1.13122172e-03, 0.00000000e+00],
 [1.00000000e+00, -9.98868778e-01, 2.22044605e-16, -1.13122172e-03,
   1.13122172e-03, 0.00000000e+00],
 [-8.82000000e+02, 8.82997738e+02, 8.82000000e+02, 2.26244344e-03,
   9.97737557e-01, 0.00000000e+00],
 [-8.83000000e+02, 8.81998869e+02, 8.83000000e+02, 1.00113122e+00,
  -1.13122172e-03, 0.00000000e+00],
 [-8.84000000e+02, 8.82997738e+02, 8.82000000e+02, 1.00226244e+00,
   9.97737557e-01, -1.00000000e+00]])

  Cap_value = 1e-9
  Ra_value = 1
  Rb_value = 1/(2*Cap_value*fs)
  Rc_value = 500
  Rd_value = 10000000
  Re_value = Rb_value
  Rf_value = 10000

  # root element RC = R1
  Rc_port_value = Rb_value*Re_value/(Rb_value + Rd_value + Re_value)
  print(Rc_port_value)

  Vin = ResistiveVoltageSource(Ra_value)
  C1 = Capacitor(Cap_value,fs)
  R1 = RootResistor(Rc_value, Rc_port_value)
  R2 = Resistor(Rd_value)
  C2 = Capacitor(Cap_value,fs)
  RL = Resistor(Rf_value)

  b = [0, 0, 0, 0, 0, 0]
  a = [0, 0, 0, 0, 0, 0]

  for i in range(steps):
    a[5] = RL.get_reflected_wave(b[5])
    a[4] = C2.get_reflected_wave(b[4])
    a[3] = R2.get_reflected_wave(0) # don't care
    a[1] = C1.get_reflected_wave(b[1])
    a[0] = Vin.get_reflected_wave(0, input[i]) # don't care

    # wave-up
    b = np.dot(S, a)
    # root, instantaneous reflection
    a[2] = R1.get_reflected_wave(b[2])
    b = np.dot(S,a) # for finding others

    output[i] = RL.wave_to_voltage()

    C1.set_incident_wave(b[1])
    C2.set_incident_wave(b[4])
  return output

# source: https://www.researchgate.net/profile/Stefano-Dangelo/publication/335464256_Fast_Approximation_of_the_Lambert_W_Function_for_Virtual_Analog_Modelling/links/5d75fbd7299bf1cb8093125e/Fast-Approximation-of-the-Lambert-W-Function-for-Virtual-Analog-Modelling.pdf
def BasicDiodeClipperCircuit_WDF(fs=44100, steps=2**14):
  Vt = 26e-3 #mV
  Is = 0.1e-15
  R1_value = 2.2e+3
  C1_value = 10e-9
  Vin = ResistiveVoltageSource(1)
  R1 = Resistor(R1_value)
  C1 = Capacitor(C1_value, fs)

  # input is two 2V peak-peak sine waves of 110Hz and 150Hz, sampled at 44.1kHz
  input = 2*(np.sin(2*np.pi*np.arange(steps)*110/fs) + np.sin(2*np.pi*np.arange(steps)*150/fs))
  output = np.zeros(steps)

  Rp_S = [Vin.Rp + R1.Rp, Vin.Rp, R1.Rp]
  #adapted so diode is root / reflection-free
  Rp_P = [1/((1/C1.Rp) + (1/Rp_S[0])), C1.Rp, Rp_S[0]]

  # I am not certain that the port-resistance is the proper value for R in the 
  # diode wave-equation
  D = DiodeClipperPair(Rp_P[0], Is, Vt)

  a_S = [0, 0, 0]
  b_S = [0, 0, 0]
  a_P = [0, 0, 0]
  b_P = [0, 0, 0]

  for i in range(steps):
    a_S[1] = Vin.get_reflected_wave(b_S[1], input[i])
    a_S[2] = R1.get_reflected_wave(b_S[2])
    b_S = series_adaptor(a_S, Rp_S)

    a_P[1] = C1.get_reflected_wave(b_P[1])
    a_P[2] = b_S[0]
    b_P = parallel_adaptor(a_P, Rp_P)

    # diode reflection
    a_P[0] = D.get_reflected_wave(b_P[0])

    #wave-down
    b_P = parallel_adaptor(a_P, Rp_P)
    a_S[0] = b_P[2]
    b_S = series_adaptor(a_S, Rp_S)

    output[i] = C1.wave_to_voltage() # not sure if across diode is best choice
    C1.set_incident_wave(b_P[1])
  return output