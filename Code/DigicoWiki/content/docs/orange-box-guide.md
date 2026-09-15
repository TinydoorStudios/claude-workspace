# Orange Box + Orange Box Controller V3.0 (DMI card reference)

*Chapter 1: Orange Box + Orange Box Controller V3.0 (DMI card reference) — manual pages 3–17*

Orange Box and Orange Box Controller V3.0 1.1 Introduction.

## The Orange Box

## 1.1 Introduction.

The Orange Box is a 2U Bi-Directional Multi-Channel audio format converter that utilises DiGiCo’s range of DMI cards.  The box has two DMI ports:- DMI 1 (MASTER) which is used to provide the Orange Box’s sync source if no Work Clock is present and DMI 2 (SLAVE).

## 1.2 DMI Cards.

Compatible DMI Cards.

The Orange Box with Orange Box Controller supports the following DMI Cards.

DMI ADC 16 Ch Line input card 48/96kHz

DMI DAC 16 Ch Line output card 48/96kHz

DMI AES 16 AES IO card with SRC 48/96kHz

DMI Aviom 16 Ch D16 Aviom Output Card 48/96kHz

DMI HYDRA 2 56 IO Calrec Hydra 2 interface 48kHz only

DMI DANTE 4/32 Ch DANTE IO card 48/96kHz

DMI DANTE 64@96 64 Ch Dante card c/w SRC 48/96kHz

DMI MADI B 128/64 Ch MADI BNC IO Card 48/96kHz

DMI MADI C 128/64 Ch MADI Cat5e IO Card 48/96kHz

DMI Optocore 128/64Ch Optocore IO Card 48/96kHz

DMI Waves 64Ch Waves SoundGrid IO Card 48/96kHz

DMI Mic 8 Ch Mic Pre Amp 48/96kHz

DMI ME A&H Personal Monitoring System 48/96kHz

DMI KLANG 64 Input into 16 immersive mixes 48/96kHz

Each release of Orange Box Controller will contain current DMI card firmware for use with that release.  Please see section 1.2.4 of this document for the Firmware contained within this release.

Please note that compatible DMI firmware may vary between current Orange Box and SD/S/Quantum series releases.

Orange Box and Orange Box Controller V3.0 1.2 DMI Cards.

Inserting a DMI Card.

IMPORTANT:- The Orange Box should be powered Off when inserting or removing any DMI card.

Slide the DMI card into the locating guides on each side of the port as show below.

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.4)](/figures/orange-box-guide-p004-1.png)

Slowly push the card in until it clicks into place and secure each card into the Orange Box using the four retaining screws.

DMI Card Pin outs and Hardware setup. DMI ADC, DAC and AES use 25 pin DSub connectors.   In addition, DMI MADI C has physical switches on it that determine its CAT5e wiring configuration. This is specified in TN 339 which in the Document Folder of Orange Box Controller, can be downloaded from https://digico.biz/base_product/all-technical-notes/ or requested from DiGiCo Support – support@digiconsoles.com

DMI Card Firmware in Orange Box Controller V3.0.

DMI Card Processor Version FPGA Version

DMI ADC V83 08/12/2015

DMI DAC V83 08/12/2015

DMI AES V83 08/12/2015

DMI AVIOM V83 08/12/2015

DMI HYDRA 2 V222 08/12/2015

DMI DANTE* V83 02/03/2016

DMI DANTE 64@96* V104 27/10/2021

DMI MADI B V167 28/02/2019

DMI MADI C V167 28/02/2019

DMI OPTOCORE V196 28/02/2019

DMI WAVES V83 22/02/2016

DMI MIC V243 21/06/2019

DMI ME V238 04/02/2019

DMI KLANG** N/A N/A

Orange Box and Orange Box Controller V3.0 2.1 Introduction

## Orange Box Controller

## 2.1 Introduction

The Orange Box Controller (OBC) program allows configuration and firmware updates of the DMI cards contained within the Orange Box.

