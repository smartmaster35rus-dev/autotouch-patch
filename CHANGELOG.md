# Changelog

All notable changes to this project will be documented in this file.

## [8.5.5-v3.5] - 2026-09-26

### Added
- **Hybrid release** — official package with **binary-patched `ATTweak.dylib`** (16-byte setupTimer fix) **plus** `crackATT` for license state after respring
- `scripts/patch_attweak.py`, `scripts/build_hybrid_release.py`, `scripts/extract_deb.py`
- **postinst** runs `ldid -S` on `ATTweak.dylib` and `crackATT.dylib`, then **`ldrestart`**

### Fixed
- **License “falls off” after respring** — v3.4-only ATTweak patch left socket/UI checks unlicensed; v3.5 keeps `crackATT` in the deb and forces `_licensed` on `Global` / `CommandServer` init, `LicenseManager` async success, and settings label on every `viewWillAppear`

## [8.5.5-v3.3] - 2026-09-25

### Fixed
- **2-minute stop + dialogs** — block `JSEngine setupTimer`, `licenseLimitTimeout`, and `alertForProVersion` (AutoTouch License Required)
- **CommandServer / Global** — noop `outputLicenseTimeout`, force `licenseTimeout` → NO
- **PlayingManager** — hook both `stopAllPlayings` and obfuscated `stopAllPlayings_309465`
- **Alert filter** — broader license strings (auto-launch: “License is needed to launch script automatically.”)

### Unchanged from v3.2
- Settings **Licensed** UI (`ATTweakClient`, `SettingsViewController`, `_downloadLicenseSynchronously`)
- `validateLicense` MSHookFunction chain, CommandServer/Global timer hooks from v3
- `crackATT.plist` injects **backboardd** + SpringBoard; install scripts use **`ldrestart`**

## [8.5.5-v3] - 2026-09-22

### Fixed
- **Auto-launch license alert** — hook `validateLicense_108147`, `_validateLicense_108147`, `_validateLicenseFromKey_565433`
- **Wrong obfuscated selector** — `stopAllPlayings_309465` (was ineffective `stopAllPlayings`)
- **License UI fallback** — block `Alert showAlert:` for license strings
- **`isLicensed` / `licensed`** on `CommandServer_907239` and `Global_983499`

## [8.5.5-v2] - 2026-09-22

### Fixed
- **2-minute license timeout** — `crackATT v2` hooks the new AutoTouch 8.5.5 license chain (IDA-confirmed):
  - `CommandServer_907239`: `setupTimer_240358`, `licenseLimitTimeout_120300`, `check_929132`
  - `Global_983499`: `setupTimer_167855`, `licenseLimitTimeout_552565`
  - `JSEngine`: `alertForProVersion`
  - `PlayingManager_932730`: `stopAllPlayings`

### Added
- Theos tweak source (`tweak/Tweak.xm`) and GitHub Actions build workflow
- `scripts/prepare_release.py` for injecting built dylib into release package

## [8.5.5] - 2026-09-22

### Added
- Patched `.deb` for AutoTouch 8.5.5 (`iphoneos-arm64`, rootless)
- `crackATT.dylib` + `crackATT.plist` MobileSubstrate patch
- One-line install scripts for iOS (`install.sh`, `install-patch-only.sh`)
- `build_deb.py` with correct LZMA-alone compression for dpkg compatibility
- Full README and MIT license

### Fixed
- LZMA compression format (`FORMAT_ALONE` instead of XZ) — fixes `dpkg-deb: lzma error`
- Duplicate tar entries when building `.deb`
