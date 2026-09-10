# InvestiGator — current web identity

Approved direction, 9 September 2026: one-colour wordmark, matching I monogram,
no mascot. Supersedes the animal identity for the current website and prepared
Telegram assets. Historical thesis illustrations retain their original artwork.

- Website: `web/assets/wordmark.svg`, adapts to light/dark mode.
- Portable exports: `wordmark-light.svg` for light backgrounds;
  `wordmark-dark.svg` for dark backgrounds. Outlined letters require no installed font.
- Favicon: `web/assets/icon.svg`; reusable vector: `monogram.svg`.
- Telegram: `telegram-avatar.png`, 512 × 512, opaque green, circular-crop safe.

The wordmark and monogram use IBM Plex Sans SemiBold, already licensed and bundled
with the website. Font licence: `web/assets/fonts/LICENSE-OFL.txt`. The name uses
one weight and colour throughout; the avatar uses the existing #0a7f4f accent.
No extra symbol or slogan is added to the dashboard header.

Slogan: **Market moves, investigated.**

Prepared Telegram description:

> Market moves, investigated. Unusual price movements, relevant news and historical context—with evidence and uncertainty made clear.

The avatar and description are prepared locally; the Telegram channel has not been changed.

Regenerate from the repository root:

```powershell
.venv/Scripts/python.exe -m scripts.build_web_brand
```

This command generates only the current web assets and the exports in this directory.
Do not run `scripts/build_brand_assets.py` to update this identity: it maintains the
earlier artwork used by historical documents.
