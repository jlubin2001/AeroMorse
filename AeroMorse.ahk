; AeroMorse.ahk — hotkeys for AeroMorse (AutoHotkey v2, Windows)
; https://github.com/jlubin2001/AeroMorse
;
; AeroMorse types keys; it cannot start a program or move the pointer to a
; place on the screen by itself. This script fills that gap: it watches for
; three key combinations, and each one has a Morse code in morse_map.py.
;
;   Ctrl+Alt+D      AeroMorse Display window on / off
;   Ctrl+Alt+Home   mouse pointer to the middle of the screen
;   Ctrl+Alt+H      AeroMorse Help (cheat sheet with tabs) on / off
;
; SET-UP (Build Guide Appendix G, Usage Guide section 7)
;   1. Install AutoHotkey v2 from https://www.autohotkey.com
;   2. Keep this file in your AeroMorse work folder (Documents\AeroMorse),
;      next to "AeroMorse Display.exe" and "AeroMorse Help.html". It finds
;      them in its own folder - there are no paths to edit.
;   3. Double-click it. A green H icon appears near the clock.
;   4. To start it with Windows: press Win+R, type  shell:startup  and put a
;      SHORTCUT to this file in the folder that opens.
;
; After editing this file: right-click the green H icon > Reload Script.
; In a hotkey,  ^ is Ctrl,  ! is Alt,  + is Shift,  # is the Windows key.

#Requires AutoHotkey v2.0
#SingleInstance Force

; A short note that closes by itself, for a file that is not where it should be.
Missing(name) {
    MsgBox(name " was not found in`n" A_ScriptDir "`n`nKeep AeroMorse.ahk in the same folder as that file.",
           "AeroMorse", "T8")
}

; Ctrl+Alt+D — AeroMorse Display window ON / OFF: opens the window if it is
; closed, closes it if it is open. The window remembers its size, place and
; see-through level.   Morse code: Group 0  .-.-.-
^!d:: {
    exe := A_ScriptDir "\AeroMorse Display.exe"
    if ProcessExist("AeroMorse Display.exe") {
        if WinExist("AeroMorse Display ahk_exe AeroMorse Display.exe")
            WinClose()
    } else if FileExist(exe)
        Run('"' exe '"', A_ScriptDir)
    else
        Missing("AeroMorse Display.exe")
}

; Ctrl+Alt+Home — put the mouse pointer in the middle of the main screen.
; Morse code: Mouse group  .-.
^!Home:: {
    CoordMode("Mouse", "Screen")
    MouseMove(A_ScreenWidth // 2, A_ScreenHeight // 2, 0)
}

; Ctrl+Alt+H — AeroMorse Help ON / OFF: the cheat sheet for YOUR map, legend
; at the top and one tab per group, in a plain window of its own (Microsoft
; Edge, no browser tabs or address bar). The same hotkey closes it.
; Morse code: Group 0  ..-..-
^!h:: {
    if WinExist("AeroMorse Help ahk_exe msedge.exe") {
        WinClose()
        return
    }
    page := A_ScriptDir "\AeroMorse Help.html"
    if !FileExist(page) {
        Missing("AeroMorse Help.html")
        return
    }
    edge := ""
    for dir in [EnvGet("ProgramFiles(x86)"), EnvGet("ProgramFiles")] {
        if dir != "" && FileExist(dir "\Microsoft\Edge\Application\msedge.exe") {
            edge := dir "\Microsoft\Edge\Application\msedge.exe"
            break
        }
    }
    if edge = ""
        Run('"' page '"')        ; no Edge: open it in the default browser instead
    else
        Run('"' edge '" --app="file:///' StrReplace(StrReplace(page, "\", "/"), " ", "%20") '"')
}

; ── Your own hotkeys ─────────────────────────────────────────────────────────
; Copy a block, change the key and what it runs, then give the new key
; combination a Morse code in morse_map.py. For example, Ctrl+Alt+N for Notepad:
;
; ^!n:: Run("notepad.exe")
