# Talkback

Setup > **Talkback** opens the panel. The talkback mic input, its gain and the three talk buttons are all here and mirrored on the surface talkback area.

![Setup > Talkback](/figures/q2-talkback.png)
*Setup > Talkback — Quantum 2 offline software, V22.*

## Set up the mic

Right side: the **gain pot** is always on the surface talkback gain encoder; the meter beside it shows level. Touch the white box under the pot to route the **talkback input** (usually the local mic input on the rear panel).

## Where each talk button goes

Each **talk** button has a text box under it. Touch the box to open TB Outputs and route that bus to physical outputs (a stage wedge, a comms feed). The first route shows in the box. The button rings red while the bus is active.

## Talk to auxes (monitor mixes)

The three blue boxes above the talk buttons select **aux busses**. Pick any combination of mono and stereo auxes for each talk button, and that button talks into all of them at once.

![Talk to Aux Setup](/figures/ref-p169-1.png)
*Manual figure: Talk to Aux Setup — mono/stereo aux list opened from one of the blue boxes — SD Quantum Software Reference, Issue H, p.169.*

Per-aux control also exists: on an aux output channel, hold an **Assign** button beside the assignable rotaries and touch the **talk** area of the screen. That rotary/switch pair becomes talk level and talk on/off for that aux, with a **dim** amount for ducking the mix while you talk.

![Aux channel talk level and dim controls](/figures/ref-p170-1.png)
*Manual figure: Aux channel talk level/dim strip — SD Quantum Software Reference, Issue H, p.170.*

Under the hood this is a Talkback Input channel that uses one processing channel; in a default session it sits alone in the last bank on the left.

Manual: [Reference 2.12.15 Talkback](/reference/2-12-setup-menu).
