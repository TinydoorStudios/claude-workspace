# The offline software, and mirroring a laptop to the console

The Quantum offline software is the console application running on a Windows PC. Use it to build a session at home, then load it on the desk, or mirror it to the desk for remote control.

## Get it

support.digico.biz > Software Downloads > Quantum > **V22 Quantum Offline Software** (download the Q225 package; the Q225 and Q225 Dual Screen builds are separate). The console must be on the same version to open a session saved from it. The installer creates `C:\Quantum2` and a desktop shortcut. Templates are read from `C:\Templates` in offline (D:\Templates on the desk).

On screen, each console section is a floating window; **Master / Left / Right** toolbar buttons switch between them, and a right-click stands in for a screen touch. System > **Keyboard Help** lists the keyboard equivalents of surface controls.

## Move a session between laptop and desk

Save on the laptop, copy the `.ses` to a USB stick, Files > Load Session > **Removable** on the console. Same the other way. Sessions are version-specific; a V22 console can open older sessions but not the reverse without the Session Converter.

## Mirror the laptop to the desk

1. Ethernet between laptop and console. The console's IP is shown in the Network panel (Master screen > **Network**). Give the laptop a static IP in the same subnet (console default is 192.168.x.x with mask 255.255.0.0; pick a different last octet).
2. On both: Options > **Console** > *Enable Console Network* = Yes, then restart both.
3. Master screen > **Network**: yellow OK lights on A and B mean they see each other.
4. Load the session on the **console**, select the laptop in the Network panel, press **Send Session to Selected**.
5. Press **Mirror**. Buttons turn green.

![Network panel](/figures/ref-p147-1.png)

Set the **Mirroring Mode** (Options) to **Remote** for a laptop: it lets the laptop show different banks and panels than the desk. **Full Mirror** is for redundant engines; **One Way** lets the laptop watch without controlling.

## Session and engine on the Q225

The Q225 has one engine, so there's no engine A/B failover; Network here is only for the laptop or another console.

Manual: [Reference 2.11 Network and Mirroring](/reference/2-11-network-and-mirroring), [Offline software readme](/downloads/digico-offline-software-readme.pdf).
