# 1.6 Audio Sync

*The Console — manual pages 22–23*

To access the Audio Sync Panel, touch the Setup Menu button, followed by Audio Sync. The following window will open…

![Audio Synchronisation panel: active sync source set to Master, sample rate, and Example Clocking from Optocore @ 96kHz](/figures/gs-p022-1.png)

The QUANTUM 2 will operate at Sample Rates of either 48000Hz (48kHz) or 96000Hz (96kHz), as configured in the Session Structure panel. By default, it is set to clock internally but, if Optocore is fitted, the standard Audio Sync method is Optocore when the entire system uses the device with the lowest Optocore ID (usually ID1) as its sync source. This setting is saved within the session file so if any console(s) are connected to racks with optical fibre then all console engines should be set to Optocore as their sync source.

There are also times when the QUANTUM 2 needs to be clocked externally. The Audio Sync panel allows you to control external synchronisation. The QUANTUM 2 will clock from the following sources: Word Clock, Waves, MADI, Optocore and relevant DMI cards. In this situation one Optocore device should be set to clock to the external source and all other Optocore devices should be set to sync to Optocore.

Note: When a valid clock is detected on an external sync input, the corresponding Green OK box will light, even if that input is not selected as the clock source for the QUANTUM 2.
