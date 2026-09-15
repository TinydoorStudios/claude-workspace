# DMI-Waves User Guide (Waves)

*Chapter 1: DMI-Waves User Guide (Waves) — manual pages 3–16*

## Introduction

The DMI Waves card enables integration with Waves SoundGrid systems via a single Ethernet cable. It provides 64 input and 64 output channels at 48kHz or 96kHz to the SoundGrid Network with two Ethercon ports. The DMI card connects to a SoundGrid host, which controls I/O devices, drivers, and an optional SoundGrid DSP server. DMI Waves is compatible with DiGiCo S-Series, Quantum Range, SD12, Orange Box and 4REA4.

DMI Waves allows easy integration of Waves plugins. One Ethercon port on the card can be connected to a computer running Waves SuperRack SoundGrid, and the other connected to a Waves server or additional I/O. The DMI-Waves can also be used in the Orange Box to run a virtual soundcheck on an Optocore loop.

A SoundGrid I/O device is part of a SoundGrid network. SoundGrid is the Waves high-speed networking protocol for moving audio, clock, and other information between a host system and I/O devices—and between I/O devices themselves. A SoundGrid host configures the network, assigning servers and I/O devices to mix, process, or record, depending on the host. SoundGrid I/Os link to the SoundGrid network with standard Ethernet cable.

SoundGrid is scalable. Connect one I/O device to a DAW and you have a high-quality sound card. Add more I/Os and your system becomes more flexible and powerful. Depending on the host application, a SoundGrid host can assign up to sixteen I/O devices. Complete SoundGrid systems can be networked together to share devices.

Add a server to a SoundGrid system to offload plugin processing from the host CPU to a SoundGrid DSP server. This dramatically increases processing power and enables greater plugin counts—it also provides very low system latency.

DMI Waves / User Guide

## Hardware and Connections

![DMI-Waves User Guide (Waves) (manual p.4)](/figures/dmi-waves-guide-p004-1.png)

DMI-Waves port 1 and port 2 connect to the SoundGrid Network. Each port has two LEDs to indicate status:

Link/Activity LED = flashing green

GigE (Gigabyte Connection Indicator) = solid orange

Two ports enable you to connect the DMI-Waves card directly to a host computer and one other device (e.g., I/Os, SoundGrid server) without needing an Ethernet switch. It is not important which of the two Ethernet ports is used to connect to the SoundGrid network. For installations that include more than two SoundGrid devices, a 1 GB Ethernet

DMI Waves / User Guide

Configure SoundGrid and assign your devices as follows, however large or small your system.

Labels: Connect the hardware · Install the software · Configure your system

## Connect the Hardware

One I/O

In this example, one DMI-Waves interface card is used to connect a console to the SoundGrid ASIO/Core Audio driver for plugin processing and/or DAW playback/recording. The interface is connected directly to the host using a Cat 5e Ethernet cable or better.

![DMI-Waves User Guide (Waves) (manual p.5)](/figures/dmi-waves-guide-p005-1.png)

Host computers with SoundGrid application and DAW

DiGiCo console with DMI-Waves card

The host computer’s LAN port that’s connected to the SoundGrid network should be used for SoundGrid only. Do not share this port with the internet or other networks.

In this configuration, all plugin processing is carried out on the host computer. The speed and power of the host defines

Labels: overall latency · DMI Waves / User Guide · Add I/Os

Adding I/O devices not only increases the number of I/O channels, but lets you have separate devices for stage and FOH, or live room and control room. When there are more than two network connections, use a "star" network configuration with a 1GB Ethernet switch. Only use switches tested and approved by Waves.

![DMI-Waves User Guide (Waves) (manual p.6)](/figures/dmi-waves-guide-p006-1.png)

Host computer DiGiCo console with DMI-Waves card Additional SoundGrid I/O 1GB Ethernet switch

See this support article for a list of supported switches.

You can connect and assign up to 16 SoundGrid I/O devices to the network, depending on the SoundGrid Host Application. All SoundGrid I/O devices, hosts, and servers are connected through the Ethernet switch. You can also add more computers to enable streaming between hosts.

ADD A SERVER

To add a server to your SoundGrid system, just connect it to the Ethernet switch and configure it in your host application. This moves all DSP processing from the host computer to the server, which provides a higher plugin count and enables the eMotion LV1 and ST mixers. Visit the waves.com hardware pages to learn more about SoundGrid servers. Consult your SoundGrid host application’s user guide to learn about using servers.

DMI Waves / User Guide

## Download and Install Software

INSTALLING A NEW SOUNDGRID HOST SYSTEM

