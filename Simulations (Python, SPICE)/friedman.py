from wdf import *
from wdf_nonlinear import DiodeClipperPair
from filters import *
from math import sqrt

def Friedman_BeOd_tightCoeffs(Rx, fs):
  return passiveRCBPFCoeffs(Rx + 4700, 10e-9, 10000, 1e-9, fs)

def Friedman_BeOd_bassCoeffs(Rx, fs):
    R = 33000
    C1 = 22e-9
    Cc = 220e-9
    k = 2*fs
    wA = 1/(math.sqrt(R*C1*Cc*(R + 2*Rx)))
    Q = 1/(wA*(2*R*C1 + Rx*Cc))
    wD = k*math.atan(wA/k)
    aK2 = (k**2)/(wD**2)
    bK = k/(Q*wA)
    gK = k*R*Cc
    d = aK2 + bK + 1
    G = gK/d
    p = (2-2*aK2)/d
    r = (aK2 - bK + 1)/d
    B0 = 1 + G
    B1 = p
    B2 = r-G
    A0 = 1
    A1 = B1
    A2 = r
    return ([B0, B1, B2], [A0, A1, A2])

def Friedman_BeOd_tightWDF(_Rx, fs, steps = 2000):
  input = np.zeros(steps)
  input[0] = 1 # delta function
  output = np.zeros(steps)

  C1 = Capacitor(10e-9, fs=fs)
  C2 = Capacitor(1e-9, fs=fs)
  R1 = Resistor(4.7e+3)
  R2 = Resistor(10e+3)
  Rx = Resistor(_Rx)

  # port resistances [to_parent, to_left_child, to_right_child]
  Rp_S1 = [0, 0, 0]
  Rp_S2 = [0, 0, 0]
  Rp_S3 = [0, 0, 0]
  Rp_P1 = [0, 0, 0]

  # series port 3
  Rp_S3[2] = C2.Rp
  Rp_S3[1] = R2.Rp
  Rp_S3[0] = Rp_S3[1] + Rp_S3[2]
  
  # series port 2
  Rp_S2[2] = Rx.Rp
  Rp_S2[1] = R1.Rp
  Rp_S2[0] = Rp_S2[1] + Rp_S2[2]

  # parallel port 
  Rp_P1[2] = Rp_S3[0]
  Rp_P1[1] = Rp_S2[0]
  Rp_P1[0] = 1/((1/Rp_P1[1]) + (1/Rp_P1[2]))

  # series port 1 (including voltage source)
  Rp_S1[2] = Rp_P1[0]
  Rp_S1[1] = C1.Rp
  Rp_S1[0] = Rp_S1[1] + Rp_S1[2]

  V1 = ResistiveVoltageSource(Rp_S1[0])

  a_S1 = [0, 0, 0]
  a_S2 = [0, 0, 0]
  a_S3 = [0, 0, 0]
  a_P1 = [0, 0, 0]
  b_S1 = [0, 0, 0]
  b_S2 = [0, 0, 0]
  b_S3 = [0, 0, 0]
  b_P1 = [0, 0, 0]

  for i in range(steps):
    # gather incident waves from child leaves
    # for resistors this resets a to zero
    a_S2[1] = R1.get_reflected_wave(b_S2[1])
    a_S2[2] = Rx.get_reflected_wave(b_S2[2])
    a_S3[1] = R2.get_reflected_wave(b_S3[1])
    a_S3[2] = C2.get_reflected_wave(b_S3[2])
    a_S1[1] = C1.get_reflected_wave(b_S1[1])

    #wave up S2 and S3
    b_S2 = series_adaptor(a_S2, Rp_S2)
    b_S3 = series_adaptor(a_S3, Rp_S3)

    # up parallel adaptor
    a_P1[2] = b_S3[0]
    a_P1[1] = b_S2[0]
    b_P1 = parallel_adaptor(a_P1, Rp_P1)

    # up series adaptor S1
    a_S1[2] = b_P1[0]
    b_S1 = series_adaptor(a_S1, Rp_S1)

    # wave down from root (voltage source)
    a_S1[0] = V1.get_reflected_wave(b_S1[0], input[i])
    
    # down S1
    b_S1 = series_adaptor(a_S1, Rp_S1)

    # down P1
    a_P1[0] = b_S1[2]
    b_P1 = parallel_adaptor(a_P1, Rp_P1)

    # down S2 and S3
    a_S2[0] = b_P1[1]
    b_S2 = series_adaptor(a_S2, Rp_S2)
    a_S3[0] = b_P1[2]
    b_S3 = series_adaptor(a_S3, Rp_S3)

    # output
    output[i] = C2.wave_to_voltage()

    # set incident waves. For resistors, b=0 regardless of incident wave a
    C1.set_incident_wave(b_S1[1])
    C2.set_incident_wave(b_S3[2])
  return output