Once the DMI cards have been configured using OBC, OBC can be disconnected, and the cards will return in the same state after every power cycle.

If a card is replaced, then OBC should be connected again to configure the new card as required.

OBC is currently compatible with Windows XP, Windows 7, Windows 8 and Windows 10.

Orange Box Controller connections and Drivers. OBC uses a standard FTDI USB to Serial Adaptor, the driver for which should automatically install on first connection.  If automatic installation does not occur, the drivers are available from http://www.ftdichip.com/FTDrivers.htm

As an example, the picture below shows Windows Device Manager with an Orange Box connected to the PC using a standard USB A-B cable.  Each DMI port is controlled by a separate COM port.  Here, the Orange Box has been assigned COM ports 60 & 61.  The COM port assignment is managed by Windows and the assignment will differ on each PC.

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.5)](/figures/orange-box-guide-p005-1.png)

## 2.2 Installing Orange Box Controller

The Orange Box Controller Installer will install the current version on to your PC.

It is currently compatible with Windows XP, Windows 7, Windows 8 and Windows 10.

The installer contains the Orange Box Controller program as well as all current DMI card firmware.

The installer will create the required folders in C:\Program Files\DiGiCo\Orange Box Controller.  DMI firmware files are copied to C:\ProgramData\DiGiCo\Orange Box Controller\Firmware

Installation Instructions.

1. Download the latest version of the Orange Box Controller Installer package from

https://digico.biz/base_product/orange-box/

2. Unzip the installer package

Orange Box and Orange Box Controller V3.0 2.3 The Orange Box Controller Interface

3. Double click on DiGiCo_Orange_Box_Controller_ Installer_VXXXXX.exe.  The Installer can be run from

either the computer or an attached USB drive.

4. The welcome screen will appear.  Click on Install.  Note that clicking Uninstall will only uninstall OBC

V3.0 or higher.  It will not uninstall any earlier versions.

5. The License Agreement window will now appear. The option to create a desktop shortcut is selected

by default.  Please click to accept the License terms and then click Install.

6. Once complete, the Finish window will appear.  Click on Exit to close this window.

## 2.3 The Orange Box Controller Interface

Version 3 of the OB interface contains an updated GUI, additional features as well as supporting new DMI functionality.

When connected to an Orange Box, the OBC main Control display shows the contents of the two DMI ports, Orange Box Sync information plus any data or controls specific to each DMI card.

The picture below shows the OBC main Control page.  There is a DMI MADI B in DMI 1 MASTER port and DMI AES in DMI 2 SLAVE port.

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.6)](/figures/orange-box-guide-p006-1.png)

Since not all cards have variable setting, a control panel will only be display when appropriate.

Orange Box and Orange Box Controller V3.0 2.3 The Orange Box Controller Interface

OBC Options menu.

Clicking on the menu icon in the top left-hand corner of OBC will open the Options Menu.  When this menu is open, the DMI card view will be blurred.

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.7)](/figures/orange-box-guide-p007-1.png)

Items that can be accesses in this Menu are:

- 

The DMI firmware folder.

- 

The Documentation folder

- 

The Software Licensing agreement

The Options menu can be closed at any time by clicking the arrow in the top right corner of the options menu.

**Sync Source Setup and display**

The Orange Box Clock is controlled by the DMI card in the MASTER (DMI 1) port.  Any DMI card in the MASTER port will show its clocking options in its Sync panel as shown below.

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.7)](/figures/orange-box-guide-p007-2.png)

When set to AUTO, the sync priority for that card will be as shown.  In the case of the MADI card shown above, clock priority is Word Clock>MADI A>MADI B. Each DMI card shows its available Sync Source options. The Sync Source in use is displayed under the Sync Select.

If the Sync Select is not set to AUTO and a specific Sync has been selected and that source becomes unavailable or the DMI card cannot lock to the selected Sync source, the DMI card will revert to its internal clock and the Sync Source will show FreeRun.

