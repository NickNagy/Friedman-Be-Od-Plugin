/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin editor.

  ==============================================================================
*/

#pragma once

#include <JuceHeader.h>
#include "PluginProcessor.h"

//==============================================================================
/**
*/
class FriedmanBeodPluginAudioProcessorEditor  : public juce::AudioProcessorEditor
{
public:
    FriedmanBeodPluginAudioProcessorEditor(FriedmanBeodPluginAudioProcessor&, juce::AudioParameterFloat *bassParam);
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

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (FriedmanBeodPluginAudioProcessorEditor)
};
