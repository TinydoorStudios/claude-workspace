# TN339 — DMI connections and setup

*Chapter 1: TN339 — DMI connections and setup — manual pages 1–5*

## TECHNICAL NOTE

Date 15th Sept 15  (rev12, Dec 21) ref  339 Raised by:   TC Distributed to:   as required

Digico(UK) Ltd. unit 10 Silverglade Business Park Chessington Surrey  KT9 2QL  England

Tel: +44 1372 845600  email: support@digiconsoles.com

**DMI INTERFACE MODULES**

**INSTALLATION, CONNECTIONS AND SETUP NOTES**

**INSTALLATION**

Orange Box racks and DMI equipped mixers are normally supplied without DMI cards installed. Installation is straightforward. First TURN OFF MAINS POWER to the host unit. Remove the blanking panel(s) and 4 fixing screws (retain these for use with the DMI module). The card guides are at the top of the module. Slide card in and secure with 4 fixing screws. Note the mode of the Madi-Cat5 card has to be set BEFORE installation (see notes below). Note use of the left and right slots in Orange box can affect clocking (see notes below)

**CLOCKING ARRANGEMENTS for DMI Modules in ORANGE BOX**

Refer to the Orange Box manual for full setup details. See Digico website manuals download page.

Note that the position of modules in the Orange box chassis normally determines the clock arrangement. The chassis is hard-wired to send word clock from the left slot to the right slot (unless an external clock is connected to the word clock input BNC and selected in software). This means the incoming (embedded) clock to the digital DMI module in the left slot (DMI 1/master) is passed to, and output from (again embedded), the digital DMI module in the right slot (DMI 2/slave). In effect, the system connected to the left slot is clock master and the system connected to the right slot is clock slave. Where an external clock is connected to the Orange Box, this is sent to DMI modules in both slots.

**CLOCKING ARRANGEMENTS for DMI MODULES in Mixers**

The above does not apply to left and right slots in DMI equipped mixers, where clock sources are software controlled on the mixer audio sync page. Refer to the specific mixer manual for setup details.

**ADC & DAC features**

ADC card is a line level card only. There is no microphone amplifier or phantom power available. Mixers have no gain control function for these inputs (only digital trim). Maximum input level +22dBu OB has no control of trim available DAC card is line level only. Maximum output level +22dBu (Digital Full Scale) See below for connection details

**MIC PRE features**

Maximum input level +22dBu. Maximum gain available +60dB. +48V switchable phantom. Note control of this module is only supported by DMI slot equipped mixers running compatible software version. Refer to the Support for required version information. Orange Box does not support control of this module. Module is 8 channels only. Ventilation holes should be kept free to allow cooling.

TN339     DMI connections and setup    Page 1 of 5

**AES IO features**

AES inputs are provided with sample rate conversion (SRC) by default and will support inputs from 44K to 96K irrespective of the mixer system rate. AES outputs are synchronised to the mixer system clock. See below for connection details

**MADI CAT 5 PORT MODE SETUP**

The Madi-C module is intended for use with Digico audio over Cat 5 devices only. This is NOT Ethernet.

It must be setup individually on both ports for the correct operating mode, prior to the module being inserted.

See picture for switch setting. Note there are separate switches for the 2 ports.

Console Mode:  This is sets the port connection to match a console or mixer connection. This is used if the remote connection is to SD-series rack (e.g. D-Rack or D2-Rack) This would be the normal setting for a DMI module installed in a mixer, when connected to rack.

Rack Mode:  This is sets the port connection to match a rack type connection. This is used if the remote connection is to a console. It is important to understand this mode could be used in a console if the other connection is also to a console.

It is not possible to send audio between 2 DMI devices if BOTH are set to the same mode.

![TN339 — DMI connections and setup (manual p.2)](/figures/tn339-dmi-setup-p002-1.png)

Please refer to Technical note TN227 for details of the Cat 5 connection specifications for Digico MADI over Cat 5. It is important note this is NOT Ethernet and therefore typical computer network considerations may not apply.

The second (B port) connection is used for 96K operation (above channel 28/32) only.

