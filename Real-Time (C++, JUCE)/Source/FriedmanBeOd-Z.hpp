#pragma once

#include <math.h>

// passive RC BPF
//
double secondOrderRCBPF(double R1_value, double R2_value, double C1_value, double C2_value, double fs) {
	auto wA = 1.0 / sqrt(R1_value * C1_value * R2_value * C2_value); // analog frequency
	auto k = 2 * fs;
	auto wD = k * atan(wA / k); // digital (pre-warped) frequency
	auto ak2 = k * k / (wD * wD);
	auto bk = k * (C1_value * R1_value + C2_value * (R1_value + R2_value));
	auto gk = C1_value * R1_value * k;
	auto den = ak2 + bk + 1;
	// TODO
	return 1.0;
}

// Some virtual base classes
class FriedmanBeOdZ {
public:
	FriedmanBeOdZ() {}
	virtual ~FriedmanBeOdZ() {}

	virtual void reset();
	virtual float processSample(float xn);

	void setSampleRate(double fs) { sampleRate = fs; }
protected:
	double sampleRate = 44100;
};

class FriedmanBeOdZTunable : public FriedmanBeOdZ {
public:
	void setTunableValue(double nextValue) {
		tunableValue = nextValue;
		computeCoefficients();
	}
protected:
	double tunableValue = 1;
	virtual void computeCoefficients();
};

// Tight Circuit
class FriedmanBeOdTightZ : public FriedmanBeOdZTunable {
public:
	FriedmanBeOdTightZ() {}
	~FriedmanBeOdTightZ() override {}

	void setTightValue(double tightParamValue) {
		setTunableValue(tightParamValue);
	}

	float processSample(float xn) override {

	}
private:
	void computeCoefficients() override {

	}
};

// Bass Circuit
class FriedmanBeOdBassZ : public FriedmanBeOdZTunable {
public:
	FriedmanBeOdBassZ() {}
	
	~FriedmanBeOdBassZ() override {}

	void reset() override {
		// clear memory
		xHistory[0] = 0;
		xHistory[1] = 0;
		yHistory[0] = 0;
		yHistory[1] = 0;
	}

	void setBassValue(double bassParamValue) {
		setTunableValue((1.0 - bassParamValue) * Rx);
	}

	float processSample(float xn) override {
		float yn = b0 * xn + b1 * xHistory[0] + b2 * xHistory[1] - a1 * yHistory[0] - a2 * yHistory[1];
		xHistory[1] = xHistory[0];
		xHistory[0] = xn;
		yHistory[1] = yHistory[0];
		yHistory[0] = yn;
		return yn;
	}

private:
	void computeCoefficients() override {
		auto k = 2 * sampleRate;
		auto wA = 1.0 / (sqrt((double)R1 * C1 * C2 * (R1 + 2 * tunableValue))); // analog frequency
		auto Q = 1.0 / (wA * (2 * (double)R1 * C1 + C2 * tunableValue));
		auto wD = k * atan(wA / k); // digital (pre-warped) frequency
		auto ak2 = k * k / (wD * wD);
		auto bk = k / (Q * wA);
		auto gk = k * R1 * C2;
		auto d = ak2 + bk + 1;
		auto G = gk / d;
		auto p = (2 - 2 * ak2) / d;
		auto r = (ak2 - bk + 1) / d;
		b2 = r - G;
		b1 = p;
		b0 = 1 + G;
		a2 = r;
		a1 = b1;
	}
	// component values
	float R1 = 33000;
	float R2 = 33000;
	float C1 = 22e-9;
	float C2 = 220e-9;
	float Rx = 100000;
	// difference equation coefficients
	float b2 = 1;
	float b1 = 1;
	float b0 = 1;
	float a2 = 1;
	float a1 = 1;
	//float a0 = 1; a0 will always be 1 (normalized)
	float xHistory[2] = { 0, 0 };
	float yHistory[2] = { 0, 0 };
};