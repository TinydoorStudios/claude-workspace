# 1.7 Rack Connections with MADI

* — manual pages 21–23*

**Single Console to Rack with MADI at 48KHz**

Labels: Rack · Console · Audio Sync = MASTER

![Rack Connections with MADI (manual p.21)](/figures/dq-p021-1.png)

Connect Console MADI BNC IN socket to Rack BNC OUT MAIN socket.

Connect Console MADI BNC OUT socket to Rack BNC IN MAIN socket.

**Single Console to Rack with MADI at 96KHz**

Labels: Rack · Console · Audio Sync = MASTER

![Rack Connections with MADI (manual p.21)](/figures/dq-p021-1.png)

Connect Console MADI BNC IN socket to Rack BNC OUT MAIN socket.

Connect Console MADI BNC OUT socket to Rack BNC IN MAIN socket.

Connect Console MADI BNC IN socket to Rack BNC OUT AUX socket.

DQ & MQ-Rack User Guide

Connect Console MADI BNC OUT socket to Rack BNC IN AUX socket.

**Sharing Racks with MADI**

If the system is running at a sample rate of 48KHz a D2-Rack, SD-Rack, SD-MINIRack or MQ Rack can be shared between 2 consoles (Two QUANTUM 2s or a QUANTUM 2 and another Quantum or SD-Series console) with the connection system shown below.

In this setup:

1) All inputs can be shared by the two consoles but only one console controls the rack analogue gains (the "Master" console)

2) The console which is not controlling the gains (the "Slave" console) can automatically adjust its digital trims to compensate for the gain changes using a system known as "Gain Tracking" (see below)

3) Only the "Master" console can use the outputs of the shared rack

The recommended connection between the Monitor (Slave) console and Stage Rack is a single MADI OUT from the Shared Rack's AUX MADI connected to the console's MADI A IN

The FOH (Master console) is connected via MADI A IN and OUT to the stage rack.

A similar method can be used if the Monitor console requires gain control and the FOH console will track the gain changes.

MADI OUT from the Shared Rack's AUX MADI connected to the FOH console's MADI A IN.

The Monitor (Master console) is connected via MADI A IN and OUT to the stage rack.

Note: The "Master" console should be set to provide "Master Sync" (Setup>Audio Sync menu - see diagram below) to the Shared rack

The "Slave" console should be set to receive its Audio Sync from the MADI slot that is connected to the Shared Rack.

1) The operators should agree on and set a level of analogue gain that provides enough headroom for the required application.

2) The second console should connect to the Shared rack in Receive Only mode (only MADI Input cable connected)

3) Gain Tracking (the GT ON/OFF button at the top of the Input channel setup view) can be switched on for the console that is in "Receive Only" mode for all the channels that are being shared.

4) When an analogue gain control is changed on the "Master" console, the "Slave" console's analogue gain should reflect the changes and the digital trim control should compensate for this change by moving by the same amount in the opposite direction.

IMPORTANT Note: If Gain Tracking is active on a channel, the digital trim control will still respond to the local gain adjustment by compensating locally for the displayed gain change.

If the "Slave" console loads a session where the Analogue Gain and +48V settings do not match the current state of the racks, the Master console should then reload its session to update the state of these controls on the "Slave" console

DQ & MQ-Rack User Guide

**FOH & MONITORS WITH SHARED RACK at 48KHz USING MADI**

Labels: Shared Rack · Console 2 · MONITORS · Console 1 · Audio Sync = MADI IN

![Rack Connections with MADI (manual p.23)](/figures/dq-p023-1.png)

FOH

Audio Sync = MASTER

![Rack Connections with MADI (manual p.23)](/figures/dq-p023-2.png)