**MADI BNC PORT MODE**

This port is normally configured for 64 channels for standard madi @ 48K. 64 channels are supported S- Mux or Hi-Speed @ 96K using both pairs of BNC’s, or 32 channels only on 1 BNC pair S-MUX. It can be configured for 56ch/28ch use. The second (B port) connection allows configuration as a second 64 channel port in Orange Box but not Mixers, or for 96K operation (above channel 28/32) in 96K equipped systems. It does not support 48K redundant operation. There is no sample rate conversion.

It is compatible with Digico Racks if installed in a mixer, which will auto detect what is present externally.

**AVIOM A-net® PORT**

This is for Aviom audio over Cat 5 personal mixers devices only and not compatible with Aviom Pro64 net. This is NOT Ethernet. This includes sample rate conversion and will operate at 48KHz (A-net standard) with the mixer system set for 96KHz.

Stereo link switches marked 1-8 link output channel pairs 1-2, 3-4, 5-6 etc.

TN339     DMI connections and setup    Page 2 of 5

**DANTE® PORT**

The Dante card will operate as a 64 channel IO at 48K and 32 channel at 96K. It is provided with main and secondary (backup) Gigabit Ethernet ports for connection to the Dante network.

All control and configuration of the Dante interface is done externally by the Audinate control software. A separate control computer must be provided to do this. There is no sample rate conversion.

In mixers, the Dante card can be selected as the mixer system clock source or the Dante network can be set to use the mixer as the network system clock (in the Audinate system software). Refer to notes above regarding clocking when used in Orange Box.

**DANTE64@96 ®  PORT**

Features as DANTE DMI but offers 64 channel IO at both 48K and 96K and also provides sample rate conversion (SRC) but not automatically and requires user intervention / setup in control software.

In mixers, the Dante card can be selected as the mixer system clock source or the Dante network can be set to use the mixer as the network system clock (in the Audinate system software). Refer to notes above regarding clocking when used in Orange Box.

It is important to note that SRC intended for conversion between 48K & 96K rates at same base clock period. It is not possible to correctly sync 2 asynchronous systems both at the same nominal sample rate via this module.

A 3rd Ethernet port is provided intended to allow local separate connection to a PC for control of the Dante networked devices (using Audinate system software).

**HYDRA-2® PORT**

The Hydra-2 card will operate as a 56 channel IO at 48K and does not operate at 96K. It is provided with primary and secondary ports for connection to the Hydra2 network.

The Hydra2 DMI card can be supplied with either Single Mode or Multimode LC optical connections. These must be specified at the time of order.

Currently the Hydra2 card must be selected to run from the system clock, refer to the mixer or Hydra2 manual.

All control and configuration of the DMI Hydra2 interface is done externally by connection to the appropriate Calrec module and Calrec HID control software. Please refer to Calrec Hydra2 Digico Orange Box Interface document ref 926-216 for full information.

See

http://calrec.com/wp-content/themes/calrec/pdf/Orangebox%20Installation%20(926-216%20Iss2).pdf

Copy/Paste the above address into your browser

**OPTOCORE ® PORT**

The Optocore card is available with HMA (expanded beam), Neutrik OpticalCON Duo or ST optical connectors. Refer to TB101 (on Digico Website) for optical cable specifications. As standard it is multimode operation, optionally it can be supplied for single mode use.

Note there are 2 standards for connection to OpticalCON or LC cabling. As standard, the DMI is parallel connected. This can be readily re-arranged within the connector if required.

The Optocore card can be configured to support any number up to a maximum of 128 channels at 48K and 64 channels at 96K.

Refer to the Orange box manual for the off-line setup procedure. The module must be pre-configured prior to use.

Currently mixers do not support the operation of Optocore DMI fitted in the mixer. Note Orange Box cannot be configured to control a Digico SD-Rack over madi from an Optocore connection.

The normal sync arrangement for the Orange box applies. If the module is used in the right side of the chassis, it receives external clock. In this case note that, in turn, this will then become clock master for the connected Optocore network (in a similar manner to connecting an external word clock to a Digico SD-series rack).

