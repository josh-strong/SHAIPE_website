# SHAIPE Website – Quickstart for Editors

This is the fastest way to make a small change and open a Pull Request (PR).

1) Fork the repo
- Go to https://github.com/josh-strong/SHAIPE_website → click Fork.
![Fork screenshot placeholder](images/01_fork.png)

2) Clone your fork
```bash
git clone https://github.com/YOUR_USERNAME/SHAIPE_website.git
cd SHAIPE_website
```
![Clone screenshot placeholder](images/02_clone.png)

3) Create a branch
```bash
git checkout -b fix/typo-or-small-change
```

4) Open in Cursor (or VS Code + Copilot)
- Ask the AI to help you: e.g. "Fix the typo on the homepage header."
![Cursor screenshot placeholder](images/03_cursor.png)

5) Preview locally
```bash
python3 -m http.server 8080
```
Open http://localhost:8080
![Preview screenshot placeholder](images/04_preview.png)

6) Commit and push
```bash
git add -A
git commit -m "Fix: homepage typo"
git push -u origin fix/typo-or-small-change
```

7) Open a PR
- On GitHub, click "Compare & pull request" and submit.
![PR screenshot placeholder](images/05_open_pr.png)

Done! A maintainer will review and merge your change.
