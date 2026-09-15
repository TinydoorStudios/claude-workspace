# A168D Stage (Dante 16×8 box)

A rugged 16-in / 8-out stage box: 16 remote-controlled mic/line XLR inputs with 48V indicators, 8 XLR line outputs at +4 dBu, universal IEC power. The **A168D** is the Dante version (the plain A168 talks DiGiCo 3232 over Cat5e to a 4REA4). Sits flat, on its side, or in a 19" rack with the X-A-168-19RK kit.

![A168 Stage](/figures/a168-guide-p002-1.png)
*A168 Stage front panel — ① 16 mic/line inputs, ② 8 line outputs — A168 Stage Quick Guide p.2.*

## Connect it

1. Power, then the Dante port to the switch (or direct to the DMI-Dante card).
2. Dante Controller: match the A168D's sample rate to the DMI card; subscribe DMI receive channels to the A168D's 16 transmit channels and the A168D's 8 receive channels to DMI transmit channels. Keep it 1:1 (input 1 → DMI 1) so the console's names make sense.
3. Console: Audio I/O > **add port** > A168D > conform. Gain, pad and 48V are now on the channel strip.

![A168D transmit → DMI receive](/figures/gs-p056-4.png)
*A168D (transmitter) routed 1:1 into DMI 64@96 receive channels on the console — Getting Started Guide p.56.*

## Firmware

Preamp control from a Quantum needs the A168D on DiGiCo firmware **V1.5+** (updated over IP with the DiGiCo Dante Rack Utility, TN515) and the DMI-Dante card on v103 with Dante firmware 4.0.20 (Summit) or the Zynq equivalent. On older console software (before V1454) the DMI should stay on Dante 4.0.19.

## Panel notes

The PP LED on each input shows phantom voltage at the socket whether the box or something external is supplying it. Keep the side and rear vents clear.

Quick guide: [A168 Stage (PDF)](/downloads/digico-a168-stage-guide.pdf), mirrored at [A168 Stage — Quick Guide](/docs/a168-guide). Manual: [Reference 3.1.8](/reference/3-1-console-audio-connections), [Getting Started 2.9](/console/2-9-dmi-dante-64-96-dante-io-control).
