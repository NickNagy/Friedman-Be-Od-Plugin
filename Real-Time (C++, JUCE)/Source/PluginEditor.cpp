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
    setSize (width, height);

    bassSlider.setSliderStyle(juce::Slider::Rotary);
    bassSlider.setTextBoxStyle(juce::Slider::NoTextBox, true, 0, 0);
    bassSlider.setColour(juce::Slider::thumbColourId, juce::Colours::white);
    bassSlider.setColour(juce::Slider::rotarySliderFillColourId, juce::Colours::lightgrey);

    bassLabel.setText("Bass", juce::dontSendNotification);
    bassLabel.setColour(juce::Label::textColourId, juce::Colours::gold);
    bassLabel.setJustificationType(juce::Justification::centred);

    addAndMakeVisible(bassSlider);
    addAndMakeVisible(bassLabel);
}

FriedmanBeodPluginAudioProcessorEditor::~FriedmanBeodPluginAudioProcessorEditor()
{
}

//==============================================================================
void FriedmanBeodPluginAudioProcessorEditor::paint (juce::Graphics& g)
{
    g.fillAll (juce::Colours::black);

    //border
    //g.setColour(juce::Colours::gold);

    //bass slider

}

void FriedmanBeodPluginAudioProcessorEditor::resized()
{
    auto area = getBounds();

    //auto innerArea = (area.getWidth() - 2 * borderThickness) * (area.getHeight() - 2 * borderThickness)/(area.getWidth()*area.getHeight());
    //area = area.getProportion(juce::Rectangle<float>(innerArea, innerArea, innerArea, innerArea));

    auto sliderBoxArea = area.removeFromTop(sliderBoxHeight);
    //bass slider
    bassSlider.setBounds(sliderBoxArea.getX(), sliderBoxArea.getY() + sliderOffsetFromTopBorder, rotaryDiameter, rotaryDiameter);
    bassLabel.setBounds(sliderBoxArea.getX(), bassSlider.getY() + rotaryDiameter, rotaryDiameter, sliderTextBoxHeight);
}
