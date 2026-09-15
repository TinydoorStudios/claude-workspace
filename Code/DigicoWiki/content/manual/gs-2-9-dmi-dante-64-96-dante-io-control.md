# 2.9 DMI-Dante 64@96  & Dante IO Control

*DMI Cards — manual pages 55–58*

PLEASE NOTE that for the connection and use of the A168D & A164D Dante IO boxes, there is a requirement for the following firmware updates to the Dante 64@96 DMI card:

1. DMI Dante 64@96  firmware update (v103) which is included in the update package.

2. A Dante firmware update (4.0.19) for the DMI card which can be updated using Dante Updater in Dante Controller.

Socket parameters on A168D and A164D IO racks can be controlled in the same way as other DiGiCo I/O racks when connected to a Dante 64@96 DMI card and routed in Audinate’s “Dante Controller” software. With a DMI Dante 64@96 card installed in a console, access to 64 channels of IO to/from the Dante network is provided. A Dante IO box can provide a specific number of IO on the Dante network according to the rack’s capability. 168D = 16 analogue In and 8 Analogue Out Any Dante network may have many more devices on it than just a single console and rack. There might be multiple Dante equipped consoles, multiple racks and other Dante devices. When a console has a DMI Dante fitted, it “sees” that DMI as a 64 channel interface device to/from the Dante network. The source device of the audio signals it is receiving across that interface and the destination device of any signals that it is sending out across that interface are generally “unknown” to the console.

50

2.9 DMI-Dante 64@96  & Dante IO Control

The critical component in determining where the audio is going to/from is the Dante network controller which is responsible for setting up audio paths (routing) on the network. As an example, using just a single console and a single rack, the console could use its DMI Dante channel 1 as an input signal to its own console Input Channel 1 but the audio signal which appeared on that DMI Dante channel could be any signal from the Dante IO rack and is determined by the routing in the Dante Controller. With the following routing in place, a console that selects any of the DMI card channels 1-16 as an input source will receive the signal from the same numbered Rack Input socket – this is a logical setup.

Dante Rack Inputs

![DMI-Dante 64@96  & Dante IO Control (manual p.56)](/figures/gs-p056-1.png)

![DMI-Dante 64@96  & Dante IO Control (manual p.56)](/figures/gs-p056-2.png)

A168D Rack is a Transmitter in this case. Each of the 16 Rack input sockets are routed to the same numbered DMI 64@96 channel

![DMI-Dante 64@96  & Dante IO Control (manual p.56)](/figures/gs-p056-3.png)

Dante Controller & Routing

![DMI-Dante 64@96  & Dante IO Control (manual p.56)](/figures/gs-p056-4.png)

Network Switch

![DMI-Dante 64@96  & Dante IO Control (manual p.56)](/figures/gs-p056-5.png)

Console 1

DMI 64@96 is a Receiver in this case. Each channel receives the same numbered input socket from the rack.

![DMI-Dante 64@96  & Dante IO Control (manual p.56)](/figures/gs-p056-6.png)

51

2.9 DMI-Dante 64@96  & Dante IO Control

In this example, a console that routes signal to DMI card output channels 1-8 will be sending them to the same numbered Rack Output socket.

Console 1 DMI is a Transmitter in this case. Each of the DMI 64@96 outputs 1-8 are routed to same numbered Rack output sockets

Network Switch

Console 1 – DMI Outputs

![DMI-Dante 64@96  & Dante IO Control (manual p.57)](/figures/gs-p057-1.png)

Dante Controller & Routing

Dante Rack Outputs

![DMI-Dante 64@96  & Dante IO Control (manual p.57)](/figures/gs-p056-1.png)

52

3.1 Main Shortcuts

When the Master screen > System > Quit To Windows button is pressed, the console application is closed and the Quantum Home interface can be used to adjust various system settings. When the system is locked, Quantum Home automatically launches the Quantum 2 application on start-up. When unlocked, the system can be configured.
