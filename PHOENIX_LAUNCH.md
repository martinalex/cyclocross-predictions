# The Phoenix Launch: 90-Day AI Product Ecosystem Experiment

## Mission Statement
Validate a three-platform AI ecosystem in 90 days: VeloPredict (personal), VeloIntel (consumer), and WellnessAI (enterprise). Test business viability while building portfolio-grade products that demonstrate Principal PM capabilities for consulting firm roles.

## The Ecosystem Vision

### How The Three Platforms Connect

**VeloPredict → VeloIntel → WellnessAI**  
Each platform builds on the last, creating a data flywheel and revenue progression:

1. **VeloPredict** (Foundation)
   - AI predicts cycling race outcomes based on historical data
   - Validates core ML capabilities with measurable accuracy
   - Establishes credibility in sports analytics
   - **Output:** Prediction models + cycling domain expertise

2. **VeloIntel** (Consumer Layer)
   - AI analyzes personal wearables data (Strava, Garmin, Wahoo, Oura, etc.)
   - Suggests personalized workouts based on performance patterns
   - Uses VeloPredict's race models to optimize training for specific events
   - **Output:** Consumer app with subscription model

3. **WellnessAI** (Enterprise Layer)
   - Retailers adopt platform to reward customers with loyalty points for workout completion
   - Integrates VeloIntel's wearables data pipeline for verification
   - Leverages my 15+ years loyalty program experience (Albertsons, Macy's, T-Mobile)
   - **Output:** B2B licensing + consulting engagement opportunity

### Strategic Progression
**Personal → Consumer → Enterprise**  
**Free tool → Subscription → B2B licensing**  
**Portfolio piece → Viable business → Consulting channel**

---

## AI Technology Architecture

### Technology Selection Philosophy
Each platform uses the **right tool for the job**, not the most impressive-sounding tech. This section maps which AI technologies genuinely fit each platform versus what would be overkill.

### Platform Technology Matrix

| Technology | VeloPredict | VeloIntel | WellnessAI | Why |
|------------|:-----------:|:---------:|:----------:|-----|
| **Gradient Boosted Trees (XGBoost/LightGBM)** | ★★★ Core | ★★ Baseline | ★★★ Core | Tabular data champion, interpretable, fast |
| **Random Forest / Logistic Regression** | ★★★ Core | ★★ Baseline | ★★★ Core | Strong baselines, explainability matters |
| **Time Series Deep Learning (LSTM/TCN)** | ★★ Form modeling | ★★★ Core | ★ Engagement patterns | Wearables data is sequential |
| **Transformers for Time Series** | ★ Maybe later | ★★★ Core | ★ Optional | Multi-modal sensor fusion |
| **Embeddings / Representation Learning** | ★ Rider similarity | ★★★ Core | ★★★ Core | Session/user/content representations |
| **Recommender Systems (Two-Tower, CF)** | — | ★★★ Core | ★★★ Core | Next workout, next reward |
| **RAG (Retrieval-Augmented Generation)** | ★★ Race context | ★★★ Training KB | ★★★ Program rules | Ground LLMs in domain knowledge |
| **LLM Generation** | ★★ Narratives | ★★★ Coach UX | ★★★ Copilot UX | Natural language interfaces |
| **Agents (Tool-Calling LLMs)** | ★ Reports | ★★★ Proactive coach | ★★ Campaign workflows | Autonomous multi-step tasks |
| **Contextual Bandits** | — | ★★ Notification timing | ★★★ Core | Real-time offer optimization |
| **Causal / Uplift Modeling** | — | — | ★★★ Very relevant | ROI measurement, incrementality |

**Legend:** ★★★ = Core/Essential | ★★ = Strong fit | ★ = Optional/Later | — = Skip

### Platform-Specific Technology Decisions

#### VeloPredict: Classical ML Focus
**Core Stack:** Gradient Boosted Trees, Feature Engineering, Probability Calibration

**Why NOT deep learning here:**
- Limited data volume (hundreds of races, not millions)
- Tabular structured data (GBMs outperform neural nets)
- Explainability matters for credibility
- 90% Top-10 accuracy at Tabor validates this approach

**LLM/RAG Role:** Supporting, not core
- RAG over race notes and course descriptions
- LLM generates prediction narratives for content
- Simple agent orchestrates prediction reports

**Skip:** Deep RL, GANs, heavy computer vision

---

#### VeloIntel: Modern AI Full Stack
**Core Stack:** Time Series Neural Networks, Embeddings, LLM + Tools, RAG, Agents

**Why deep learning fits here:**
- Continuous sensor data (HR, power, HRV, sleep) is sequential
- Pattern recognition across multiple data streams
- Personalization requires learned representations
- Conversational interface is the product

**Key Technical Components:**
1. **Time Series Models** — LSTM/TCN on daily metrics predicts readiness, fatigue, injury risk
2. **Session Embeddings** — Learned representations of workouts enable similarity search
3. **RAG Knowledge Base** — Training principles, periodization theory, recovery guidelines
4. **AI Coach Agent** — Calls readiness models, recommender, and RAG to generate weekly plans

**Skip:** Multi-agent orchestration (one capable agent is enough), full RL training optimization

---

#### WellnessAI: Enterprise AI Patterns
**Core Stack:** Propensity Models, Recommender Systems, Contextual Bandits, Causal Inference

**Why this stack:**
- Enterprise buyers care about ROI, not model complexity
- Bandits optimize offers in real-time (next-best-action done right)
- Uplift modeling proves incrementality (consulting-firm-sexy)
- LLM copilot makes analytics accessible to non-technical stakeholders

**Key Technical Components:**
1. **Propensity Models** — Likelihood to join, complete, respond to challenges
2. **Two-Tower Recommender** — Next-best challenge, next-best reward
3. **Contextual Bandits** — Real-time offer optimization with exploration
4. **Uplift/Causal Models** — Measure true incremental impact on behavior
5. **LLM Analyst Copilot** — Natural language queries over metrics

**Skip:** Complex RL simulation, vision models (unless receipt scanning later)

### Cross-Platform Shared Infrastructure

These components are built once and reused across all three platforms:

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| **Feature Store** | Shared embeddings for riders, athletes, customers | Redis + PostgreSQL |
| **Vector Database** | Namespaced: courses, training knowledge, loyalty rules | Pinecone or Chroma |
| **Model API Layer** | `/predict`, `/recommend`, `/optimize` endpoints | FastAPI |
| **Observability** | Data drift detection, performance dashboards | Custom + Weights & Biases |
| **Explainability** | SHAP values fed into LLM explanations | SHAP + prompt templates |
| **Phoenix Copilot** | Unified LLM interface to query all three platforms | Claude API + tools |

### Technology Learning Path (Aligned to 90 Days)

#### Phase 1: VeloPredict (Days 1-30)
**Learn:**
- Data scraping, PDF parsing, feature engineering
- Logistic regression → Random Forest → GBMs
- Time series features (rolling stats, exponential moving averages)
- Model evaluation (Brier score, log loss, calibration)
- Wrap model in FastAPI endpoint
- Simple LLM explanation layer

**Milestone:** 80%+ prediction accuracy, deployed demo

---

#### Phase 2: VeloIntel (Days 31-60)
**Learn:**
- Time series deep learning (LSTM, Temporal CNN)
- Embedding spaces and similarity search
- Basic recommender system concepts (user/item embeddings)
- RAG architecture with training knowledge base
- LLM + tool calling patterns
- Agent that orchestrates multiple models

**Milestone:** Working AI coach with Strava integration, 5 beta users

---

#### Phase 3: WellnessAI (Days 61-90)
**Learn:**
- Enterprise-scale propensity modeling
- Two-tower recommender systems
- Contextual bandits for real-time optimization
- Causal inference / uplift modeling basics
- LLM copilot over metrics APIs
- Multi-tenant architecture patterns

**Milestone:** Retailer demo, consulting firm pitch deck with technical depth

### What to Explicitly Skip (Across All Platforms)

| Technology | Why Skip |
|------------|----------|
| GANs / Diffusion Models | No image generation use case |
| Complex Multi-Agent Systems | One capable agent with tools is sufficient |
| Full Reinforcement Learning | Bandits + rules get 80% of value at 20% complexity |
| Heavy Computer Vision | Not core to any platform (maybe later for form analysis) |
| Transformer-based tabular models | GBMs still win on structured data at this scale |

---

## Success Criteria (90 Days)

### Business Validation
**Primary Question:** Can this become a viable business, or is it a portfolio asset?

**Validation Metrics:**
- [ ] 10+ competitive cyclists actively using VeloPredict
- [ ] 5+ cyclists willing to pay $10-20/month for VeloIntel
- [ ] 2+ retailers express interest in WellnessAI pilot
- [ ] Revenue generated (even $1 proves monetization)
- [ ] Consulting firm (McKinsey/Deloitte) interest in distribution partnership

**Portfolio Metrics:**
- [ ] GitHub repository with production-quality code
- [ ] LinkedIn case study series generating engagement
- [ ] Working demos for all three platforms
- [ ] Technical documentation showing PM + Builder credibility

### Technical Validation (NEW)
- [ ] VeloPredict: 80%+ accuracy with explainable GBM model
- [ ] VeloIntel: Time series model outperforms baseline on readiness prediction
- [ ] VeloIntel: RAG reduces hallucination in training advice
- [ ] WellnessAI: Bandit outperforms random assignment in A/B test
- [ ] WellnessAI: Uplift model shows measurable incrementality

## Platform 1: VeloPredict (Days 1-30)

### Product Vision
AI-powered cycling race prediction platform. Predicts individual rider performance and race outcomes using historical race data, weather conditions, and rider statistics.

### Why This First?
- Validates core ML capabilities with measurable accuracy (80%+ target)
- Smallest scope - can ship fast
- Establishes domain expertise in cycling analytics
- Creates foundation for VeloIntel training recommendations

### Technical Requirements
- Web scraping pipeline for race results
- PDF extraction for rider statistics (PDFPlumber)
- Pandas data cleaning and feature engineering
- Scikit-learn prediction models (Random Forest → XGBoost)
- Probability calibration (Platt scaling)
- Jupyter notebooks → production Python modules
- FastAPI endpoint for predictions
- Basic web interface for predictions

### 30-Day Milestones
- [ ] Week 1: Complete data pipeline (scraping + cleaning)
- [ ] Week 2: Baseline prediction model (60%+ accuracy)
- [ ] Week 3: Optimized model (80%+ accuracy) with calibrated probabilities
- [ ] Week 4: Deployed demo + validation with 10 cyclists

### Distribution
- Free tool with GitHub source code
- LinkedIn content: "Building AI Race Predictions"
- Proof of concept for VeloIntel's training algorithms

## Platform 2: VeloIntel (Days 31-60)

### Product Vision
Personal AI coach that analyzes wearables data from Strava, Garmin, Wahoo, Oura to suggest optimal workouts. Uses VeloPredict's race models to train cyclists for specific events.

### Why This Second?
- Builds on VeloPredict's prediction algorithms
- Tests consumer subscription willingness ($10-20/month)
- Creates wearables data pipeline needed for WellnessAI
- Validates product-market fit before enterprise pitch

### Technical Requirements
- OAuth integrations (Strava, Garmin, Wahoo, Oura APIs)
- Data aggregation across multiple wearables platforms
- Time series models for readiness/fatigue prediction
- Embedding-based workout recommender
- RAG over training knowledge base
- LLM-powered conversational coach interface
- User dashboard showing insights + recommendations
- Subscription payment system (Stripe)

### 30-Day Milestones
- [ ] Week 1: Strava integration + time series baseline model
- [ ] Week 2: AI recommendation engine with embeddings
- [ ] Week 3: RAG + conversational coach interface
- [ ] Week 4: Beta test with 20 cyclists, convert 5 to paid

### Distribution
- Freemium model: Basic predictions free, advanced coaching $15/month
- LinkedIn content: "Personal AI Coaching from Your Wearables"
- Direct outreach to cycling clubs and Strava communities

## Platform 3: WellnessAI (Days 61-90)

### Product Vision
Enterprise loyalty platform for retailers. Customers earn loyalty points when they complete verified workouts tracked via wearables. Retailers increase engagement, customers get rewarded for healthy behavior.

### Why This Third?
- Leverages VeloIntel's wearables verification infrastructure
- Taps into my 15+ years loyalty program expertise
- Creates consulting engagement opportunity with retailers
- Positions platform for McKinsey/Deloitte distribution channel

### Business Model
- B2B licensing to retailers ($5K-50K/month based on customer base)
- Consulting on loyalty program integration (my expertise)
- White-label option for larger retailers
- Revenue share on increased customer engagement

### Technical Requirements
- Multi-tenant architecture for retailers
- Wearables data verification (reuse VeloIntel pipeline)
- Propensity models for challenge completion prediction
- Two-tower recommender for challenges and rewards
- Contextual bandit for real-time offer optimization
- Uplift modeling for ROI measurement
- LLM analyst copilot for retailer stakeholders
- Points calculation and reward distribution system
- Retailer admin dashboard
- Customer mobile app (rewards tracking)
- Integration with retailer loyalty systems

### 30-Day Milestones
- [ ] Week 1: Retailer pitch deck + ROI model with uplift framework
- [ ] Week 2: MVP with bandit-based offer selection
- [ ] Week 3: Wearables verification + points system working
- [ ] Week 4: Demo to 3 retailers + 2 consulting firms

### Distribution Strategy
**Primary Channel:** Consulting firms (McKinsey, Deloitte, Accenture)
- They recommend loyalty solutions to retail clients
- WellnessAI becomes implementation partner
- I position as PM + Implementation consultant

**Direct Sales:** Regional retailers and gym chains
- Prove concept with smaller players
- Case studies for enterprise pitch

## The Interconnected Data Flywheel
```
VeloPredict (Race Data) 
    ↓
Prediction Models + Cycling Analytics
    ↓
VeloIntel (Personal Wearables Data)
    ↓
Workout Recommendations + Verification
    ↓
WellnessAI (Enterprise Loyalty Platform)
    ↓
More Users = More Data = Better Models
    ↓
Improved VeloPredict Accuracy
```

## 90-Day Decision Framework

### Pivot to Business If:
✅ Revenue generated (any amount proves monetization)  
✅ 5+ paying VeloIntel users  
✅ 1+ retailer pilot signed for WellnessAI  
✅ Consulting firm expresses partnership interest  
✅ Strong engagement on LinkedIn content (building audience)

### Portfolio Asset If:
⚠️ No revenue after 90 days  
⚠️ Low user engagement (<10 active users)  
⚠️ No retailer interest in WellnessAI  
⚠️ Better PM offers come through before validation

**Either outcome is success:**
- Business path: Continue building, raise funding, or bootstrap
- Portfolio path: Landed Principal PM role using credibility established

## Technical Stack (Entire Ecosystem)

**Core ML/AI:**
- Python, Pandas, NumPy (data processing)
- Scikit-learn (classical ML, baselines)
- XGBoost/LightGBM (gradient boosting)
- PyTorch (deep learning when needed)
- HuggingFace Transformers (time series transformers)
- LangChain or raw Claude API (LLM orchestration)

**Backend:**
- FastAPI (model serving + APIs)
- PostgreSQL (relational data)
- Redis (caching, feature store)
- Pinecone or Chroma (vector database for RAG)

**Frontend:**
- React (web dashboards)
- React Native or Flutter (mobile if needed)

**Wearables Integrations:**
- Strava API
- Garmin Connect API
- Wahoo API
- Oura Ring API

**Infrastructure:**
- GitHub (version control + portfolio)
- Vercel/Railway (deployment)
- Stripe (payments)
- Weights & Biases (ML experiment tracking)
- AWS/GCP (production scaling if needed)

**Development:**
- VS Code + Claude Code (AI pair programming)
- Jupyter (exploratory analysis)
- Google Colab (GPU for training)

## Code Quality Standards

**Remember:** This code will be reviewed by:
- ✅ Consulting firm technical teams (McKinsey Digital, Deloitte Tech)
- ✅ Potential co-founders or investors (if business path)
- ✅ Hiring managers for Principal PM roles (if portfolio path)

**Standards:**
- Production-ready, not prototype quality
- Modular, reusable, well-documented
- Professional git commits (tell the story)
- Security best practices (API keys, user data)
- Scalable architecture (even if MVP functionality)
- Clear separation: notebooks for exploration, .py for production

## Success Metrics Dashboard

### Week 4 (VeloPredict)
- Prediction accuracy: ___% (target: 80%+)
- Brier score: ___ (target: <0.2)
- Cyclists validated with: ___ (target: 10)
- GitHub stars: ___
- LinkedIn post engagement: ___

### Week 8 (VeloIntel)
- Active beta users: ___ (target: 20)
- Paying subscribers: ___ (target: 5)
- Wearables integrations working: ___ (target: 2+)
- Readiness model accuracy: ___% 
- MRR (Monthly Recurring Revenue): $___

### Week 12 (WellnessAI)
- Retailer pilots: ___ (target: 1)
- Consulting firm meetings: ___ (target: 2)
- Bandit lift over random: ___% 
- Total revenue generated: $___
- Decision: ☐ Business ☐ Portfolio

## Current Status

**Completed:**
- ✅ Phoenix Launch strategy defined
- ✅ AI technology architecture mapped
- ✅ VS Code + Claude Code environment setup
- ✅ Initial race prediction notebook with pandas
- ✅ PDF scraping pipeline started
- ✅ First live test: 90% Top-10 accuracy at Tabor

**This Week:**
- [ ] Complete data extraction pipeline
- [ ] Clean and structure race data
- [ ] Build baseline prediction model
- [ ] Validate approach with test races

**This Month:**
- [ ] Achieve 80%+ prediction accuracy
- [ ] Refactor to production modules
- [ ] Deploy working demo
- [ ] LinkedIn case study: "Building VeloPredict"

## Why This Approach Works

**For Consulting Firms:**
Shows end-to-end product thinking from personal tool → consumer app → enterprise platform. Demonstrates understanding of market progression, monetization strategies, AND appropriate technology selection.

**For Technical Credibility:**
GitHub portfolio proves "this PM actually codes." Technology choices show I understand when to use classical ML vs. deep learning vs. LLMs — not just chasing trends.

**For Business Validation:**
90 days is enough to test demand signals without overcommitting. Clear pivot criteria based on metrics, not hope.

**For Personal Growth:**
Regardless of outcome, I'll have shipped three AI products using progressively sophisticated technology stacks, documented the entire process publicly on LinkedIn.

## The Real Win

**If it's a business:** I'm solving a real problem with paying customers  
**If it's a portfolio:** I'm a Principal PM who builds AI products with the right tech for each problem  
**Either way:** I'm unemployable at companies that don't value builders

---

*Let's build something real.*