In the top left corner of DMI 1 is the sample rate display showing the Current sample rate of DMI 1The DMI card in the SLAVE (DMI 2) port will always be clocked to the MASTER (DMI 1) port.

Orange Box and Orange Box Controller V3.0 2.3 The Orange Box Controller Interface

The sample rate display in the top left corner of DMI 2 I the sample rate provided from DMI1 > DMI 2.  If any SRC is enabled, this will show the internal Sample Rate of DMI 2.

**Upgrading DMI Card Firmware**

When OBC is started, it will check the DMI Firmware Codes are up to date with the codes contained within the Orange Box Controller Folder.  If either DMI card requires a change in firmware the Update Code tab will automatically be selected.

In Update, the code the DMI card is currently running and the available code is displayed.  If an update is required, the tick in the Update column will be replaced by a Green arrow and Update Required! will be displayed.

The picture below shows the Update section for both DMI ports.  Both cards are running up to date codes.

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.8)](/figures/orange-box-guide-p008-1.png)

IMPORTANT:-  Remove ALL Audio connections from the DMI cards before beginning the update process.

Clicking Update All will update both the Processor and FPGA codes.  Alternatively, each code can be individually updated by clicking on the tick in the Update column.

The update process can be run simultaneously on both DMI cards if required.

Please note:- Firmware packaged with OBC maybe different to the DMI firmware included in the current S/SD/Quantum releases, 4rea4 or KLANG Konductor.  OBC only supports the firmware packaged with each OBC release.

Orange Box and Orange Box Controller V3.0 3.1 General

## DMI Card settings

## 3.1 General

In addition to Sync Source Selection, DMI AES, DMI H2, DMI MADI B, DMI MADI C, DMI Dante 64@96, DMI KLANG and DMI Optocore have variable settings which are adjusted using the OBC.

These settings are stored on the card until either the Firmware is changed or the DMI card is used in a DiGiCo S/SD/Quantum Console, 4rea4 or KLANG Konductor.

This section will detail the possible settings for each card.

Please note:-

DMI Dante card will need Dante Network configuration in addition to its Sync Source settings.  All DANTE devices should be configured using Dante Controller which is available from:-

https://my.audinate.com/support/downloads/dante-controller

DMI Waves Card will need Soundgrid Network configuration in addition to its Sync Source settings.  This is done using either Waves MultiRack, SuperRack or SoundGrid Studio, all of which are available from:-

https://www.waves.com/products

## 3.2 DMI AES

The DMI AES card has SRC controls on each pair of inputs.  The default setting for the SRCs is ON.

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.9)](/figures/orange-box-guide-p009-1.png)

OBC will also display the incoming sample rate of each AES stream.

The AES outputs do not have SRCs and will therefore be at system sample rate.

Orange Box and Orange Box Controller V3.0 3.3 DMI HYDRA 2

## 3.3 DMI HYDRA 2

The DMI H2 card requires an ID to be set before joining a Hydra 2 network.  The Hydra Network must be running V3.2 or above software.

Please note the DMI Hydra card will only work when in the SLAVE Port of the Orange Box.

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.10)](/figures/orange-box-guide-p010-1.png)

## 3.4 DMI MADI B & DMI MADI C

**DMI MADI C Hardware Switch**

DMI MADI C has a physical hardware switch which sets whether the card is acting as a “console” or “rack”. The switch is located on the main pcb to the rear of the RJ45 connectors as shown below.

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.10)](/figures/orange-box-guide-p010-2.png)

Further detail on this are in TN339 which is available from https://digico.biz/base_product/all-technical-notes/

Orange Box and Orange Box Controller V3.0 3.4 DMI MADI B & DMI MADI C

**MADI Mode Selector**

At the bottom of the OBC MADI DMI display is a MADI type connection.  When the DMI card is in the Master slot there are two options, Auto & DiGiCo.  When the DMI card is in the slave slot there are three options, Auto, DiGiCo & 64CH

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.11)](/figures/orange-box-guide-p011-1.png)

