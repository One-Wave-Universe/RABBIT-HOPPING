# Virtual Breadboard — Android Build Audit

## What exists

- `Virtual_Breadboard/android/VirtualBreadboardSimulator.apk` — signed APK, ~54KB, WebView host loading the same `index.html`/`js` bundle.
- `android/build-apk.sh` — rebuilds via `aapt` + `smali` + `zipalign` + `apksigner` (no Android Studio/Gradle).
- `android/src/.../MainActivity.java` + `smali/.../MainActivity.smali` — single Activity, loads local assets.

## Audit result (this pass)

Cannot execute the APK or `build-apk.sh` in this environment (no Android SDK / aapt / device / emulator). The build path is documented and self-contained; it is **not verified runnable here**.

## What would upgrade it

1. Add a headless test harness: `node simulate.js` (already referenced in README) to run circuit solves without a browser.
2. Add Rabbit Hopping memory-core test boards: wire Memory Core parts into a small lattice, assert remanence + induced voltage on sense winding.
3. Add CI that runs `build-apk.sh` on a Linux runner with `aapt zipalign apksigner` installed.
4. Expose `window.__runFast(...)` as a stable CLI for AI-driven bring-up.

## Status

YELLOW — documented, not executed. Do not claim the Android build is verified until a runner actually produces and installs the APK.