class Friedman_BeOd_BassDelta1(WDFOnePort): # horizontal
  def __init__(self, Rx, fs=44100):
    Ra = 33000
    C = 220e-9
    WDFOnePort.__init__(self)
    self.Rp = 2*Ra + Ra*Ra/(Rx + 1/(2*C*fs))
    den = Ra*Ra + (2*Ra + self.Rp)*(Rx + 1/(2*C*fs))
    self.B2 = 2*Ra*(Rx - 1/(2*C*fs))/den
    self.B1 = -(Ra*Ra + 4*Ra*Rx + self.Rp*(Rx + 1/(2*C*fs)))/den
    self.A2 = self.B2
    self.A1 = (Ra*Ra + 4*Ra*Rx - self.Rp*(Rx + 1/(2*C*fs)))/den
    self.a_prev = 0 # a[n-2]
    self.b_prev = 0 # b[n-2]

  def get_reflected_wave(self, a):
    b_next = self.A1*self.a + self.A2*self.a_prev - self.B1*self.b - self.B2*self.b_prev
    self.a_prev = self.a
    self.b_prev = self.b
    self.a = a
    self.b = b_next
    return self.b

  def set_incident_wave(self, a):
    self.a_prev = self.a
    self.a = a

class Friedman_BeOd_BassDelta2(WDFOnePort): # vertical 
  def __init__(self, Rx, fs=44100):
    Ra = 33000
    C = 220e-9
    WDFOnePort.__init__(self)
    self.Rp = Ra + 2*(Rx + 1/(2*C*fs))
    self.B1 = -(2*Ra + 4*Rx)/(2*Ra + 4*(Rx + 1/(2*C*fs)))
    self.A1 = 1/(C*fs*(2*Ra + 4*(Rx + 1/(2*C*fs))))

  def get_reflected_wave(self, a):
    b_prev = self.b # for better visual understanding
    self.b = self.A1*self.a - self.B1*b_prev
    self.a = a
    return self.b

  def set_incident_wave(self, a):
    self.a=a

def Friedman_BeOd_bassWDFScatteringMatrix(Rx, fs, is_root=True):
  C1 = 22e-9
  C2 = 220e-9
  Rb = 1.0/(2*fs*C1)
  Rd = 33000
  Rf = Rx + 1.0/(2*fs*C2)

  print(Rb)
  print(Rf)

  if is_root:
    d = Rb*Rf + 66000*Rf + 1089000000
    S = np.array([
      [1, 0, 0, 0, 0, 0],
      [-66000*Rb/d, (-Rb*Rf + 66000*Rf + 1089000000)/d, -2*Rb*(Rf + 33000)/d, -2*Rb*Rf/d, 0, 66000*Rb/d],
      [-2178000000/d, -66000*Rf/d, (Rb*Rf - 1089000000)/d, -66000*Rf/d, 0, 2178000000/d],
      [66000*(Rb + 33000)/d, -(66000*Rf + 2178000000)/d, 66000*(Rb - Rf)/d, (Rb*Rf - 1089000000)/d, 0, -(66000*Rb + 2178000000)/d],
      [2*(Rb*Rf + 33000*Rb + 66000*Rf + 1089000000)/d, -(132000*Rf + 2178000000)/d, 2*Rb*(Rf + 33000)/d, 2*Rb*Rf/d, -1, -66000*Rb/d],
      [2*Rf*(Rb + 66000)/d, -66000*Rf/d, 2*Rf*(Rb + 33000)/d, -66000*Rf/d, 0, (-Rb*Rf - 66000*Rf + 1089000000)/d]
    ])
  else:
    d1 = Rb + Rd
    d2 = Rf*d1
    d3 = Rd + Rf
    d4 = d2*d3
    S = np.array([
      [1, 0, 0, 0, 0, 0],
      [-Rb*Rd/d2, Rd/d1, -Rb*(Rd+Rf)/d2, -Rb/d1, 0, Rb*Rd/d2],
      [-Rd/d3, -Rf/d3, 0, -Rf/d3, 0, Rd/d3],
      [Rd*(Rb*d3 + d2)/d4, -Rd*(Rb + 2*Rd + Rf)/(d1*d3), Rd*(Rb-Rf)/d2, (Rb*Rf - (Rd**2))/(Rd**2 + Rb*Rd + Rb*Rf + Rd*Rf), 0, -Rd*(Rb*d3 + d2)/d4],
      [(Rb*Rd + 2*Rb*Rf + 2*Rd*Rf)/d2, -(Rb + 2*Rd)/d1, Rb*(Rd+Rf)/d2, Rb/d1, -1, -Rb*Rd/d2],
      [(Rd+2*Rf)/d3, -Rf/d3, 1, -Rf/d3, 0, -Rf/d3]
    ])
  return S

