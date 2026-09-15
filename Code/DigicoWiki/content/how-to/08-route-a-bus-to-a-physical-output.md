# Route an aux, group or matrix to a physical output

Output channels (aux, group, matrix) route from their **Output** panel to a socket on the console or a rack.

1. Go to the layer/bank with the bus (outputs live on layer 2 by default). Touch the **bottom** of the bus strip.
2. Press **output** at the bottom of the panel, then the routing button. Pick the port (Local I/O, rack, DMI-Dante…), signal group, then the output socket. Any number of outputs can be selected for a bus.

![Output panel routing (same panel on a bus)](/figures/q2-channel-output.png)
*Output panel routing (same panel on a bus) — Quantum 2 offline software, V22.*

3. The route shows under the button. Unlike inputs, adding a route doesn't remove the previous one; touch a blue socket again to remove it.

## What's already using a socket

An output socket already routed from another channel shows in blue text in the route panel; grabbing it anyway pops a confirmation, and continuing unroutes the old channel from that socket. In Audio I/O the socket number turns red (listen source) or orange (copy) if Copy Audio is using it. Output routes *can* overwrite copy-audio routes, so check before you grab a socket on a rack that's also feeding the recorder.

## Unroute everything on a port

Setup > Audio I/O > select the port > **unroute all outputs** (below the card graphic) > *Yes*. This clears every channel route to that port and can't be undone. Copied audio isn't touched.

## MQ-Rack AES outputs

On the MQ-Rack, output sockets 6, 12, 18 and 24 can be analogue *or* AES. Switch them in Audio I/O (the Line Out/AES switch on the socket). Switching one type makes the other inactive: audio routed to an inactive socket goes nowhere and the socket shows greyed out in routing.

![Line Out/AES switch, MQ-Rack](/figures/ref-p205-1.png)
*Manual figure: MQ-Rack Line Out/AES switch — Reference 3.1.10 MQ-Rack.*

See [MQ-Rack](/hardware/04-mq-rack).

Manual: [Reference 1.5 Output Channel Specific Functions](/reference/1-5-output-channel-specific-functions), [3.1.10 MQ-Rack](/reference/3-1-console-audio-connections).