Auto – When Auto is selected, the DMI card will set its transmit channel count and sample rate to match that of the received MADI stream.

When connected to an SD Series console, it will also detect and respond to DiGiCo CH57 Control Data where applicable and report the Orange Box as an IO Device.

The picture below shows an SD series Audio IO Page.  The Console is connected to an Orange Box with MADI with a DMI MADI in the MASTER port and a DMI AES in the SLAVE port. The DMI MADI type is set to Auto.

Conforming all ports in Audio IO detects the Orange Box as an IO Device type.  The DMI AES in the SLAVE port is also detected and the card slots are populated to allow for routing within the console.

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.11)](/figures/orange-box-guide-p011-2.png)

If the SLAVE was a DANTE DMI, Audio IO would report 64 DANTE IO.

DiGiCo – When DiGiCo is selected, the DMI MADI card no longer responds to DiGiCo Ch57 control Data being received from an SD series console but acts as a pass-through device.

An additional function of the DMI MADI card is to allow the transparent transportation of DiGiCo CH57 Control Data, either as a MADI extender or across and 3 Party Digital Network. This allows an SD Series rack to be detected and controlled without a direct connection.

Here is an example.

SD Console>MADI>Orange Box MADI/DANTE>DANTE Network>Orange Box DANTE/MADI>SD Rack.

- 

The SD console is connected using BNCs to an Orange Box configured as MADI/DANTE.

- 

A second Orange Box configured as DANTE/MADI is connected to an SD Rack with BNC.

- 

Using OBC, in both Orange Boxes set DMI MADI Type to DiGiCo.

- 

Using DANTE Controller, create a 57CH Bi Directional connection between the two DMI DANTE cards.

- 

When Conform all ports is pressed in Audio IO, the console will report the SD rack as a device type and the console will have full control over all socket parameters eg, gain, +48v, pad.

Orange Box and Orange Box Controller V3.0 3.4 DMI MADI B & DMI MADI C

In the above set up, both Orange Boxes transparently pass the DiGiCo control data across the DANTE Network allowing the console to directly communicate with the SD Rack.

64CH – When 64CH is selected, the MADI channel RX/TX count is fixed to 64 Channels and the DMI card will not respond to DiGiCo Ch57 Control Data.  The SRC Controls also become active and the Device Connected At sample rate must be defined.

Note - When a DMI MADI card is in the Master Slot, it is assumed that BOTH the MADI in & MADI out are connected to another device.

**MADI Connection Details**

Below the Controls label are two columns labelled MADI A and MADI B, one for each connection to the DMI card.  The following information is displayed in each box:-

- 

In Channels – Number of MADI channels being received.

- 

In Sample Rate – Sample rate of the connected MADI input.

- 

Out Channels – Number of channels in the outgoing MADI Stream.

- 

Sync – When locked is displayed, the incoming, outgoing MADI and DMI MADI Cards are synchronised.

- 

Connection – Displays either Generic (Standard MADI), Console (connected to a DiGiCo Console). Rack (connected to an SD Rack), DiGiCo (control pass through mode) or Unknown.

- 

The picture below shows a DMI MADI B in the “SLAVE” port of an Orange Box connected to an SD Rack at 48 kHz,

- 

Rack type/Rack code – When connected to an SD series rack and the MADI type is set to Auto, the rack type and Sharc firmware dates will be displayed.

In addition to the Rack type and Code dates, the contents of each card slot will be displayed as will rack power supply diagnostic data.

The picture below shows a DMI MADI B in the “SLAVE” port of an Orange Box connected to an SD Rack at 48 kHz.  The Racks menu is selected so the card, firmware and PSU details are shown.

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.12)](/figures/orange-box-guide-p012-1.png)

Orange Box and Orange Box Controller V3.0 3.4 DMI MADI B & DMI MADI C

**96 kHz MADI**

There are 2 MADI standards when running at 96 kHz, SMUX (48k frame) and High Speed (true or 96k frame). For a detailed explanation on the differences between the two standards, please consult DiGiCo Technical Note TN294.