def Friedman_BeOd_GainStage2_WDF(_Rx, fs=44100, steps=2**14):
  input = np.zeros(steps)
  input[0] = 1.0 #delta function
  output = np.zeros(steps)

  V1 = ResistiveVoltageSource(22e+3)
  C1 = Capacitor(100e-9,fs)

  I1 = ResistiveCurrentSource(_Rx)
  C2 = Capacitor(47e-12)
  D = DiodeClipperPair(1/((1/C2.Rp) + (1/I1.Rp)))

  b_S = [0, 0]
  a_S = [0, 0]
  Rp_S = [C1.Rp, V1.Rp]

  b_P = [0, 0, 0]
  a_P = [0, 0, 0]
  Rp_P = [D.Rp, C2.Rp, I1.Rp]

  for i in range(steps):
    Vin = input[i]
    a_S[0] = C1.get_reflected_wave(b_S[0])
    a_S[1] = V1.get_reflected_wave(b_S[1], Vin)
    b_S = series_adaptor(a_S, Rp_S)

    # wave-current equation
    Is = (V1.a - V1.b)/(2*V1.Rp)

    a_P[2] = I1.get_reflected_wave(a_P[2], Is)
    a_P[1] = C2.get_reflected_wave(b_P[1])
    b_P = parallel_adaptor(a_P, Rp_P)
    #root reflection
    a_P[0] = D.get_reflected_wave(b_P[0])
    b_P = parallel_adaptor(a_P, Rp_P)

    output[i] = Vin + I1.wave_to_voltage()

    C1.set_incident_wave(b_S[0])
    C2.set_incident_wave(b_P[1])
  return output

def Friedman_BeOd_bassWDF(_Rx, fs=44100, steps=2**14):
  input = np.zeros(steps)
  input[0] = 1.0 # delta function
  output = np.zeros(steps)
  # construct
  ''' circuit is a non-inverting op-amp structure '''
  # v+ sub-circuit (here is just a voltage source)
  # in fact, I think it might just be the input (Rp plays no role here I don't think?)

  S = Friedman_BeOd_bassWDFScatteringMatrix(_Rx, fs, True)
  C1_value = 22e-9
  C2_value = 220e-9
  Rb = 1.0/(2*fs*C1_value)
  Rd = 33000
  Rf = _Rx + 1.0/(2*fs*C2_value)

  Rp_Root = Rf*(Rb+Rd)/(Rd+Rf)

  Vin = ResistiveVoltageSource(1)
  RL = Resistor(1) #load resistor
  C1 = Capacitor(C1_value,fs)
  R1 = Resistor(33000) #RootResistor(Rd, Rp_Root)
  R2 = Resistor(Rd)
  R3 = Resistor(_Rx)
  C2 = Capacitor(C2_value,fs)

  Rp_S = [C2.Rp + R3.Rp, C2.Rp, R3.Rp]
  a_S = [0, 0, 0]
  b_S = [0, 0, 0]

  # C1, Vin, R1, R2, RL, S(eries adaptor)
  b_R = [0, 0, 0, 0, 0, 0]
  a_R = [0, 0, 0, 0, 0, 0]

  for i in range(steps):
    a_S[1] = C2.get_reflected_wave(b_S[1])
    a_S[2] = R3.get_reflected_wave(b_S[2])
    b_S = series_adaptor(a_S, Rp_S)

    a_R[5] = b_S[0]
    a_R[4] = RL.get_reflected_wave(b_R[4])
    a_R[3] = R2.get_reflected_wave(b_R[3])
    a_R[2] = R1.get_reflected_wave(b_R[2])
    a_R[1] = C1.get_reflected_wave(b_R[1])
    a_R[0] = Vin.get_reflected_wave(b_R[0], input[i])


    #scattering matrix for R-type adaptor
    b_R = np.dot(S, a_R)

    a_S[0] = b_R[5]
    b_S = series_adaptor(a_S, Rp_S)
  
    output[i] = RL.wave_to_voltage()

    C1.set_incident_wave(b_R[1])
    C2.set_incident_wave(b_S[1])

  return output