# Data analyst portfolio — Munashe Makuyana

Static site showcasing data analytics projects. Built with plain HTML/CSS (no build step needed).

## Structure

```
portfolio/
├── index.html                      # homepage
├── css/style.css                   # shared styles
├── projects/
│   ├── etl-pipeline.html           # case study 01 (live)
│   └── etl-pipeline/               # the actual project code + data
│       ├── etl_pipeline.py
│       ├── README.md
│       └── data/
└── README.md
```

## Deploying to GitHub Pages

1. Create a new GitHub repo (e.g. `portfolio` or `<yourusername>.github.io`).
2. Push this folder's contents to the repo root:
   ```bash
   git init
   git add .
   git commit -m "Initial portfolio site"
   git branch -M main
   git remote add origin https://github.com/<yourusername>/<repo-name>.git
   git push -u origin main
   ```
3. In the repo, go to **Settings → Pages**.
4. Under **Source**, select the `main` branch and `/ (root)` folder, then save.
5. Your site will be live at `https://<yourusername>.github.io/<repo-name>/` (or `https://<yourusername>.github.io/` if you named the repo `<yourusername>.github.io`).

## Next projects to add

- `projects/sales-dashboard.html` — Financial Performance & Sales Analytics Dashboard
- `projects/iot-maintenance.html` — IoT Equipment Performance & Predictive Maintenance

Follow the same pattern as `etl-pipeline.html`: real data, real numbers, a short "problem → pipeline → results" structure.
