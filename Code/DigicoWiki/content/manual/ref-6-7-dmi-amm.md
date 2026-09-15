# 6.7 DMI – AMM

*Chapter 6: DMI Cards — manual pages 238–242*

Quantum 852, Quantum 338 and SD12 are compatible with the DMI-AMM card. The DMI-AMM card automatically manages live microphones in unpredictable dialogue situations. When one person speaks, that microphone’s gain level fades up instantly, while the other microphone gains are reduced. When the speaker pauses, all microphone levels will adjust to medium gain to collectively match the level of one microphone at full gain. The resulting effect will be as if all speakers are sharing one microphone. When several people talk at once, the gain is shared. The AMM Controls (Figure 1) can be found in the Audio I/O window after conforming the DMI card (Figure 2 & 3).

![DMI – AMM (manual p.238)](/figures/ref-p238-1.png)

**Figure 1: AMM Control Window**

Each of the 64 slots within the AMM control panel include a group assign (Group A & Group B) and a weight control. The Floor control of each group imposes a lower limit on the level detector for all microphones assigned to that group, this prevents a noisy microphone from receiving a disproportionate share of gain. The Floor should be left at the default value of -130dB for normal operation.

6.7 DMI – AMM

![DMI – AMM (manual p.239)](/figures/ref-p089-1.png)

**Figure 2: Conform AMM**

![DMI – AMM (manual p.239)](/figures/ref-p090-1.png)

**Figure 3: Open AMM Control**

There are two ways to route channels to the AMM. The first is from within the AMM Control window itself. Touch the white box below each of the slots, this will open the AMM Routing window (Figure 4). Here you can ripple route channels to the AMM, using touch turn to select the desired number of channels. The AMM is automatically assigned a post-fader Insert B. Therefore, AMM can also be assigned in a way that DiGiCo users will be more familiar with, via the Insert B routing window at the bottom of a channel strip (Figure 5).

6.7 DMI – AMM

![DMI – AMM (manual p.240)](/figures/ref-p090-3.png)

**Figure 4: Routing Within AMM Control**

![DMI – AMM (manual p.240)](/figures/ref-p090-2.png)

**Figure 5: Routing via Insert B Routing Menu**

6.7 DMI – AMM

When channels are routed to the AMM and assigned to a group, a Share % bar is seen in yellow on the right side of an AMM slot. This represents the gain Share that the channel is getting when the AMM is active. This meter is shown in terms of percentage, meaning that if 2 speakers stop talking at the same time then they will both get 50% of the gain share. The Weight control allows adjustment of the relative sensitivity on a per channel basis. When weighting controls are balanced (equal), each microphone has an equal opportunity to “take over” the system. Changing the weight will not have an effect on the overall level of the channel, just how easily it can take a share of the gain. Adding weight to one primary microphone ensure that the particular microphone (e.g. a chairperson) will get more of the share of gain (Figure 6).

![DMI – AMM (manual p.241)](/figures/ref-p091-1.png)

**Figure 6: AMM Share Percentage and Weights**

There are a set of master controls available at the bottom of the AMM Control window. These include a Floor control for each AMM group within the card and a safe control. The Floor control imposes a lower limit on the level detector for all microphones assigned to the relevant AMM group. This prevents a noisy microphone from receiving a disproportionate share of gain. The Floor should be left at the default value of -130dB for normal operation. The safe option excludes these floor controls from snapshots.

**Figure 7: AMM Master Controls**

All AMM parameters (both master and channel specific) are saved on a per snapshot basis and can be safed or removed from the global scope. Only input channels can be added to the AMM. It can be saved globally via the Input Devices option in the Global Scope menu on the Snapshots window. This is NOT enabled by default.

6.8 DMI KLANG

![DMI – AMM (manual p.242)](/figures/ref-p091-2.png)

**Figure 8: Global Scope > Input Devices**
