# 6.3 DMI - Dante Cards

*Chapter 6: DMI Cards — manual pages 232–234*

A DMI-Dante 64@96 DMI card provides 64 input and 64 output channels at 48kHz or 96kHz, along with support for SRC (Sample Rate Conversion). This enables the desk to run at a different sample rate to the Dante network.

![DMI - Dante Cards (manual p.232)](/figures/ref-p232-1.png)

Sample rate conversion can be enabled in the Audio IO panel by enabling ‘Auto SRC’. This will automatically switch on when necessary to convert the sample rate of the desk inputs and outputs to match the Dante network’s sample rate e.g. the Dante network at 96kHz and console structured at 48kHz. SRC will not affect the number of input and output channels that can be routed.

For both Dante cards, all control and configuration of the Dante interface is done externally by the Dante controller software. A separate control computer must be provided to do this.

In S-Series, the Dante network can be set to use the console as the network system clock (in the Dante Controller software) or the Dante card can be selected as the console clock source.

In the picture below, the Dante Controller software displays two DiGiCo DMI Dante devices.

The second device in the list is installed in an QUANTUM 8 and has been manually labelled "DiGiCo QUANTUM 8".

In the Dante Device Config tab the QUANTUM 8 DMI-Dante card must be set to match the QUANTUM 8 sample rate at 48KHz or 96KHz

**Example 1 - Console is Master clock for Dante Network**

In the Dante Clock Status tab, the QUANTUM 8 DMI-Dante card is set to Sync To External and Preferred Master.

This setup enables the DMI-Dante in the QUANTUM 8 to take its Audio Sync Source from the console itself and in turn provide sync to the rest of the Dante network. The console would typically be set as Audio Master in the Main Menu > Audio Sync panel

![DMI - Dante Cards (manual p.232)](/figures/ref-p232-2.png)

![DMI - Dante Cards (manual p.232)](/figures/ref-p226-1.png)

**Example 2 - Dante Network is Master clock for console**

If the console is required to use the Dante network as its sync source the following settings should be applied.

Enable Sync to External = OFF

![DMI - Dante Cards (manual p.233)](/figures/ref-p233-1.png)

![DMI - Dante Cards (manual p.233)](/figures/ref-p233-2.png)

Sync To External = OFF

Console External DMI Sync

6.4 DMI - ADC - DAC - MIC - AES Cards
