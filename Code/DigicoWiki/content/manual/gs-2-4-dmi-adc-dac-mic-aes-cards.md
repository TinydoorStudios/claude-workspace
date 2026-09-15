# 2.4 DMI - ADC - DAC - MIC - AES Cards

*DMI Cards — manual page 49*

![DMI-ADC card rear panel: 16 analogue inputs on two 25-way D connectors, channels 1-8 and 9-16](/figures/gs-p049-1.png)

![DMI-DAC card rear panel: 16 analogue outputs on two 25-way D connectors, channels 1-8 and 9-16](/figures/gs-p049-2.png)

![DMI-AES card rear panel: 16 AES-EBU inputs/outputs (8 pairs) on two 25-way D connectors, channels 1-8 and 9-16](/figures/gs-p049-3.png)

The DMI-ADC card provides 16 analogue inputs on 2 x 25 way "D" connectors. The ADC card is a line card only. There is no microphone amplifier or phantom power available. The S-series consoles have no gain control function for these inputs (only digital trim). Maximum input level +22dBu.

The DMI-DAC card provides 16 analogue outputs on 2 x 25 way "D" connectors. DAC card is line level only. Maximum output level +22dBu (Digital Full Scale).

The DMI-MIC card provides 8 microphone pre-amps on 1 x 25 way "D" connector. The S-Series consoles have control over phantom power, gain and pad on the card.

The DMI-AES card provides 16 Inputs (8 pairs) and 16 outputs (8 pairs) on 2 x 25 way "D" connectors. All AES inputs are provided with sample rate conversion (SRC) by default. All AES outputs are synchronised to the mixer system clock.

### Multi-Pin Connector Pinouts

The DMI module range use 25 way "D" connectors, Female on the module (Male required on the connecting cable). The pin connections are as follows.

**Analogue inputs and outputs — sorted by pin**

| Pin | Function |
|---|---|
| 1 | 8+ |
| 2 | 0 |
| 3 | 7- |
| 4 | 6+ |
| 5 | 0 |
| 6 | 5- |
| 7 | 4+ |
| 8 | 0 |
| 9 | 3- |
| 10 | 2+ |
| 11 | 0 |
| 12 | 1- |
| 13 | nc |
| 14 | 8- |
| 15 | 7+ |
| 16 | 0 |
| 17 | 6- |
| 18 | 5+ |
| 19 | 0 |
| 20 | 4- |
| 21 | 3+ |
| 22 | 0 |
| 23 | 2- |
| 24 | 1+ |
| 25 | 0 |

**Analogue inputs and outputs — sorted by function**

| Function | Pin |
|---|---|
| 0 | 2 |
| 0 | 5 |
| 0 | 8 |
| 0 | 11 |
| 0 | 16 |
| 0 | 19 |
| 0 | 22 |
| 0 | 25 |
| 1- | 12 |
| 1+ | 24 |
| 2- | 23 |
| 2+ | 10 |
| 3- | 9 |
| 3+ | 21 |
| 4- | 20 |
| 4+ | 7 |
| 5- | 6 |
| 5+ | 18 |
| 6- | 17 |
| 6+ | 4 |
| 7- | 3 |
| 7+ | 15 |
| 8- | 14 |
| 8+ | 1 |
| nc | 13 |

**AES-EBU combined in/out — sorted by pin**

| Pin | Function |
|---|---|
| 1 | 4out+ |
| 2 | 0 |
| 3 | 3out- |
| 4 | 2out+ |
| 5 | 0 |
| 6 | 1out- |
| 7 | 4in+ |
| 8 | 0 |
| 9 | 3in- |
| 10 | 2in+ |
| 11 | 0 |
| 12 | 1in- |
| 13 | nc |
| 14 | 4out- |
| 15 | 3out+ |
| 16 | 0 |
| 17 | 2out- |
| 18 | 1out+ |
| 19 | 0 |
| 20 | 4in- |
| 21 | 3in+ |
| 22 | 0 |
| 23 | 2in- |
| 24 | 1in+ |
| 25 | 0 |

**AES-EBU combined in/out — sorted by function**

| Function | Pin |
|---|---|
| 0 | 2 |
| 0 | 5 |
| 0 | 8 |
| 0 | 11 |
| 0 | 16 |
| 0 | 19 |
| 0 | 22 |
| 0 | 25 |
| 1in- | 12 |
| 1in+ | 24 |
| 1out- | 6 |
| 1out+ | 18 |
| 2in- | 23 |
| 2in+ | 10 |
| 2out- | 17 |
| 2out+ | 4 |
| 3in- | 9 |
| 3in+ | 21 |
| 3out- | 3 |
| 3out+ | 15 |
| 4in- | 20 |
| 4in+ | 7 |
| 4out- | 14 |
| 4out+ | 1 |
| nc | 13 |

**Pinout and connection notes:** 0 = earth/ground or screen/shield · nc = not connected · + = phase/hot · - = antiphase/cold

Analogue connections for input and output are connected in the same way, as shown. Analogue connections for channels 1-8 shown, channels 9-16 follow the same pattern (1 = 9, 2 = 10 etc.).

AES connections are shown as 4 stereo (2 channel) connections, equivalent to channels 1-8. AES connections for stereo connections 1-4 (ch 1-8) shown, connections stereo 5-8 (ch 9-16) follow the same pattern (1 = 5, 2 = 6 etc.).