The DMI MADI card auto detects sample rate changes between 48 kHz and 96 kHz.  SMUX MADI uses a native 48 kHz clock which the DMI detects and reports.  This 48 kHz SMUX clock cannot be differentiated from a standard 48 kHz without intervention.

If the DMI card is connected to an SD Series console and its MADI type is set to AUTO, the DiGiCo CH57 Control Data will instruct the DMI card to set itself to SMUX mode therefore providing the SLAVE DMI card with a 96 kHz clock.

In any other MADI type mode, the SMUX mode needs to be manually set.  This is done by clicking the SMUX box located above each MADI details box.

In the following picture, the incoming sample rate in the MADI details box is being correctly reported as 96 kHz (SMUX).  If SMUX was not selected, the sample rate would report as 48kHz.  By activating SMUX mode, the Orange Box sample rate is set to 96 kHz and consequently the DMI Card in the SLAVE slot is being provided a 96 kHz sync source and audio will appear on the correct channels.

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.13)](/figures/orange-box-guide-p013-1.png)

An Orange Box containing two DMI MADI cards can be used to convert 96 kHz MADI between the SMUX and Labels: High-Speed Formats. · Port Mode · There are two Port Modes.

Redundant. – The same signal is sent and received on both sets on BNC/CAT5 connections.  If the input from connection MADI A fails, then the Audio arriving on MADI B will routed to the other DMI Card.

Dual. -  MADI A and MADI B act as independent MADI connections allowing up to 128 Channels (2 x 64CH) of MADI at 48kHz and up to 64 Channels (2 x 32CH) at 96kHz of MADI to be passed between DMI 1 & DMI 2

Orange Box and Orange Box Controller V3.0 3.4 DMI MADI B & DMI MADI C

**MADI SRC**

From OBC V3 and DMI MADI V167, Sample Rate Conversion (SRC) is supported. Additional controls have been added to OBC to control this.  The controls are different depending on whether the DMI MADI card is in DMI1 Labels: or DMI 2. · MADI DMI In Master Slot · MADI DMI In Slave Slot

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.14)](/figures/orange-box-guide-p014-1.png)

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.14)](/figures/orange-box-guide-p014-2.png)

When in the Master Slot (DMI 1), the SRC controls decide the Sample rate provided to the DMI card in the Slave Slot (DMI 2).

The DMI MADI Mode must be set to Auto for the SRC controls to become active.

The controls are: -

Off – SRC is switched off.  The sample rate provided to Slave Card (DMI 2) track the sample rate of the incoming MADI stream.

48kHz – The sample rate provided to Slave Card (DMI 2) will be 48kHz whatever the sample rate of the incoming MADI stream is.

96kHz - The sample rate provided to Slave Card (DMI 2) will be 96kHz whatever the sample rate of the incoming MADI stream is.

When in the Slave Slot (DMI 2), the SRC controls should match the Sample rate of the device that is connected to the MADI card.

The DMI MADI Mode must be set to 64CH for the SRC controls to become active.

The controls are: -

48kHz – The connected device has a sample rate of 48kHz

96k Smux – The Connect device has a sample rate of 96kHz and the MADI format is set to SMUX.

96K HiSpeed - The Connect device has a sample rate of 96kHz and the MADI format is set to Hi Speed.

The SRC State box compares the Sample rate of the MADI input and the DMI Card Sample rate and will report either Active or Inactive.

Orange Box and Orange Box Controller V3.0 3.5 DMI Optocore

## 3.5 DMI Optocore

**Overview**

This card enables an Orange Box to be added to an existing Digico Optocore Network.  The card runs V221 Optocore firmware and so can only be integrated into systems using SD Racks.

The Optocore card will need its ID, Fibre speed and channel count set using OBC before it is added to a network.

The picture below shows a DMI Optocore card in the MASTER port of the Orange box.  In the audio IO page of an SD Console, this would appear as an Orange Box, Optocore ID 14 with 48 inputs and 32 outputs.

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.15)](/figures/orange-box-guide-p015-1.png)

