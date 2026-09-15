# 2.2 DMI-MADI Cards

*DMI Cards — manual pages 42–47*

There are 2 types of DMI-MADI Card:

**MADI B has 2 pairs of BNC connectors**

**MADI C has 2 bi-directional Cat5e connectors**

Both of these cards can be used to connect a Standard MADI stream at 48KHz or 96KHz or an SD-Series DiGiCo Rack with the appropriate connector (D-Rack, D2-Rack, SD-Rack, SD-MiNiRack).

NOTE: Only one DiGiCo Rack can be connected to a single DMI-MADI card at one time. NOTE: With QUANTUM 2 software V14.0.1400+, cable redundancy at 48KHz using both the Main and Aux MADI ports on a D2-Rack, SD-Rack or SD-MINIRack is not implemented

### 2.2.1 Connecting DMI-MADI

External audio connections can be made using either BNC MADI (AES10) or the DiGiCo Cat5e Connection. There are 2 types of MADI connection available. A DiGiCo Stage rack can be connected to a console via a bi-directional MADI connection will have up to 112 channels (56 in, 56 out) of audio plus the control data for the Rack (located on CH57).  A bi-directional standard MADI stream will contain up to 128 channels of Audio (64 in, 64 out) and can be connected to any 3rd party device that has MADI connectivity. A DiGiCo Cat5e connection is a bi-directional up to 64 Channel interface that uses STP Cat5e Cable with interference suppressors fitted on each end used to connect D-Racks and D2-Racks. Please carefully note the following connection requirements:

**DMI-MADI C to D-Rack at 48KHz**

Connect DMI card Cat5e socket A to D-Rack Cat5e socket.

**DMI-MADI C to D-Rack at 96KHz**

Connect DMI card Cat5e socket A to D-Rack Cat5e socket.

NOTE: This setup provides one 28 channel 96kHz MADI stream therefore D-Rack input sockets 29-32 will not pass audio.

**Single Console to D-Rack with DMI MADI C Card**

Labels: D-Rack · Console · Audio Sync = MASTER

![DMI-MADI Cards (manual p.42)](/figures/gs-p022-1.png)

37

2.2 DMI-MADI Cards

**DMI-MADI C to D2-Rack at 48kHz**

Connect DMI card Cat5e socket A to D2-Rack Cat5e Main socket.

**Single Console to D-Rack with DMI MADI C Card**

Labels: D-Rack · Console · Audio Sync = MASTER

![DMI-MADI Cards (manual p.43)](/figures/gs-p022-1.png)

**DMI-MADI C to D2-Rack at 96kHz**

Connect DMI card Cat5e socket A to D2-Rack Cat5e MAIN socket. Connect DMI card Cat5e socket B to D2-Rack Cat5e AUX socket.

**Single Console to D2-Rack with DMI MADI C Card at 96KHz**

D2-Rack

Audio Sync = MASTER

![DMI-MADI Cards (manual p.43)](/figures/gs-p022-1.png)

38

2.2 DMI-MADI Cards

**DMI-MADI B to D2-Rack, SD-Rack or SD-MiNiRack at 48kHz**

Connect DMI card BNC IN socket A to D2-Rack BNC OUT MAIN socket. Connect DMI card BNC OUT socket A to D2-Rack BNC IN MAIN socket.

**Single Console to D2-Rack with DMI MADI B Card at 48KHz**

![DMI-MADI Cards (manual p.44)](/figures/gs-p044-1.png)

**DMI-MADI B to D2-Rack, SD-Rack or SD-MiNiRack at 96kHz**

Connect DMI card BNC IN socket A to D2-Rack BNC OUT MAIN socket. Connect DMI card BNC OUT socket A to D2-Rack BNC IN MAIN socket. Connect DMI card BNC IN socket B to D2-Rack BNC OUT AUX socket. Connect DMI card BNC OUT socket B to D2-Rack BNC IN AUX socket.

**Single Console to D2-Rack with DMI MADI B Card at 96KHz**

![DMI-MADI Cards (manual p.44)](/figures/gs-p044-2.png)

