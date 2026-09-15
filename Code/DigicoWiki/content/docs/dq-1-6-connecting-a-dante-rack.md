# 1.6 Connecting a DANTE rack

* — manual pages 18–21*

PLEASE NOTE that for the connection and use of the A168D & A164D Dante IO boxes and DQ Rack, there is a requirement for the following firmware updates to the Dante 64@96 DMI card:

1. DMI Dante 64@96 firmware update (v103) which is currently available (June 2021) as part of the

Quantum 2 V1454 update package and all other DMI equipped SD/Quantum consoles running software application version v1280+.

2. A Dante firmware update (4.0.20) for the DMI Dante 64@96 card is required for control of the DQ-

Rack, details on how to update the DMI firmware can be found in TN514 available on the website and is included in the Quantum 2 V1454 update package.

3. If A168D and A164D Dante IO Racks are used with SD/Quantum applications earlier than V1454 they

should remain using Dante DMI firmware version 4.0.19 which can be updated using Dante Updater in Dante Controller.

Users who wish to use A164D and A168D with SD/Quantum applications V1454 or higher, need to upgrade the Digico firmware in these IO devices to V1.5.  This is done using the new DiGiCo Dante Rack Utility and can be done over an IP Network.  The update process is detailed in TN515.

Socket parameters on A168D, A164D and DQ-racks can be controlled in the same way as other DiGiCo I/O racks when connected to a Dante 64@96 DMI card and routed in Audinate’s “Dante Controller” software.

With a DMI Dante 64@96 card installed in a console, access to 64 channels of IO to/from the Dante network is provided.

A Dante IO box can provide a specific number of IO on the Dante network according to the rack’s capability.

168D = 16 analogue In and 8 analogue Out.

DQ-Rack = 48 analogue In and 24 analogue Out of which 4 are switchable AES Outs.

Any Dante network may have many more devices on it than just a single console and rack.

There might be multiple Dante equipped consoles, multiple racks and other Dante devices.

When a console has a DMI Dante fitted, it “sees” that DMI as a 64 channel interface device to/from the Dante network.

The source device of the audio signals it is receiving across that interface and the destination device of any signals that it is sending out across that interface are generally “unknown” to the console.

The critical component in determining where the audio is going to/from is the Dante network controller which is responsible for setting up audio paths (routing) on the network.

As an example, using just a single console and a single rack, the console could use its DMI Dante channel 1 as an input signal to its own console Input Channel 1 but the audio signal which appeared on that DMI Dante channel could be any signal from the Dante IO rack and is determined by the routing in the Dante Controller.

With the following routing in place, a console that selects any of the DMI card channels 1-16 as an input source will receive the signal from the same numbered Rack Input socket – this is a logical setup.

17

DQ & MQ-Rack User Guide 1.6 Connecting a DANTE rack

Dante Rack

Inputs

![Connecting a DANTE rack (manual p.19)](/figures/dq-p019-1.png)

![Connecting a DANTE rack (manual p.19)](/figures/dq-p019-2.png)

DANTE Rack is a Transmitter in this case.

Each of the 16 Rack input sockets are routed to the same numbered DMI 64@96 channel

![Connecting a DANTE rack (manual p.19)](/figures/dq-p019-3.png)

Dante Controller & Routing

![Connecting a DANTE rack (manual p.19)](/figures/dq-p019-4.png)

Network Switch

![Connecting a DANTE rack (manual p.19)](/figures/dq-p019-5.png)

Console 1

![Connecting a DANTE rack (manual p.19)](/figures/dq-p019-6.png)

DMI 64@96 is a Receiver in this case.

![Connecting a DANTE rack (manual p.19)](/figures/dq-p019-7.png)

Each channel receives the same numbered input socket from the rack.

In this example, a console that routes signal to DMI card output channels 1-8 will be sending them to the same numbered Rack Output socket.

18

DQ & MQ-Rack User Guide 1.6 Connecting a DANTE rack

![Connecting a DANTE rack (manual p.20)](/figures/dq-p020-1.png)

Console 1 DMI is a Transmitter in this case.

Each of the DMI 64@96 outputs 1-8 are routed to same numbered Rack output sockets

Network Switch

Console 1 – DMI Outputs

![Connecting a DANTE rack (manual p.20)](/figures/dq-p020-2.png)

Dante Controller & Routing

Dante Rack

![Connecting a DANTE rack (manual p.20)](/figures/dq-p019-1.png)

19

DQ & MQ-Rack User Guide 1.7 Rack Connections with MADI
