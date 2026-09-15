# 2.11 Network and Mirroring

*Chapter 2: The Master Screen — manual pages 147–150*

### 2.11.1 Network Configuration

Any two SD Series consoles of the same type can be mirrored together to provide a fully redundant audio system. The SD7. Q7 and Q8 consoles are fitted with two separate engines, and as such, offer built in redundancy.

In order to take advantage of this redundancy, you need to verify the console networking is working and synchronise your session between the two consoles/engines.

Before the consoles/engines can be mirrored, you should ensure that a standard crossover network (Ethernet) cable is connected between the two consoles/engines (a standard network cable will also work with Quantum consoles). Without this connection, the two consoles/engines will not “talk” to each other. To open the Network window, touch the Network button at the top of the Master Screen. The following window will open…

Press the Select button to choose which device to send to or receive a session from

Optocore ID

![Network and Mirroring (manual p.147)](/figures/ref-p147-1.png)

![Network and Mirroring (manual p.147)](/figures/ref-p147-2.png)

When highlighted in orange the Audio Master button indicates this audio engine is currently active

![Network and Mirroring (manual p.147)](/figures/ref-p147-3.png)

Once synchronised, session details for both Engines will match

Press here to send a session to the selected device

Press here to receive a session from the selected device

Press here to mirror to or from the selected device

### 2.11.2 Mirroring for the first time

If the consoles are physically connected, but do not see each other, then you may need to enable Networking.

There is an option in the OPTIONS/CONSOLE tab to ENABLE CONSOLE NETWORK (YES/NO).  This must be set to YES on both Engines.  After doing this, shutdown and restart both consoles/engines and when the sessions are loaded go to the NETWORK window and you should see yellow OK lights against A & B. This indicates that the network has connected the two consoles/engines, but they are not yet mirrored.

To mirror the two consoles/engines, they need to be running the same session. The way to achieve this is to load the session into the A console/engine, then transfer it to the B console/engine using this Network window.

2.11 Network and Mirroring

1. Ensure you are switched to the A console/engine.

2. Load your session into console/engine A

3. Open the Network Window

4. Press the Select button for console/engine B and then press the Send Session to Selected button.

This will copy your current console/engine A session and load it into the B console/engine.  Once this is done, the console/engine B detail section will change to reflect the new loaded session.

You can now press the Mirror button. The Mirror buttons will turn green, and the console is now mirrored. Audio mastership can be switched between console/engine A and console/engine B using the Audio Master button and, if the racks are correctly connected, you will not hear the switch of between the two engines.

There is also an option to Receive Session from Selected which allows a session file to be brought into one engine from another.

When the Mirror from Selected or Mirror to Selected buttons are pressed, the current worksurface mix settings like fader positions are transferred from one device to another. If you have sent or received a session and then made some simple changes, the additional adjustments are normally transferred when you activate the Mirror mode. If there is a significant difference between the two devices' settings at that point, you will be prompted to resync the session.

On an SD7, the ENGINE A/B switch at the top of the centre worksurface will switch the entire worksurface from one engine’s control computer to another. It will not (by default) switch the audio processing from one engine to the other. This is achieved by pressing the relevant Audio Master button in the network window on either engine. When the button is orange, the engine is active. There is an option in OPTIONS/SURFACE tab that enables the switching of both control computer and audio mastership at the same time with the worksurface ENGINE A/B switch. When first configuring the system, we do not recommend running in this mode.

### 2.11.3 Mirroring Mode

This option determines how the console will behave when Mirrored via a network to another console, engine or Offline PC. This option is saved for console not in the individual session.

There are 4 modes of operation:

Full Mirror - all functions mirrored from one device to the other - this mode should be used on both engines in an SD7.

Expander - intended for use with an SD7 console and an EX007 Expander unit. The second device mirrors most functions from the first device but, significantly, allows different banks to be selected on the different devices.

Remote - intended for use with a PC being used as a Remote Control for a console. Allows different banks to be selected and different setup options on each device.

One Way - this mode is intended for remote monitoring of what another device is doing. If a device is in this mode, it can "see" what the other mirrored device is doing but cannot control the other device. This mode is only likely to be used in exceptional circumstances.

When mirroring 2 single engine consoles, the correct mirroring mode will depend on the operational requirements of the system.

2.11 Network and Mirroring

![Network and Mirroring (manual p.149)](/figures/ref-p149-1.png)

### 2.11.4 Mirroring with a laptop PC

Any SD or Quantum Series console can also be connected to a laptop PC running the Windows operating system in similar way to achieve remote control of the console.

When running SD or Quantum software on a PC, the software will appear in a number of "floating" windows, each of which represent a console section. A screen touch on the console is simulated by a right click with the PC mouse. To switch between console sections, use the small toolbar buttons that also appear on the screen marked Master\Left\Right etc.

The DiGiCo website has downloads available for all current versions of "Offline" software.

The SD and Quantum software on the PC is identical in operation to the console software and the USB key that is provided with the console will contain the offline software installation package.

Run the Installer from the USB Key.  It will create folders in the root directory of your PC's C:\ drive and place a shortcut to the Offline Software on the desktop.

IMPORTANT NOTE: When mirroring a console to a PC you are required to set a static IP address on your PC which is in the same subnet as the console itself. The console's subnet mask is 255.255.0.0  255.255.255.0 (SD7 only) and its IP address can be seen next to its entry in the Network panel - in the picture above it is 192.168.2.146 for Engine A.

The IP address of the PC must start with 192.168.2.xxx. and must be different to that of the console.

The setup of network addresses on a PC may differ from one operating system to another so if you are in doubt, please consult the documentation for your PC's operating system before proceeding.

As an example, on Windows 10, the IP address and subnet mask can be changed by:

2.12 Setup Menu

1) Opening the Control Panel>Network and Internet>Network and Sharing Centre.

2) Left click on Change adapter settings in the side panel.

3) Double click on the on connection that is connected to the same network as the console.

4) Double Click on Internet Protocol (TCP/IP) from the list to show its properties.

5) Set the radio button to Use the following IP address

6) Type the IP Address and Subnet Mask as detailed above

7) Confirm the changes and restart the computer
