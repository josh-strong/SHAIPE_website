# Contributing to the SHAIPE Website (no coding experience needed)

This guide shows you how to update the site using an AI assistant ("vibe‑coding") with Cursor or GitHub Copilot. You'll fork the repo, edit locally with AI help, preview, then open a Pull Request (PR) for review.

## What you need
- A GitHub account: https://github.com
- Git installed (Mac: Xcode Command Line Tools or `brew install git`)
- Python 3 (for the local preview server)
- One of:
  - Cursor: https://www.cursor.com/ (recommended)
  - VS Code + GitHub Copilot extension (free for many `.ac.uk` emails)

---

## 1) Fork the repository (creates your copy)
1. Visit: https://github.com/josh-strong/SHAIPE_website
2. Click "Fork" (top‑right) to create a fork under your account.

![GitHub fork button – screenshot placeholder](docs/images/01_fork.png)

Reference: https://docs.github.com/repositories/creating-and-managing-repositories/forking-a-repository

---

## 2) Clone your fork to your computer
Replace YOUR_USERNAME with your GitHub username.

```bash
# In Terminal
git clone https://github.com/YOUR_USERNAME/SHAIPE_website.git
cd SHAIPE_website
# Point back to the original repo so you can sync later
git remote add upstream https://github.com/josh-strong/SHAIPE_website.git
```

---

## 3) Create a new branch for your change
```bash
git checkout -b feature/your-change
```

---

## 4) Open the project in Cursor or VS Code
- Cursor: Open Cursor → File → Open Folder → select the `SHAIPE_website` folder.
- VS Code: Open folder, install GitHub Copilot (View → Extensions → search for "GitHub Copilot").

Examples of what to ask the AI
- "Increase the homepage hero logo size by 10%."
- "Add an item to the navigation linking to Events."
- "Update People page with a new member (name, role, photo)."
- "Improve mobile menu spacing on iPhone."

Tip: Mention the file you want to edit (e.g. `index.html`, `assets/css/styles.css`).

---

## 5) Preview locally
From the project folder, run:
```bash
python3 -m http.server 8080
```
Open http://localhost:8080 in your browser. Refresh after each change. Use Cmd/Ctrl+Shift+R for a hard refresh if needed.

---

## 6) Commit your changes
```bash
git add -A
git commit -m "Describe your change clearly"
```

---

## 7) Push to your fork
```bash
git push -u origin feature/your-change
```

---

## 8) Open a Pull Request (PR)
1. Go to your fork on GitHub. You should see a prompt to "Compare & pull request".
2. Write a short description and submit the PR to `josh-strong/SHAIPE_website`.

Reference: https://docs.github.com/pull-requests/collaborating-with-pull-requests

---

## 9) Keep your fork in sync (optional)
If the main site changes, update your fork:
```bash
git checkout main
git fetch upstream
git merge upstream/main
# or: git rebase upstream/main
```

---

## Quick edit (no local setup)
- Edit files directly on GitHub: open a file (e.g. `people.html`) → click the pencil icon → make your edit → "Commit changes" → open a PR.
- For larger or multi‑file changes, prefer Cursor or VS Code so you can preview locally.

---

## Project structure (what to edit)
- `index.html` — Home
- `about.html`, `people.html`, `research.html`, `publications.html`, `news.html`, `events.html`, `contact.html`
- `assets/css/styles.css` — Styles (colours, layout, typography)
- `assets/js/main.js` — Small interactivity (mobile nav)
- `assets/img/` — Images (logo, favicons, people photos)

## Accessibility and style
- Use British English.
- Keep good contrast (AA or better).
- Keep the Oxford Blue palette:
  - Primary: `#002147`
  - Accent: `#0f4d92`

If unsure, ask the AI assistant to "implement the change accessibly and consistently with the site style".

## Starter prompts to copy‑paste
- "Open `people.html`. Add \"Professor Jane Doe — Clinical AI Fellow\" under Members; insert photo from `assets/img/jane-doe.jpg`, rounded corners, matching existing style."
- "Tighten header spacing on mobile; ensure the menu does not shift layout when opened."
- "Create a `news.html` entry dated today titled \"Workshop on Trustworthy AI\" with a short paragraph and a signup link."

---

If you get stuck at any step, open an issue on GitHub or ask in the team channel; we're happy to help.