**DMI-MADI B to a Standard MADI device at 48kHz**

Connect DMI card BNC IN socket A to Standard MADI device BNC OUT. Connect DMI card BNC OUT socket A to Standard MADI device BNC IN.

**DMI-MADI B to a Standard MADI device at 96kHz**

Connect DMI card BNC IN socket A to Standard MADI device CH 1-32 BNC OUT. Connect DMI card BNC OUT socket A to Standard MADI device CH 1-32 BNC IN. Connect DMI card BNC IN socket B to Standard MADI device CH 33-64 BNC OUT. Connect DMI card BNC OUT socket B to Standard MADI device CH 33-64 BNC IN.

39

2.2 DMI-MADI Cards

### 2.2.2 Sharing Racks with DMI-MADI

If the system is running at a sample rate of 48KHz a D2-Rack, SD-Rack or SD-MINIRack can be shared between 2 consoles (Two QUANTUM 2s or an QUANTUM 2 and another S or SD-Series console) with the connection system shown below. In this setup: 1) All inputs can be shared by the two consoles but only one console controls the rack analogue gains (the "Master" console) 2) The console which is not controlling the gains (the "Slave" console) can automatically adjust its digital trims to compensate for the gain changes using a system known as "Gain Tracking" (see below) 3) Only the "Master" console can use the outputs of the shared rack The recommended connection between the Monitor (Slave) console and Stage Rack is a single MADI OUT from the Shared Rack's AUX MADI connected to the console's MADI A IN The FOH (Master console) is connected via MADI A IN and OUT to the stage rack. A similar method can be used if the Monitor console requires gain control and the FOH console will track the gain changes. MADI OUT from the Shared Rack's AUX MADI connected to the FOH console's MADI A IN. The Monitor (Master console) is connected via MADI A IN and OUT to the stage rack.

Note: The "Master" console should be set to provide "Master Sync" (Setup>Audio Sync menu - see diagram below) to the Shared rack The "Slave" console should be set to receive its Audio Sync from the MADI DMI slot that is connected to the Shared Rack. 1) The operators should agree on and set a level of analogue gain that provides enough headroom for the required application. 2) The second console should connect to the Shared rack in Receive Only mode (only MADI Input cable connected) 3) Gain Tracking (the GT ON/OFF button at the top of the Input channel setup view) can be switched on for the console that is in "Receive Only" mode for all the channels that are being shared. 4) When an analogue gain control is changed on the "Master" console, the "Slave" console's analogue gain should reflect the changes and the digital trim control should compensate for this change by moving by the same amount in the opposite direction.

IMPORTANT Note: If Gain Tracking is active on a channel, the digital trim control will still respond to the local gain adjustment by compensating locally for the displayed gain change. If the "Slave" console loads a session where the Analogue Gain and +48V settings do not match the current state of the racks, the Master console should then reload its session to update the state of these controls on the "Slave" console

**FOH & MONITORS WITH SHARED RACK at 48KHz USING MADI**

![DMI-MADI Cards (manual p.45)](/figures/gs-p045-1.png)

![DMI-MADI Cards (manual p.45)](/figures/gs-p044-1.png)

40

2.2 DMI-MADI Cards

If the system is running at a sample rate of 48KHz, a D-Rack can also be shared between 2 consoles (Two QUANTUM 2s or a QUANTUM 2 and another SD-Series console with Cat5e connections eg SD9 or SD11) with the connection system shown below. This setup is similar to the one previously described but requires a DiGiCo Little Red Box. The Little Red Box has separate Cat5e connections for: The D-Rack itself The FULL CONNECT " Master" console The RECEIVE ONLY "Slave" console In all other respects the setup is the same as that for the D2-Rack and SD-Rack

**SHARING A D-RACK at 48KHz USING MADI**

![DMI-MADI Cards (manual p.46)](/figures/gs-p045-1.png)

![DMI-MADI Cards (manual p.46)](/figures/gs-p044-1.png)

41

2.3 DMI - Dante Cards
