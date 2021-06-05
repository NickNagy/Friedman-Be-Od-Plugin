# WDF Tutorial: Diodes and R-Type Adaptors

If you are new to Wave Digital Filters, I recommend Olafur Bogason's [Jupyter Notebook Tutorial](https://github.com/multivac61/wave_digital_notebook/blob/master/WDFs_in_circuit_emulation.ipynb). It is an easy-to-follow introduction to linear WDF elements and series and parallel adaptors, and includes examples in Python. Save from some adjustments (like adding a sample frequency field to Inductor and Capacitor objects), I use a lot of his code directly in this folder.
I am treating this tutorial as a continuation of everything brought up in his Notebook, and jumping right in to the topics that have yet to be covered that are essential in understanding how this guitar pedal is simulated with WDFs.

## Operational Amplifiers

### WDF Operational Amplifiers

## Non-linearities

Resistors, capacitors and inductors all share a common trait of being linear elements. Any system comprised of only these three elements will scale or phase-shift a signal, but every part of the signal will be scaled or phase-shifted as every other part of the signal.
Distortion is an inherently non-linear phenomenon, since... well, you're *distorting* the signal. That is to say, different parts of the signal are being affected in different ways from each other.

### Wave Digital Non-linearities

### Diodes

### WDF Diodes

#### Singular

#### Anti-parallel Pair

## Arbitrary Wave Digital Adaptors: R-Type

Introduced previously 

## References
