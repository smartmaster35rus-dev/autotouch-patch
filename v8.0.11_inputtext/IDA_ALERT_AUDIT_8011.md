# AutoTouch 8.0.11 ATTweak — alert / license handler audit

Source: `ATTweak.dylib` from `me.autotouch.autotouch.ios8.inputtext` (arm64 slice, static disasm + ObjC dump).

## User-visible license strings (ATTweak)

| String | Role |
|--------|------|
| `License is needed to launch script automatically.` | Auto-launch gate — **modal waits for OK** |
| `License is needed to run script by timer.` | Timer scripts |
| `License Required` | Generic |
| Long App Store / license pitch text | `outputLicenseTimeout` / cooldown UI |

License state can be **OK** while this dialog still runs: auto-launch logic fires, then **Alert / UIAlertController** blocks until dismissed → script appears “stopped”.

## ObjC handlers (arm64 IMP)

| Class | Method | IMP | Patch |
|-------|--------|-----|-------|
| CommandServer | `licenseLimitTimeout` | `0xf7f4d0` | RET @ entry |
| CommandServer | `outputLicenseTimeout` | `0xf7f56c` | RET @ entry (calls alert stub `0xfd6820`) |
| CommandServer | `check` | `0xf7f5b0` | RET @ entry (schedules license re-check) |
| Spring | `licenseLimitTimeout` | `0xf8253c` | RET @ entry |
| CommandServer | `suYYKTj6MHk` | timer setup | RET (pattern scan, both slices) |

`outputLicenseTimeout` disasm: loads strings → `bl #0xfd6820` → **`showAlertWithTitle:message:buttonTitle:`** trampoline.

`AutoLaunchManager` `launch` / `start:` call into playing pipeline; alert is not always in the same function — **blocking UI is UIKit**.

## Patch strategy (hybrid v3)

1. **Binary** (`patch_attweak_8011.py`): timer + license handler RET (FAT arm64 + arm64e via signatures).
2. **crackATT v3**: in `SpringBoard`, `backboardd`, `AutoTouch.app` — **drop every `UIAlertController`** (armor mode) + keep `Alert showAlert*` no-ops + license hooks.

This matches “license is fine; kill all distraction popups so scripts keep running after respring”.
