#pragma once

#include "../../rt-wdf_lib/Libs/rt-wdf/rt-wdf.h"

class FriedmanBeOdBassWdf : public wdfTree {
public:
	FriedmanBeOdBassWdf(){
		treeSampleRate = 44100;
		// param
		paramData bassParam;
		bassParam.name = "Bass";
		bassParam.ID = 0;
		bassParam.type = doubleParam;
		bassParam.value = 0.0001;
		bassParam.units = "";
		bassParam.lowLim = 0.0001;
		bassParam.highLim = 0.9999;
		params[0] = bassParam;
		// elements
		Vin.reset(new wdfTerminatedResVSource(0, VinR_value));
		R1.reset(new wdfTerminatedRes(R1_value));
		R2.reset(new wdfTerminatedRes(R1_value));
		C1.reset(new wdfTerminatedCap(C1_value, treeSampleRate));
		RL.reset(new wdfTerminatedRes(VinR_value));
		Rx.reset(new wdfTerminatedRes(0.0));
		C2.reset(new wdfTerminatedCap(C2_value, treeSampleRate));
		// adapters
		S.reset(new wdfTerminatedSeries(C2.get(), Rx.get()));
		// subtree
		subtreeCount = 6;
		subtreeEntryNodes = new wdfTreeNode * [subtreeCount];
		subtreeEntryNodes[0] = Vin.get();
		subtreeEntryNodes[1] = C1.get();
		subtreeEntryNodes[2] = R1.get();
		subtreeEntryNodes[3] = R2.get();
		subtreeEntryNodes[4] = RL.get();
		subtreeEntryNodes[5] = S.get();
		// root
		root.reset(new wdfRootRtype(subtreeCount));	
		Rp = new double[subtreeCount];
	}

	int setRootMatrData(matData* rootMats, double* Rp) {
		if (rootMats->Smat.is_empty()) {
			return -1;
		}
		if (rootMats->Smat.n_cols != subtreeCount) {
			return -1;
		}
		if (rootMats->Smat.n_rows != subtreeCount) {
			return -1;
		}
		double S_Rp = S->calculateUpRes(treeSampleRate);
		double C1_Rp = C1->calculateUpRes(treeSampleRate);

		// denominator
		auto R1t2 = R1_value*2;
		auto R1sq = R1_value*R1_value;
		auto R1sqt2 = R1sq * 2;
		double den = S_Rp * C1_Rp * R1t2 * S_Rp + R1sq;

		// common fractions
		double commonFrac1 = R1t2 * C1_Rp / den;
		double commonFrac2 = R1t2 * S_Rp / den;
		double commonFrac3 = 2 * C1_Rp * (S_Rp + R1_value) / den;
		double commonFrac4 = 2 * C1_Rp * S_Rp / den;
		double commonFrac5 = R1sqt2 / den;

		// scattering matrix
		double S[6][6] = {
			{1.0, 0.0, 0.0, 0.0, 0.0, 0.0},
			{-commonFrac1, (-S_Rp * C1_Rp + R1t2 * S_Rp + R1sq) / den, -commonFrac3, -commonFrac4, 0.0, commonFrac1},
			{-commonFrac5, -commonFrac2, (C1_Rp * S_Rp - R1sq) / den, -commonFrac2, 0.0, commonFrac5},
			{R1t2 * (C1_Rp + R1_value) / den, -(R1t2 * S_Rp + R1sqt2) / den, R1t2 * (C1_Rp - S_Rp) / den, (C1_Rp * S_Rp - R1sq) / den, 0.0, -(R1t2 * C1_Rp + R1sqt2) / den},
			{2 * (C1_Rp * S_Rp + R1_value * C1_Rp + R1t2 * S_Rp + R1sq) / den, -(2 * R1t2 * S_Rp + R1sqt2) / den, commonFrac3, commonFrac4, -1.0, -commonFrac1},
			{2 * S_Rp * (C1_Rp + R1t2) / den, -commonFrac2, 2 * S_Rp * (C1_Rp + R1_value) / den , -commonFrac2, 0.0, (-C1_Rp * S_Rp + -R1t2 * S_Rp + R1sq) / den}
		};

		for (unsigned int ii = 0; ii < 6; ++ii) {
			for (unsigned int jj = 0; jj < 6; ++jj) {
				rootMats->Smat.at(ii, jj) = S[ii][jj];
			}
		}
		return 0;
	}

	void setSamplerate(double fs) {
		C1.reset(new wdfTerminatedCap(C1_value, fs));
		C2.reset(new wdfTerminatedCap(C2_value, fs));
		adaptTree();
		treeSampleRate = fs;
	}

	~FriedmanBeOdBassWdf() override;

	// set signal on Vin
	void setInputValue(double signalIn) {
		Vin->Vs = signalIn;
	}

	// get voltage out across load resistor
	double getOutputValue() {
		return RL->upPort->getPortVoltage();
	}

	const char* getTreeIdentifier() override { return treeName.c_str(); }

	// paramValue in range of 0.0 to 1.0
	void setParam(size_t paramID, double paramValue) override {
		if (paramID == 0) {
			// bass circuit dial is inverted (when Rx is max, bass-boost is minimized)
			double trueParamValue = 1.0 - paramValue;
			Rx->R = trueParamValue * Rx_max;
			adaptTree();
			params[0].value = trueParamValue;
		}
	}

private:
	const float C1_value = 22e-9;
	const float C2_value = 220e-9;
	const float R1_value = 33000.0;
	const float Rx_max = 100000.0;
	const float VinR_value = 1.0;

	std::unique_ptr<wdfTerminatedResVSource> Vin;
	std::unique_ptr<wdfTerminatedRes> R1; // reflection
	std::unique_ptr<wdfTerminatedRes> R2;
	std::unique_ptr<wdfTerminatedCap> C1;
	std::unique_ptr<wdfTerminatedRes> RL; // load resistor
	std::unique_ptr<wdfTerminatedRes> Rx; // variable resistor
	std::unique_ptr<wdfTerminatedCap> C2;

	std::unique_ptr<wdfTerminatedSeries> S;

	std::string treeName = "Bass Control Circuit";
};