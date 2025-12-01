# Streamlit Cloud Deployment Guide

**Quick 5-minute deployment to make VeloPredict publicly accessible**

---

## Prerequisites

- ✅ Models retrained (you just did this!)
- ✅ Code in GitHub repository
- ✅ Streamlit account (free)

---

## Step 1: Prepare for Deployment

### Install Streamlit Locally (Optional - for testing)

```bash
pip install streamlit plotly
```

### Test Locally First

```bash
streamlit run app/demo.py
```

This should open http://localhost:8501 in your browser.

**Verify:**
- ✅ Models load successfully
- ✅ Predictions work for sample riders
- ✅ Metrics display correctly (79.2% accuracy, Brier score 0.1569)

---

## Step 2: Push to GitHub

```bash
# Add all new files
git add .

# Commit with descriptive message
git commit -m "Add v4 calibrated model + FastAPI + production structure

- Added Platt scaling calibration (Brier: 0.1569)
- Created FastAPI REST API (src/api/)
- Reorganized file structure (src/, notebooks/)
- Updated README with 'Why Classical ML' rationale
- Retrained model: 79.2% accuracy, 93.1% Top-3

Ready for Streamlit deployment and consulting firm review."

# Push to GitHub
git push origin main
```

---

## Step 3: Deploy to Streamlit Cloud

### 3.1 Go to Streamlit Cloud

1. Visit: https://share.streamlit.io
2. Sign in with GitHub account
3. Click "New app"

### 3.2 Configure Deployment

**Repository:** Select your cyclocross-predictions repo

**Branch:** `main`

**Main file path:** `app/demo.py`

**Python version:** 3.12 (or 3.11 if 3.12 not available)

### 3.3 Advanced Settings (Optional)

If you need to specify Python version or additional packages:

Create `.streamlit/config.toml` (optional):
```toml
[server]
headless = true
enableCORS = false
```

---

## Step 4: Deploy!

Click **"Deploy"**

**What happens:**
1. Streamlit Cloud clones your repo
2. Installs dependencies from requirements.txt
3. Runs `streamlit run app/demo.py`
4. Gives you a public URL

**Deployment time:** 2-3 minutes

---

## Step 5: Get Your Public URL

Once deployed, you'll get a URL like:
```
https://[your-username]-cyclocross-predictions-[hash].streamlit.app
```

**Share this URL:**
- LinkedIn post
- User testing with cyclists
- Portfolio / resume
- Consulting firm presentations

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'pandas'"

**Fix:** Ensure requirements.txt is in repo root and contains:
```
pandas==2.2.0
numpy==1.26.3
scikit-learn==1.4.0
streamlit==1.30.0
plotly==5.18.0
joblib==1.3.2
```

### Error: "FileNotFoundError: models/top10_classifier.joblib"

**Fix:** Ensure models are committed to GitHub:
```bash
git add models/*.joblib models/*.json
git commit -m "Add trained models"
git push
```

### Error: "App is too slow"

**Options:**
1. Reduce model size (not needed - your models are fine)
2. Use `@st.cache_resource` for model loading (already done!)
3. Upgrade to Streamlit Cloud paid tier (not needed for MVP)

### Models are too large for GitHub (>100MB)

**Fix:** Use Git LFS:
```bash
# Install Git LFS
git lfs install

# Track model files
git lfs track "models/*.joblib"
git add .gitattributes
git commit -m "Track models with Git LFS"
git push
```

---

## Post-Deployment

### 1. Test Your Live App

Visit your Streamlit URL and verify:
- ✅ Models load (check sidebar metrics)
- ✅ Sample predictions work
- ✅ Live validation stats show (Tabor 90%)
- ✅ Calibration info displays (Brier: 0.1569)

### 2. Update Documentation

Add the live URL to:
- [README.md](README.md) (Quick Start section)
- [CURRENT_VERSION.md](CURRENT_VERSION.md) (Deployment Status section)
- LinkedIn profile / portfolio

### 3. Monitor Usage

Streamlit Cloud dashboard shows:
- Daily active users
- Page views
- Errors (if any)

---

## Custom Domain (Optional)

### Free Custom Domain Options:

1. **Streamlit Sharing Custom Domain**
   - Not available on free tier

2. **Use Vercel/Netlify for Frontend + API**
   - Deploy Streamlit on Streamlit Cloud
   - Deploy static landing page on Vercel
   - Link with subdomain

3. **Keep Streamlit URL**
   - Most users won't care
   - Focus on functionality over vanity URL

---

## Maintenance

### Updating the Deployed App

**Automatic Updates:**
- Push to GitHub → Streamlit auto-redeploys
- No manual intervention needed

**Force Reboot:**
- Streamlit Cloud dashboard → "Reboot app"

**View Logs:**
- Streamlit Cloud dashboard → "Logs"

---

## Alternative: Local Network Demo

If you can't deploy publicly yet:

```bash
# Share on local network
streamlit run app/demo.py --server.address 0.0.0.0

# Get your local IP
# Mac: ifconfig | grep "inet "
# Access from other devices: http://[your-ip]:8501
```

---

## Success Checklist

Before sharing with users:

- [ ] Live URL works from any browser
- [ ] Predictions are accurate (test with known riders)
- [ ] Metrics display correctly
- [ ] No errors in Streamlit logs
- [ ] README updated with live link
- [ ] LinkedIn post drafted mentioning live demo

---

## What to Share

**LinkedIn Post Template:**

```
🚀 VeloPredict is now live!

I built an AI to predict cyclocross race results - now deployed for anyone to test.

📊 Performance:
• 79% Top-10 accuracy (test set)
• 90% accuracy on live UCI World Cup races
• Brier score: 0.1569 (excellent calibration)

🧠 Tech Stack:
• Random Forest + Platt Scaling calibration
• 47 races, 7,793 observations
• FastAPI backend + Streamlit frontend

🎯 Try it: [Your Streamlit URL]

This is Phase 1 of my 90-day AI product experiment.
Full code on GitHub: [Your repo URL]

#MachineLearning #AI #ProductManagement #Cyclocross
```

---

## Next Steps After Deployment

1. **User Validation**
   - Share with 10+ cyclists
   - Collect feedback on accuracy
   - Ask willingness to pay

2. **Live Race Testing**
   - Generate predictions for next UCI race
   - Validate post-race
   - Update accuracy stats

3. **Phase 2 Planning**
   - VeloIntel (wearables AI coach)
   - Time series models
   - Subscription model

---

**You're now 95% complete with Phase 1!** 🎉

The last 5%:
- Deploy to Streamlit (5 minutes)
- Share on LinkedIn (5 minutes)
- Get user feedback (ongoing)

Then move to Phase 2 (VeloIntel) or pivot to consulting firm interviews with a killer portfolio.
