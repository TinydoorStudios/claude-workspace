# 6.4 DMI - ADC - DAC - MIC - AES Cards

*Chapter 6: DMI Cards — manual pages 234–236*

![DMI - ADC - DAC - MIC - AES Cards (manual p.234)](/figures/ref-p234-1.png)

![DMI - ADC - DAC - MIC - AES Cards (manual p.234)](/figures/ref-p234-2.png)

![DMI - ADC - DAC - MIC - AES Cards (manual p.234)](/figures/ref-p234-3.png)

![DMI - ADC - DAC - MIC - AES Cards (manual p.234)](/figures/ref-p234-4.png)

The DMI-ADC card provides 16 analogue inputs on 2 x 25 way "D" connectors.

The ADC card is a line card only. There is no microphone amplifier or phantom power available.

The S-series consoles have no gain control function for these inputs (only digital trim). Maximum input level +22dBu.

The DMI-DAC card provides 16 analogue outputs on 2 x 25 way "D" connectors.

DAC card is line level only. Maximum output level +22dBu (Digital Full Scale).

The DMI-MIC card provides 8 microphone pre-amps on 1 x 25 way “D” connector.

The S-Series consoles have control over phantom power, gain and pad on the card.

The DMI-AES card provides 16 Inputs (8 pairs) and 16 outputs (8 pairs) on 2 x 25 way "D" connectors.

All AES inputs are provided with sample rate conversion (SRC) by default.

All AES outputs are synchronised to the mixer system clock.

**Multi-Pin Connector Pinouts**

The DMI module range use 25 way “D” connectors, Female on the module (Male required on the connecting cable). The pins connections are as follows.

**Analogue inputs and outputs**

**AES-EBU combined in/out**

**Sorted by pin**

**Sorted by function**

**Sorted by pin**

**Sorted by function**

Function  Pin Function Pin Function Pin Function Pin

8+ 1 0 2 4out+ 1 0 2

0 2 0 5 0 2 0 5

7- 3 0 8 3out- 3 0 8

6+ 4 0 11 2out+ 4 0 11

0 5 0 16 0 5 0 16

5- 6 0 19 1out- 6 0 19

4+ 7 0 22 4in+ 7 0 22

0 8 0 25 0 8 0 25

3- 9 1- 12 3in- 9 1in- 12

2+ 10 1+ 24 2in+ 10 1in+ 24

6.4 DMI - ADC - DAC - MIC - AES Cards

0 11 2- 23 0 11 1out- 6

1- 12 2+ 10 1in- 12 1out+ 18

nc 13 3- 9 nc 13 2in- 23

8- 14 3+ 21 4out- 14 2in+ 10

7+ 15 4- 20 3out+ 15 2out- 17

0 16 4+ 7 0 16 2out+ 4

6- 17 5- 6 2out- 17 3in- 9

5+ 18 5+ 18 1out+ 18 3in+ 21

0 19 6- 17 0 19 3out- 3

4- 20 6+ 4 4in- 20 3out+ 15

3+ 21 7- 3 3in+ 21 4in- 20

0 22 7+ 15 0 22 4in+ 7

2- 23 8- 14 2in- 23 4out- 14

1+ 24 8+ 1 1in+ 24 4out+ 1

0 25 nc 13 0 25 nc 13

Pinout and connection notes:

0 = earth/ground or screen/shield nc = not connected + = phase/hot - = antiphase/cold

Analogue connections for input and output are connected in the same way, as shown.

Analogue connections for channels 1-8 shown, channels 9-16 follow the same pattern (1 = 9, 2 = 10 etc.).

AES connections are shown as 4 stereo (2 channel) connections, equivalent to channels 1-8.

AES connections for stereo connections 1-4 (ch 1-8) shown, connections stereo 5-8 (ch 9-16) follow the same pattern (1 = 5, 2 = 6 etc.).

6.5 DMI - Waves - Hydra Cards
