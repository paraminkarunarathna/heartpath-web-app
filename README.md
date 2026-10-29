# HeartPath website



Download page for the HeartPath Android app (APK), in Sinhala, Tamil and English.
It's a plain static site: no build step, no framework, no tracking.

```
index.html            Home: download button, 5 install steps, features, screenshots, FAQ
privacy.html          Privacy policy (all three languages)
assets/css/styles.css All styles (mobile first)
assets/js/i18n.js     All text, per language — edit wording here
assets/js/main.js     Language switch, phone detection, QR code, download bar
                      APP = { version, size, file, sha256 } lives at the top
assets/img/           Icons (icons.svg), app icon, screenshots, link-preview image
assets/fonts/         App fonts as woff2 (Sinhala/Tamil load only when needed)
downloads/            The APK
tools/make_assets.py  Rebuilds images, icons and fonts from the app repo
```

## Preview on your computer

```bash
cd heartpath-website
python3 -m http.server 8000
```

Open http://localhost:8000. Add `?lang=si` or `?lang=ta` to test the other languages.
To test on a phone, connect it to the same Wi-Fi and open `http://<your-computer-ip>:8000`.

## Publish

Any static host works. Make sure it allows a file of about 71 MB:

| Host | Notes |
|---|---|
| **GitHub Pages** | Make the repository public, then go to **Settings → Pages → Deploy from branch** and choose `main` / root. Files must be under 100 MB. GitHub warns on files over 50 MB, but they still work. |
| **Netlify** | Drag the folder onto app.netlify.com/drop. |
| Cloudflare Pages | ⚠️ Limited to 25 MB per file. Host the APK somewhere else (e.g. a GitHub Release) and change `APP.file`. |

After publishing:

1. In `index.html`, change `og:image` to the full URL, e.g.
   `https://your-domain/assets/img/og-image.jpg`. WhatsApp and Facebook need a full
   URL to show the preview picture.
2. Open the site on an Android phone and do a real install from start to finish.

## Releasing a new app version

1. In the app repo, raise the build number in `pubspec.yaml` (e.g. `1.0.1+3`). It must
   always go up, or phones refuse the update.
2. Build with **the same signing key**. Otherwise phones won't install it over the
   old version, and users would have to uninstall and lose their data:
   ```bash
   flutter build apk --release
   ```
3. Copy `build/app/outputs/flutter-apk/app-release.apk` to
   `downloads/HeartPath-<version>.apk`, and delete the old file.
4. Get the size and checksum:
   ```bash
   ls -l downloads/*.apk
   shasum -a 256 downloads/HeartPath-<version>.apk
   ```
5. Update `APP` at the top of `assets/js/main.js` (version, build, sizeMB, file, sha256).
   Also update the `href="downloads/…apk"` links and the "71 MB" fallback text in
   `index.html`, which is shown before JavaScript loads.

## Editing text

All wording is in `assets/js/i18n.js`, under `en`, `si` and `ta`. Every key must exist
in all three. The English text also sits in the HTML, so the page still works without
JavaScript. If you change English wording, change it in both places.

Buttons that appear on the phone itself (“Install”, “Open”, “Download anyway”, “Allow
from this source”) are left in English on purpose, because most phones show them in
English.

> The Sinhala and Tamil text should be checked by a native speaker before launch.

## Rebuilding images and fonts

Needs Python with `pillow`, `fonttools` and `brotli`:

```bash
python3 -m venv /tmp/hp && /tmp/hp/bin/pip install pillow fonttools brotli
/tmp/hp/bin/python tools/make_assets.py ../HomeTele-CR .
```

App screenshots come from the app repo's `test_screenshots/goldens/`. Regenerate them
there first with `flutter test test_screenshots --update-goldens`.
