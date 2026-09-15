# 3.4 Advanced Settings

*Quantum Home — manual pages 61–62*

![Advanced Settings window: Lock System Settings, Display Settings (External Screen, Configure All, Identify Displays), Quantum Home Update](/figures/gs-p061-1.png)

- **Lock System Settings / Unlock System Settings:** locks/unlocks the system and triggers a console PC reboot.
  - **Locked state:** this is the "console mode" in which Quantum Home automatically launches the Quantum 2 application at start-up.
  - **Unlocked state:** "configuration mode" in which advanced settings and network settings are enabled.
- **Display Settings:**
  - **External Screen:** settings for the external monitor.
    - **Resolution:** drop-down list of available screen resolutions for the external screen.
    - **Orientation:** drop-down list of screen orientations:
      - Landscape.
      - Portrait.
      - Landscape (inverted).
      - Portrait (inverted).
      - Disconnected: disables the external screen.
    - **Position:** drop-down list of available positions for the external screen:
      - Left screen (acts as a channel view for the left fader bank, the screen follows bank selection).
      - Overview (acts as an external overview screen).
  - **Configure All:** applies the external screen settings and reconfigures the master, left and right screens. Once configured, Quantum Home identifies the screens, allowing for a visual confirmation of the new display configuration. Quantum Home will require a restart after displays configuration, either by locking and rebooting the console or by a forced restart of Quantum Home when exiting the Advanced Settings menu.
  - **Identify Displays:** pops up the display identification view on each screen, highlighting the current screen position.

![Advanced Settings with Identify Displays active, showing the "Master" screen-position overlay](/figures/gs-p062-1.png)

NOTE: To switch between Left and Overview screen as selections for the external screen, first unlock the system settings and wait for the console to reboot, then switch the position in Display Settings > External Screen > Position and press Configure All. This should display the new position of the screens relative to the master screen; lock and restart the console to apply it.

- **Quantum Home Update:**
  - **Select File:** opens a file dialog window to browse and open a new QuantumHome.exe file.
  - **Update:** applies the update by replacing the current Quantum Home with the selected file. Triggers a restart of Quantum Home.
