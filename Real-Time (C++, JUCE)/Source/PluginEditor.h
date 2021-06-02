/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin editor.

  ==============================================================================
*/

#pragma once

#include <JuceHeader.h>
#include "PluginProcessor.h"

#define SCALE 50 // scale dimensions (in cm) by whatever this number is

//==============================================================================
/**
*/
class FriedmanBeodPluginAudioProcessorEditor  : public juce::AudioProcessorEditor
{
public:
    FriedmanBeodPluginAudioProcessorEditor(FriedmanBeodPluginAudioProcessor&, juce::AudioParameterFloat* bassParam);
    ~FriedmanBeodPluginAudioProcessorEditor() override;

    //==============================================================================
    void paint (juce::Graphics&) override;
    void resized() override;

private:
    // This reference is provided as a quick way for your editor to
    // access the processor object that created it.
    FriedmanBeodPluginAudioProcessor& audioProcessor;

    juce::Slider bassSlider;
    juce::SliderParameterAttachment bassSliderAttachment;

    juce::Label bassLabel;

    /* dimensions (taken in cm from original pedal) */
    float height = 12*SCALE;
    float width = 6.5*SCALE;
    float borderWidth = 5.8*SCALE;
    float borderHeight = 11.5*SCALE;
    float borderThickness = 0.3*SCALE;
    float rotaryDiameter = 1.5*SCALE;
    float sliderBoxHeight = 6*SCALE;
    float sliderOffsetFromTopBorder = 0.5 * SCALE;
    float sliderTextBoxHeight = 0.5 * SCALE;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (FriedmanBeodPluginAudioProcessorEditor)
};
