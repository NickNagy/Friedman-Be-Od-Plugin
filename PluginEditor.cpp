/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin editor.

  ==============================================================================
*/

#include "PluginProcessor.h"
#include "PluginEditor.h"

//==============================================================================
FriedmanBeodPluginAudioProcessorEditor::FriedmanBeodPluginAudioProcessorEditor (FriedmanBeodPluginAudioProcessor& p, juce::AudioParameterFloat* bassParam)
    : AudioProcessorEditor (&p), audioProcessor (p), bassSliderAttachment(*bassParam, bassSlider)
{
    // Make sure that before the constructor has finished, you've set the
    // editor's size to whatever you need it to be.
    setSize (400, 300);

    bassSlider.setSliderStyle(juce::Slider::Rotary);
    addAndMakeVisible(bassSlider);
}

FriedmanBeodPluginAudioProcessorEditor::~FriedmanBeodPluginAudioProcessorEditor()
{
}

//==============================================================================
void FriedmanBeodPluginAudioProcessorEditor::paint (juce::Graphics& g)
{
    // (Our component is opaque, so we must completely fill the background with a solid colour)
    g.fillAll (getLookAndFeel().findColour (juce::ResizableWindow::backgroundColourId));

    g.setColour (juce::Colours::white);
    g.setFont (15.0f);
    g.drawFittedText ("Hello World!", getLocalBounds(), juce::Justification::centred, 1);
}

void FriedmanBeodPluginAudioProcessorEditor::resized()
{
    
}