Installing the Waves SoundGrid host application will also install applicable device drivers and ASIO/Core Audio drivers. Your devices will appear in the Inventory of your host system. If a device is not visible in the Inventory, you may need to install a specific driver from Waves Central—please see below. First, however, check the device’s connections and power.

ADDING AN I/O DEVICE TO AN EXISTING SOUNDGRID HOST SYSTEM If you are already using a Waves SoundGrid host application and your device does not appear in the Network Devices list, use Waves Central to update the host application, which also updates the device drivers—or install just the missing device driver from Waves Central.1

Waves Central

All Waves software is downloaded and installed via the Waves Central application. To install a specific device driver, launch Waves Central and follow these steps:

![DMI-Waves User Guide (Waves) (manual p.7)](/figures/dmi-waves-guide-p007-1.png)

Choose All Products

![DMI-Waves User Guide (Waves) (manual p.7)](/figures/dmi-waves-guide-p007-2.png)

Search for the driver by name

Choose the driver and click Install

![DMI-Waves User Guide (Waves) (manual p.7)](/figures/dmi-waves-guide-p007-3.png)

If you are new to Waves products, begin by downloading the Waves Central installer from the Waves Download Page. See the Waves Central User Guide for instructions on how to install drivers, plugins, and applications.

LICENSES

You do not need a license to use this device. However, many hosts or specific host configurations do require a license. Refer to your host’s product page for details.

DMI Waves / User Guide

## Configure the System

A SoundGrid network is configured and devices are assigned in a host’s Setup window. At the heart of this window are racks where devices are assigned. Any compatible device that’s part of the host’s SoundGrid network will be available for assignment. This collection of devices is called the Inventory. Setup is similar with all hosts: identify the host’s LAN port, select a device slot, and use the drop-down menu to choose an available device.

Please consult the user guide of your host application for specific instructions.

![DMI-Waves User Guide (Waves) (manual p.8)](/figures/dmi-waves-guide-p008-1.png)

![DMI-Waves User Guide (Waves) (manual p.8)](/figures/dmi-waves-guide-p008-2.png)

SoundGrid QRec

SoundGrid Studio Setup Window

All SoundGrid devices are configured in a similar manner. Throughout this section, we show DiGiGrid IOS as an example.

DMI Waves / User Guide

Manual Device Configuration

You can assign, remove, and manage a device manually. Click on the plus or arrow symbol in a device slot to open the Device Menu, then select a device.

![DMI-Waves User Guide (Waves) (manual p.9)](/figures/dmi-waves-guide-p009-1.png)

Any device not already used will be available for assignment. If no other devices are assigned, the current device will become your clock master. Drivers and servers are assigned in the same manner.

SoundGrid QRec

See the user guide of your host system for specific instructions on device assignment and I/O channel patching.

![DMI-Waves User Guide (Waves) (manual p.9)](/figures/dmi-waves-guide-p009-2.png)

SoundGrid Studio

Automatic Device Configuration with SoundGrid Studio

![DMI-Waves User Guide (Waves) (manual p.9)](/figures/dmi-waves-guide-p009-3.png)

Certain SoundGrid hosts—including SoundGrid Studio, eMotion LV1 or SuperRack SoundGrid—offer an Auto- Config tool. Once your devices are connected and powered up, click Auto to start the configuration.

Auto-config chooses the correct LAN port on the host computer and scans the SoundGrid network for devices. It then patches the devices to the host. We recommend that you let Auto-Config take care of things, at least when you are getting started. If later you add, remove, or swap a device; Auto-Config will reconfigure your inventory and re-patch.

Note that SoundGrid Studio assigns the SoundGrid driver automatically. SuperRack SoundGrid and eMotion LV1 require that the SoundGrid ASIO/Core Audio driver is assigned manually.

DMI Waves / User Guide

Device Firmware An I/O that is using outdated or incompatible firmware will not work properly in a SoundGrid network until its firmware is updated. The color of the FW button in a device slot indicates the current firmware status.

![DMI-Waves User Guide (Waves) (manual p.10)](/figures/dmi-waves-guide-p010-1.png)

![DMI-Waves User Guide (Waves) (manual p.10)](/figures/dmi-waves-guide-p010-2.png)

Grey Compatible firmware

Blue Compatible firmware, but a newer version exists

Red Firmware not compatible and must be updated in order to use

SoundGrid Studio SoundGrid QRec

If a device requires updated firmware, click on the FW button to start a hardware scan. Do not disconnect the device or turn off the computer before Done appears. Once the update is ready, turn the device off and on to reset.

Identify a Device on the SoundGrid Network

![DMI-Waves User Guide (Waves) (manual p.10)](/figures/dmi-waves-guide-p010-3.png)