TN339     DMI connections and setup    Page 3 of 5

**ALLEN & HEATH Me ® PORT**

This is for A&H audio over Cat 5, 40 channel personal mixers devices only. This is NOT Ethernet. This includes sample rate conversion and will operate at 48KHz (Me standard) with the mixer system set for 96KHz.

**WAVES SoundGrid ®  PORT**

The Waves card will operate as a 64 channel IO at 48K and also 64 channel at 96K.

It is provided with 2 Gigabit Ethernet ports for connection to the SoundGrid network. These act a 2 port switch allowing simultaneous connection, for example, to a control PC and Waves SoundGrid server.

All control and configuration of the Waves interface is done externally by Waves control software. A separate control computer must be provided to do this. Note mixers cannot run Waves software.

In DMI equipped mixers, the Waves card can be selected as the mixer system clock source or the SoundGrid network can be set to use the mixer as the network system clock (in the Waves system software). Refer to notes above regarding clocking when used in Orange Box.

**Digco AMM (Automatic Mic Mixer) Module**

This is a self-contained processor module with no external audio connections. It supports 64 channels of audio providing automatic gain control to a proprietary Digico algorithm. It operates at 48K or 96K

Note control of this module is only supported by DMI slot equipped mixers running compatible software version. Refer to the current mixer manuals for  operating notes.

Orange Box does not support control of, or connection to this module.

**4REA4 A3232 PORT**

Provides 2 separate 32 channel A3232 ports, compatible with all Digico 4REA4 devices. Ethernet IO is 96K (standard for 4REA4) there is no SRC.

Note control of this module is only supported by S Series mixers running compatible software version. Refer to the Support for required model and version information.

Orange Box does not support control of, or connection to this module.

Refer to TN444 for 4REA4 network connection requirements.

**KLANG Processor Module**

Provides complete low latency KLANG immersive processing for up to 16 x 2-channel mixes with 64 inputs at 48kHz or 96kHz.There is no sample rate conversion. Note there are no audio connections direct to this module.

It provides 2 Ethernet control ports for external personal controller PC’s and devices.

Note this module is only supported by DMI slot equipped mixers running compatible software version. Orange Box is supported only with limited choice of companion connection to this module.

Refer to the Klang Documentation for required model and version information.

TN339     DMI connections and setup    Page 4 of 5

**MULTI-PIN CONNECTOR  PINOUTS**

The DMI module range use 25 way “D” connectors, Female on the module (Male required on the connecting cable). The pins connections are as follows.

**Analogue inputs and outputs**

AES-EBU combined in/out

Pinout and connection Notes: 0 = earth/ground or screen/shield    nc = not connected  + = phase/hot    - = antiphase/cold Analogue connections for input and output are connected the same, as shown Analogue connections for channels 1-8 shown channels 9-16 follow the same pattern (1 = 9, 2 = 10 etc.)  (except 8 channel Mic Pre module) AES connections are shown as 4 stereo (2 channel) connections, equivalent to channels 1-8 AES connections for stereo connections 1-4 (ch 1-8) shown, connections stereo 5-8 (ch 9-16) follow the same pattern (1 = 5, 2 = 6 etc.)

Function pin 8+ 7- 6+ 5- 4+ 3- 2+ 1- nc 8- 7+ 6- 5+ 4- 3+ 2- Labels: 1+ · Function pin · Function pin

4out+ 3out- 2out+ 1out- 4in+ 3in- 2in+ 1in- nc 4out- 3out+ 2out- 1out+ 4in- 3in+ 2in- Labels: 1in+ · Function pin · 1-

1+ 2- 2+ 3- 3+ 4- 4+ 5- 5+ 6- 6+ 7- 7+ 8- 8+ nc

1in- 1in+ 1out- 1out+ 2in- 2in+ 2out- 2out+ 3in- 3in+ 3out- 3out+ 4in- 4in+ 4out- 4out+ nc

Note the threaded pillars for locating the D connectors are UNC 440 thread, female.

TN339     DMI connections and setup    Page 5 of 5
