/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin processor.

  ==============================================================================
*/

#include "PluginProcessor.h"
#include "PluginEditor.h"

//==============================================================================
FriedmanBeodPluginAudioProcessor::FriedmanBeodPluginAudioProcessor()
#ifndef JucePlugin_PreferredChannelConfigurations
     : AudioProcessor (BusesProperties()
                     #if ! JucePlugin_IsMidiEffect
                      #if ! JucePlugin_IsSynth
                       .withInput  ("Input",  juce::AudioChannelSet::stereo(), true)
                      #endif
                       .withOutput ("Output", juce::AudioChannelSet::stereo(), true)
                     #endif
                       )
#endif
{
    prevBassValue = 0.00001;
    addParameter(bassParam = new juce::AudioParameterFloat("bass", "Bass", 0.00001, 0.99999, 0.00001));
    bassWDFLeft.initTree();
    bassWDFRight.initTree();
    //bassZLeft.reset();
    //bassZRight.reset();
}

FriedmanBeodPluginAudioProcessor::~FriedmanBeodPluginAudioProcessor()
{
}

//==============================================================================
const juce::String FriedmanBeodPluginAudioProcessor::getName() const
{
    return JucePlugin_Name;
}

bool FriedmanBeodPluginAudioProcessor::acceptsMidi() const
{
   #if JucePlugin_WantsMidiInput
    return true;
   #else
    return false;
   #endif
}

bool FriedmanBeodPluginAudioProcessor::producesMidi() const
{
   #if JucePlugin_ProducesMidiOutput
    return true;
   #else
    return false;
   #endif
}

bool FriedmanBeodPluginAudioProcessor::isMidiEffect() const
{
   #if JucePlugin_IsMidiEffect
    return true;
   #else
    return false;
   #endif
}

double FriedmanBeodPluginAudioProcessor::getTailLengthSeconds() const
{
    return 0.0;
}

int FriedmanBeodPluginAudioProcessor::getNumPrograms()
{
    return 1;   // NB: some hosts don't cope very well if you tell them there are 0 programs,
                // so this should be at least 1, even if you're not really implementing programs.
}

int FriedmanBeodPluginAudioProcessor::getCurrentProgram()
{
    return 0;
}

void FriedmanBeodPluginAudioProcessor::setCurrentProgram (int index)
{
}

const juce::String FriedmanBeodPluginAudioProcessor::getProgramName (int index)
{
    return {};
}

void FriedmanBeodPluginAudioProcessor::changeProgramName (int index, const juce::String& newName)
{
}

//==============================================================================
void FriedmanBeodPluginAudioProcessor::prepareToPlay (double sampleRate, int samplesPerBlock)
{
    bassWDFLeft.setSamplerate(sampleRate);
    bassWDFRight.setSamplerate(sampleRate);
    bassWDFLeft.adaptTree();
    bassWDFRight.adaptTree();
    //bassZLeft.setSampleRate(sampleRate);
    //bassZRight.setSampleRate(sampleRate);
}

void FriedmanBeodPluginAudioProcessor::releaseResources()
{
    // When playback stops, you can use this as an opportunity to free up any
    // spare memory, etc.
}

#ifndef JucePlugin_PreferredChannelConfigurations
bool FriedmanBeodPluginAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
{
  #if JucePlugin_IsMidiEffect
    juce::ignoreUnused (layouts);
    return true;
  #else
    // This is the place where you check if the layout is supported.
    // In this template code we only support mono or stereo.
    if (layouts.getMainOutputChannelSet() != juce::AudioChannelSet::mono()
     && layouts.getMainOutputChannelSet() != juce::AudioChannelSet::stereo())
        return false;

    // This checks if the input layout matches the output layout
   #if ! JucePlugin_IsSynth
    if (layouts.getMainOutputChannelSet() != layouts.getMainInputChannelSet())
        return false;
   #endif

    return true;
  #endif
}
#endif

void FriedmanBeodPluginAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages)
{
    juce::ScopedNoDenormals noDenormals;
    auto totalNumInputChannels  = getTotalNumInputChannels();
    auto totalNumOutputChannels = getTotalNumOutputChannels();
    auto numSamples = buffer.getNumSamples();
    for (auto i = totalNumInputChannels; i < totalNumOutputChannels; ++i)
        buffer.clear (i, 0, buffer.getNumSamples());

    auto nextBassValue = bassParam->get();
    if (nextBassValue != prevBassValue) {
        bassWDFLeft.setParam(0, (double)nextBassValue);
        bassWDFRight.setParam(0, (double)nextBassValue);
        //bassZLeft.setBassValue((double)nextBassValue);
        //bassZRight.setBassValue((double)nextBassValue);
        prevBassValue = nextBassValue;
    }

    // WDF channel
    auto* leftChannelData = buffer.getWritePointer(0); 
    for (auto i = 0; i < numSamples; i++) {
        bassWDFLeft.setInputValue(double(leftChannelData[i]));
        bassWDFLeft.cycleWave();
        // for debugging purposes
        leftChannelData[i] = (float)bassWDFLeft.getOutputValue();
    }

    // Z channel
    if (totalNumOutputChannels > 1) {
        auto* rightChannelData = buffer.getWritePointer(1);
        for (auto i = 0; i < numSamples; i++) {
            bassWDFRight.setInputValue(double(rightChannelData[i]));
            bassWDFRight.cycleWave();
            rightChannelData[i] = (float)bassWDFRight.getOutputValue();
        }
    }
}

//==============================================================================
bool FriedmanBeodPluginAudioProcessor::hasEditor() const
{
    return true; // (change this to false if you choose to not supply an editor)
}

juce::AudioProcessorEditor* FriedmanBeodPluginAudioProcessor::createEditor()
{
    return new FriedmanBeodPluginAudioProcessorEditor (*this, bassParam);
}

//==============================================================================
void FriedmanBeodPluginAudioProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    // You should use this method to store your parameters in the memory block.
    // You could do that either as raw data, or use the XML or ValueTree classes
    // as intermediaries to make it easy to save and load complex data.
}

void FriedmanBeodPluginAudioProcessor::setStateInformation (const void* data, int sizeInBytes)
{
    // You should use this method to restore your parameters from this memory block,
    // whose contents will have been created by the getStateInformation() call.
}

//==============================================================================
// This creates new instances of the plugin..
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new FriedmanBeodPluginAudioProcessor();
}