**Channel Count Setup**

When a DMI card is paired with a DMI Optocore card in an Orange Box, the OBC control panel will provide controls to set the required input and output channels to the Optocore system in groups of 8 channels.  The Sample rate of the system will dictate the number of available channels.

DMI Optocore has extra configuration options when used with DMI MADI.  At 48kHz, up to 128 inputs and outputs can be used using MADI A (64Ch) and MADI B (64Ch).  At 96kHz, up 64 channels can be used but this can be configured as one 64 channel port or two independent 32 channel ports.  This configuration will determine how the Orange Box is displayed in the SD consoles audio IO.

The picture below shows DMI Optocore panel at 96kHz configuring its MADI channel count.  It is set as 2 x 32ch MADI connections with MADI A as 32in 32out and MADI B as 16in 16out.

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.15)](/figures/orange-box-guide-p015-2.png)

If the MADI mode was set to 1x64, then only one 64ch port would be displayed.

Orange Box and Orange Box Controller V3.0 3.6 DMI Dante 64@96

**Optocore System Clock**

The location of the DMI Optocore card in the Orange Box will have a direct impact on the clock set up of the Optocore network.

When located in the MASTER port, the card will get its clock from the Optocore Network.

When the card is in located in the MASTER port and a Word clock is applied to the Orange Box then the DMI Optocore will become the master clock for the Optocore Network.

When the card is located in the SLAVE port, it will automatically become the Optocore Network clock master and will get its reference clock from the DMI card located in the MASTER port.

## 3.6 DMI Dante 64@96

OBC V2.7 or above includes support for the new DMI Dante 64@96 card. This card provides 64 input and 64 output channels at both 48kHz &96kHz, along with support for SRC (Sample Rate Conversion). This enables the Orange Box to run at a different sample rate to the Dante network.

When the DMI Dante 64@96 is in the SLAVE port of the Orange Box AUTO SRC is active, the card keeps track of the sample rate of the card in the MASTER port of the Orange Box and the Dante network and will sample rate convert if they do not match.  The picture below shows an Orange Box with a DMI Optocore in the MASTER port running at 96kHz and a DMI Dante 64@96 where the Dante Network is running at 48kHz with SRC active.

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.16)](/figures/orange-box-guide-p016-1.png)

When the DMI Dante 64@96 is in the MASTER port of the Orange Box, the SRC control defines the sample rate that is applied to the card in the SLAVE port. The picture below shows an Orange Box with a DMI Dante 64@96 in the MASTER Port running at 48kHz and a DMI Optocore in the SLAVE port where the Optocore Network is running at 48kHz.  The SRC control has been set to 96kHz therefore the SLAVE port will always receive a 96kHz sample rate as its reference.

Orange Box and Orange Box Controller V3.0 3.7 DMI KLANG

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.17)](/figures/orange-box-guide-p017-1.png)

## 3.7 DMI KLANG

OBC V2.8 and above includes support for DMI KLANG.  The Card provides 64 sends from the console and returns 16 stereo binaural mixes plus a stereo solo (34 Channels).  In order to get the full channel processing count when paired with a DMI Optocore, the Optocore card should be set for 40 inputs and 64 Outputs as shown below.  The DMI KLANG must be running KOS 4.3.24 or higher to work with an Optocore Connection.

The card must be located in the Slave slot of the Orange Box

![Orange Box + Orange Box Controller V3.0 (DMI card reference) (manual p.17)](/figures/orange-box-guide-p017-2.png)

From the control panel, the card’s network details can be viewed.  There are 2 modes, Dynamic, where the cards IP is set by DHCP; and Fixed IP, where the IP address, Subnet Mask and Gateway (if required) can be defined.

All of these settings are also available in KLANG:app.

The DMI KLANG firmware version cannot be updated using Orange Box Controller.

For Firmware details please see https://www.klang.com/en/downloads
