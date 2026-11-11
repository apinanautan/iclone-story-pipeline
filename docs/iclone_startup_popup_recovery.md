# iClone 8 Startup Popups: inspect BOTH monitors, dismiss safely

MANDATORY before EVERY iClone start, restart, project load or queued scene job.
User confirms these dialogs recur at launch. The iClone MAIN window can be on monitor 2 while blocking dialogs appear on MONITOR 1. Looking only at monitor 2 is a known failure.

## Observed incidents (2026-11-11)
A) Connection warning. Title 'iClone 8'; body: 'Failed to establish a connection due to unknown error. Please ensure proper internet connection and try again.' Button: 'OK'. Closing it may reveal a second dialog.
B) Registration/signup splash. Title 'iClone'; image says 'SIGN UP NOW AND GET' with 'Sign me up!' and 'No, thank you.' buttons. On MONITOR 1 it was observed at bounds (520,292)-(1016,572), HWND 462014, PID 5088. These are historic examples ONLY; never reuse historic HWND/PID/coordinates.
C) A DIFFERENT visible title 'iClone 8' dialog was also found on MONITOR 2, while the main window 'iClone 8 - DefProject.iProject' was on monitor 2. That dialog's message was not conclusively identified, so inspect before dismissing. Never blindly dismiss a save-confirmation or other unknown dialog.

## Required startup sequence
1. On DESKTOP-F1PJT4S identify BOTH current screens via Windows Screen.AllScreens / their actual bounds. Do not assume monitor 1 has no iClone window just because main iClone is on monitor 2.
2. Enumerate ALL visible top-level Windows for the iClone.exe PID using EnumWindows, GetWindowThreadProcessId, IsWindowVisible, GetWindowText and GetWindowRect. Also inspect child/Qt dialogs and capture the smallest necessary part of EACH monitor if title is generic.
3. For the verified connection warning only: click its OK button, or close the EXACT verified dialog HWND. Re-enumerate both monitors immediately.
4. For the verified signup only: click 'No, thank you.' (do not sign up). If the button cannot be accessed, use a targeted WM_CLOSE on that registration dialog HWND ONLY after confirming process, bounds and visual content. NEVER close main iClone hwnd.
5. For any other popup, first read the message. DO NOT automatically close unsaved-work confirmation or unrecognized dialogs.
6. After each dismissal, verify (a) target HWND no longer exists, (b) iClone main process/window still alive and responsive, (c) both monitors now free of blocking iClone startup dialogs. Repeat the scan until no verified startup blockers remain.
7. Avoid stealing focus or moving the cursor on MONITOR 1. Prefer targeted Win32 / headless semantic operations. If headed mouse/keyboard is absolutely necessary, remember and restore previous foreground/window and cursor; verify restoration. Main iClone work belongs on MONITOR 2.
8. Only after the startup dialogs are gone: verify watcher actually running by checking a NEW read-only job completion (not merely watcher.alive), and confirm actual iProject title. A loaded default scene is not the requested story.
9. If dismiss action fails, STOP, report title, content, PID, live HWND, screen and blockage. Never press random keys or load a huge project while a modal blocks UI. Do not claim scene/video done just because a dialog closed.
10. Record which dialog was found on which screen, the action taken and confirmation. Check on EVERY launch/relaunch, not just once.

Relevant prior evidence: Verified registration HWND 462014 on monitor 1 was closed with targeted WM_CLOSE; IsWindow returned false, while iClone.exe remained alive. A distinct iClone 8 dialog existed on monitor 2. HWND 462014, PID 5088 and listed coordinates must NOT be hardcoded for future sessions.

## iCloneStoryBridge startup compatibility warning (2026-11-11)
A real modal on DISPLAY2 titled "iClone 8" said: "'iCloneStoryBridge' Python plugin is not compatible with this version of iClone. Do you still want to proceed?" It has OK and Cancel. Distinguish this from signup or internet connection error; inspect both monitors. On 2026-11-11, stale queued Python work was first moved to a safe .hold filename, then the exact OK button was clicked through agent-desktop accessibility (not physical mouse). Verified fresh mcp_autostart_status.txt said STARTED: ic8_watch.py loaded by OpenPlugin, and a fresh read-only watcher script produced a .done result. Only then open the saved iProject. Do not interpret this warning as a completed load, and do not blindly press OK on unknown dialogs.
