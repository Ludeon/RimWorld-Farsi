# Support & Troubleshooting Guide

Need help installing or running **RimWorld Farsi**? Check these quick steps before opening an issue.

## Quick Troubleshooting

1. **Game UI Still Shows English After Installing**
   - Ensure you deleted cached `.tar` language archives inside `<RimWorld>/Data/<DLC>/Languages/` (`Persian (فارسی).tar`).
   - Open **Options -> Language** and select **Persian (فارسی)**.

2. **Disconnected Letters or Inverted Words**
   - If you installed the **With RTL Mod** edition (or `autoinstall-*` Option 3), make sure **RTL Persian Support** is enabled under the in-game **Mods** menu and restart the game.
   - If you prefer **Mod-Free / Vanilla**, use the **Essential** or **Full** release archives (never copy raw repository XMLs directly without `PersianFixer.py`).

3. **Windows SmartScreen Warning on `.bat` Installer**
   - Unsigned batch files downloaded from GitHub trigger Windows SmartScreen. Click **More info -> Run anyway**, or verify the file's SHA-256 against `SHA256SUMS.txt` attached to the release.

4. **Check Logs When Filing a Bug**
   - **Steam / RimWorld log (`Player.log`)**:
     - Windows: `%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log`
     - Linux: `~/.config/unity3d/Ludeon Studios/RimWorld by Ludeon Studios/Player.log`
     - macOS: `~/Library/Logs/Ludeon Studios/RimWorld by Ludeon Studios/Player.log`

## Where to Reach Out
- **Translation bugs, UI clipping, or installer/mod issues:** [Open an Issue](https://github.com/Ludeon/RimWorld-Farsi/issues/new/choose)
- **General questions & ideas:** [GitHub Discussions](https://github.com/Ludeon/RimWorld-Farsi/discussions)
- **Security vulnerabilities:** [GitHub Security Advisories](https://github.com/Ludeon/RimWorld-Farsi/security/advisories/new)