![DMI-Waves User Guide (Waves) (manual p.10)](/figures/dmi-waves-guide-p010-4.png)

When the ID button is pressed, the LEDs on the panel of the card change colors repeatedly to help identify the device.

SoundGrid Studio SoundGrid QRec

DMI Waves / User Guide

## DMI Waves Control Panel

There are two ways to access the device control panel:

FROM THE DEVICE RACK

![DMI-Waves User Guide (Waves) (manual p.11)](/figures/dmi-waves-guide-p011-1.png)

![DMI-Waves User Guide (Waves) (manual p.11)](/figures/dmi-waves-guide-p011-2.png)

Click on the Gear button on a device in the rack slot.

SoundGrid Studio SoundGrid QRec

FROM THE DRIVER CONTROL PANEL

![DMI-Waves User Guide (Waves) (manual p.11)](/figures/dmi-waves-guide-p011-3.png)

Open the driver control panel and then click the Hardware Control Panel button. The driver control panel is located here in the host computer:

PC: C:\Program Files (x86)\Waves\SoundGrid\Driver Control Panel

Mac: System HD/Applications/Waves/SoundGrid

## Control Panel Pages

The About and System Info pages provide information about the unit, such as MAC address, SoE master, firmware version, and more. The Clock page is used to assign clock source and sample rate, as well as to monitor clock status.

DMI Waves / User Guide

## Clock Page

Use the Clock page to set the clock source and sample rate for the device and to assess clock status.

![DMI-Waves User Guide (Waves) (manual p.12)](/figures/dmi-waves-guide-p012-1.png)

SOURCE sets the requested clock source.

Internal The unit itself provides the clock

Digital Syncs via the connection to the console

Sync over Ethernet Syncs to the master I/O of the SoundGrid network.

SAMPLE RATE sets the sample rate when Clock Source is set to Internal. Range: 48 kHz, 96 kHz

DMI Waves / User Guide

**CLOCK STATUS INDICATORS**

Three windows on the right side of the Clock control panel help you to quickly assess the network status of the device.

Status Reports the presence or absence of sync between the unit and the SoundGrid network.

Current Clock Source Displays the current sync method. This may differ from the choice made in the Source menu.

SOE Indicates whether this unit is the master or a slave in the SoundGrid network. This mirrors the status information in the SoundGrid Studio Device Rack

When the device is a slave in the SoundGrid network, you will likely sync it to the SoundGrid network clock (via SOE).

Even when the device is an SOE slave, you can lock it to an external clock source. For example, if another SoundGrid I/O device is the SOE master and is locked to a word clock device, you may choose to receive clock from the same external device over word clock from the master device, rather than via network SOE.

DMI Waves / User Guide

## System Info Page and About Page

The About page contains a description of the device. The System Info page contains technical details about the device, including MAC address, and Firmware version. This information can be useful for troubleshooting. Please have this information handy if you contact Waves technical support concerning the device.

![DMI-Waves User Guide (Waves) (manual p.14)](/figures/dmi-waves-guide-p014-1.png)

![DMI-Waves User Guide (Waves) (manual p.14)](/figures/dmi-waves-guide-p014-2.png)

DMI Waves / User Guide

## Presets

The Top Bar is used to load and save device presets and to identify device hardware.

You can save and load presets of device settings. A saved preset includes all Clock and Control panels parameters. Save DMI-Waves presets to use on future sessions or copy them to another computer to duplicate a configuration.

Click the ID button to indicate which DMI-Waves hardware device belongs to this Control Panel. Clicking the button causes the LEDs on the panel of the card change colors repeatedly to help identify the device.

DMI Waves / User Guide

## Using an I/O Device with a DAW

Setting up SoundGrid devices with a DAW involves these steps:

PATCH THE I/O DEVICE AND THE SOUNDGRID ASIO/CORE AUDIO DRIVER

When using a DAW on a SoundGrid network, the SoundGrid ASIO/Core Audio driver serves as a bridge between the I/O device and the DAW. It enables the I/O to communicate with the DAW, and it provides patches. Patching an I/O to the SoundGrid ASIO/Core Audio driver differs slightly among hosts. When you use a host’s Auto-Config tool, the host input channels are patched automatically, in an order based on rack. The order of the devices in the Device Rack determines the default patching order. Please refer to your SoundGrid host’s user guide for details.

CONFIGURE THE DAW FOR SOUNDGRID

1. Set the DAW playback engine to “Waves SoundGrid.” The SoundGrid driver channels will now appear in the DAW

I/O preferences and in the Input/Output selector in each DAW channel.

2. Route the DAW inputs and outputs to SoundGrid.

DMI Waves / User Guide
