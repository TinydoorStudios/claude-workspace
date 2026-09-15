# 2.3 DMI - Dante Cards

*DMI Cards — manual pages 47–48*

A DMI-Dante card in a QUANTUM 2 console provides 64 input and 64 output channels at 48kHz and 32 input and 32 output channels at 96kHz. It is provided with Primary and Secondary (backup) Gigabit Ethernet ports for connection to the Dante network.

![DMI-Dante card rear panel: Primary and Secondary Dante Ethernet ports](/figures/gs-p047-1.png)

A DMI-Dante 64@96 DMI card provides 64 input and 64 output channels at 48kHz or 96kHz, along with support for SRC (Sample Rate Conversion). This enables the desk to run at a different sample rate to the Dante network.

![DMI-Dante 64@96 card rear panel: Control port plus Primary and Secondary Dante Ethernet ports](/figures/gs-p047-2.png)

Sample rate conversion can be enabled in the Audio IO panel by enabling 'Auto SRC'. This will automatically switch on when necessary to convert the sample rate of the desk inputs and outputs to match the Dante network's sample rate, e.g. the Dante network at 96kHz and console structured at 48kHz. SRC will not affect the number of input and output channels that can be routed. For both Dante cards, all control and configuration of the Dante interface is done externally by the Dante controller software. A separate control computer must be provided to do this. In S-Series, the Dante network can be set to use the console as the network system clock (in the Dante Controller software) or the Dante card can be selected as the console clock source. In the picture below, the Dante Controller software displays two DiGiCo DMI Dante devices. The second device in the list is installed in an QUANTUM 2 and has been manually labelled "DiGiCo QUANTUM 2". In the Dante Device Config tab the QUANTUM 2 DMI-Dante card must be set to match the QUANTUM 3 sample rate at 48KHz or 96KHz.

**Example 1 - Console is Master clock for Dante Network**

In the Dante Clock Status tab, the QUANTUM 2 DMI-Dante card is set to Sync To External and Preferred Master. This setup enables the DMI-Dante in the QUANTUM 2 to take its Audio Sync Source from the console itself and in turn provide sync to the rest of the Dante network. The console would typically be set as Audio Master in the Main Menu > Audio Sync panel.

![Dante Controller Network View, Master Clock tab: Preferred Master and Sync To External set on the QUANTUM 2's Dante device, with the console's own Audio Sync panel set to Master](/figures/gs-p047-3.png)

**Example 2 - Dante Network is Master clock for console**

If the console is required to use the Dante network as its sync source the following settings should be applied. Enable Sync to External = OFF.

![Dante Controller Network View, Clock Status tab: Enable Sync To External unchecked on the master device](/figures/gs-p048-1.png)

![Console Audio Sync panel with DMI 1 selected as the external sync source](/figures/gs-p048-2.png)
