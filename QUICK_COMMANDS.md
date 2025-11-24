# Quick Reference: Git & GitHub Commands

## 🎯 FIRST TIME SETUP (Do This Now)

### 1. Create GitHub Repository
Go to: https://github.com/new

**Settings:**
- Name: `cyclocross-predictions`
- Description: `AI-powered cyclocross race predictions with 80.2% Top-10 accuracy`
- Public repo
- Do NOT initialize with anything

### 2. Connect & Push (Replace YOUR-USERNAME)
```bash
# Add your GitHub repo as remote
git remote add origin https://github.com/YOUR-USERNAME/cyclocross-predictions.git

# Push your code
git push -u origin main
```

Done! Your code is now on GitHub.

---

## 📝 DAILY WORKFLOW (After Sunday's Race)

### After you validate predictions:

```bash
# See what changed
git status

# Add all changes
git add .

# Commit with message
git commit -m "Tabor validation: 75% Top-10 accuracy

- Validated predictions on UCI World Cup Tabor
- Men Elite: 7/10 correct
- Women Elite: 8/10 correct
- Updated README with results"

# Push to GitHub
git push
```

---

## 🔍 USEFUL COMMANDS

### Check what's in your repo
```bash
git log --oneline          # See commit history
git status                 # See current changes
git diff                   # See what changed
```

### Made a mistake?
```bash
git reset HEAD~1           # Undo last commit (keep changes)
git checkout -- filename   # Discard changes to a file
```

### See your remote URL
```bash
git remote -v              # Shows your GitHub URL
```

---

## 📊 YOUR CURRENT STATUS

✅ Git initialized locally
✅ First commit created (150 files)
✅ All code ready to push

⏳ Waiting for you to:
1. Create GitHub repo at https://github.com/new
2. Run the "Connect & Push" commands above

---

## 🎯 AFTER GITHUB PUSH

Your repo will be at:
```
https://github.com/YOUR-USERNAME/cyclocross-predictions
```

**Share this URL:**
- LinkedIn posts
- Reddit comments
- Resume/portfolio
- Consulting firm applications

---

## 📱 QUICK LINKS

**Create repo:** https://github.com/new
**Your repos:** https://github.com/YOUR-USERNAME?tab=repositories
**Full guide:** See GITHUB_SETUP.md

---

*Need help? Just ask!*
