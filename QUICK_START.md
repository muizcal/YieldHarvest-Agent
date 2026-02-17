# 🚀 QUICK START GUIDE - YieldHarvest Agent

## ⏰ You have ~3 days until submission deadline (Feb 19, 3:00 PM UTC)

This guide will get you from zero to deployed in **2-4 hours**.

---

## 📋 Prerequisites Checklist

Before starting, make sure you have:

- [ ] Node.js 18+ installed
- [ ] Python 3.10+ installed
- [ ] Git installed
- [ ] BNB for gas fees (~0.5 BNB)
- [ ] BSC RPC URL (free from https://chainlist.org)
- [ ] Private key with BNB (NEVER commit this!)
- [ ] (Optional) Anthropic API key for AI decision-making
- [ ] (Optional) BscScan API key for verification

---

## 🎯 Step-by-Step Deployment

### Step 1: Clone & Setup (5 minutes)

```bash
# Clone the repository
git clone <your-repo-url>
cd yieldharvest-agent

# Install Node dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### Step 2: Configure Environment (5 minutes)

Edit `.env` file with your details:

```bash
# CRITICAL: Add your private key (keep this secret!)
PRIVATE_KEY=your_private_key_here

# BSC RPC (get free one from chainlist.org)
BSC_RPC_URL=https://bsc-dataseed1.binance.org

# Optional but recommended
ANTHROPIC_API_KEY=your_claude_api_key  # For AI decisions
BSCSCAN_API_KEY=your_bscscan_key       # For verification

# These will be filled after deployment
VAULT_MANAGER_ADDRESS=
SESSION_KEY_MANAGER_ADDRESS=
DECISION_LOGGER_ADDRESS=
```

### Step 3: Deploy Contracts (10 minutes)

```bash
# Compile contracts
npx hardhat compile

# Deploy to BSC mainnet
npx hardhat run scripts/deploy.ts --network bsc

# ⚠️ SAVE THE OUTPUT! You'll need these addresses
```

**Expected Output:**
```
SessionKeyManager:  0x123...
DecisionLogger:     0x456...
YieldVaultManager:  0x789...
```

### Step 4: Update Environment (2 minutes)

Copy the deployed addresses to your `.env`:

```bash
VAULT_MANAGER_ADDRESS=0x789...
SESSION_KEY_MANAGER_ADDRESS=0x123...
DECISION_LOGGER_ADDRESS=0x456...
```

### Step 5: Verify Contracts (15 minutes)

```bash
# Verify on BscScan (makes your submission look professional)
npx hardhat verify --network bsc <SESSION_KEY_MANAGER_ADDRESS>
npx hardhat verify --network bsc <DECISION_LOGGER_ADDRESS>
npx hardhat verify --network bsc <VAULT_MANAGER_ADDRESS> <SESSION_KEY_MANAGER_ADDRESS> <DECISION_LOGGER_ADDRESS> <YOUR_ADDRESS>
```

### Step 6: Start the Agent (2 minutes)

```bash
# In terminal 1: Start the agent
python agent/core/agent.py
```

You should see:
```
🚀 Starting YieldHarvest Agent...
✅ Session key is valid
✅ Agent is now running autonomously
🔍 Scanning for yield opportunities...
```

### Step 7: Start Dashboard (5 minutes)

```bash
# In terminal 2: Setup dashboard
cd dashboard
npm install
cp .env.example .env.local

# Edit .env.local with your contract addresses
# Then start
npm run dev
```

Visit `http://localhost:3000` - you should see your live agent!

---

## ✅ Submission Checklist

Before submitting to the hackathon:

### Required (Will be Disqualified Without These!)

- [ ] **Onchain Proof:** Transaction hash or contract address
  - Vault Manager: `0x...` (from Step 3)
  - First transaction: `0x...` (from BSCScan)

- [ ] **Public GitHub Repo:** 
  - Make repo public
  - Include README with setup instructions
  - Add .env.example (no secrets!)

- [ ] **Demo Link:**
  - Deploy dashboard to Vercel (free): `vercel --prod`
  - OR: Record video demo of agent working

- [ ] **Reproducible:**
  - Clear README with setup steps
  - Working deployment script
  - No hardcoded values

### Highly Recommended

- [ ] **AI Build Log:** 
  - Already created at `docs/AI_BUILD_LOG.md`
  - Shows how you used Claude/AI

- [ ] **Video Demo:**
  - 2-3 minute Loom video
  - Show: deployment → agent scanning → making decisions → dashboard

- [ ] **Clean Code:**
  - Run `prettier --write "**/*.{ts,tsx,sol}"`
  - Remove debug logs
  - Add comments

---

## 📹 Creating Your Demo

### Option 1: Live Dashboard (Recommended)

Deploy to Vercel:
```bash
cd dashboard
vercel --prod
```

Get a live URL like: `https://yieldharvest-agent.vercel.app`

### Option 2: Video Demo

Record with Loom/OBS showing:

1. **Intro (30 seconds)**
   - "This is YieldHarvest, an autonomous yield farming agent"
   - Show contract addresses on BscScan

2. **Agent in Action (90 seconds)**
   - Terminal: Agent scanning opportunities
   - Terminal: Agent making decisions
   - Show decision logs onchain

3. **Dashboard (60 seconds)**
   - Portfolio view
   - Performance metrics
   - Decision history timeline

---

## 🎯 Hackathon Submission Form

When submitting, include:

**Project Name:** YieldHarvest Agent

**Track:** Agent (AI Agent × Onchain Actions)

**Short Description:**
```
Autonomous AI agent that discovers, evaluates, and compounds DeFi yields 24/7 
on BNB Chain. Uses Claude for decision-making and logs all reasoning onchain 
for transparency.
```

**Contract Address (BSC):**
```
0x... (YieldVaultManager address)
```

**Transaction Hash:**
```
0x... (First transaction hash from BscScan)
```

**GitHub Repo:**
```
https://github.com/yourusername/yieldharvest-agent
```

**Demo Link:**
```
https://yieldharvest-agent.vercel.app
OR
https://loom.com/share/... (video)
```

**AI Tools Used:**
```
- Claude (Anthropic) - 90% of codebase, architecture design, decision logic
- GitHub Copilot - Smart contract development
- Cursor - Dashboard components

See docs/AI_BUILD_LOG.md for detailed breakdown.
```

**What Makes It Unique:**
```
✅ Fully autonomous - runs 24/7 without human intervention
✅ Economic agent - actually makes money onchain
✅ AI-powered decisions - uses Claude API for reasoning
✅ Transparent - all decisions logged onchain with explanations
✅ Non-custodial - session keys with spending limits
✅ Reproducible - anyone can deploy and verify
```

---

## 🐛 Troubleshooting

### "Insufficient funds for gas"
- Make sure you have at least 0.5 BNB in your wallet
- Check BSC gas prices on BscScan

### "Session key invalid"
- Session keys expire after 24 hours
- Re-run deployment script to create new key

### "Cannot find module"
- Run `npm install` and `pip install -r requirements.txt`
- Make sure you're in the right directory

### "Contract not whitelisted"
- Check if protocols were whitelisted during deployment
- Manually whitelist: `await vaultManager.whitelistProtocol(address, true)`

### Agent not finding opportunities
- BSC RPC might be rate-limited - try different RPC from chainlist.org
- Check if protocols have active pools (use PancakeSwap UI to verify)

---

## 📊 Testing Before Submission

### Quick Test Checklist:

1. **Contracts Deployed?**
   ```bash
   # Check on BscScan
   https://bscscan.com/address/<YOUR_VAULT_ADDRESS>
   ```

2. **Agent Running?**
   ```bash
   # Should see logs like:
   🔍 Scanning for yield opportunities...
   Found 12 potential opportunities
   ```

3. **Dashboard Working?**
   ```bash
   # Open browser to localhost:3000
   # Should show live agent status
   ```

4. **Decisions Logged?**
   ```bash
   # Check DecisionLogger on BscScan
   # Should see Decision Logged events
   ```

---

## 🏆 Winning Tips

### Stand Out From Other Submissions:

1. **Show Real Results**
   - Let agent run for 6-12 hours before submitting
   - Show actual compound transactions on BscScan
   - Demonstrate measurable ROI

2. **Professional Presentation**
   - Clean, deployed dashboard (not just localhost)
   - Verified contracts on BscScan
   - Clear README with screenshots

3. **Prove Autonomy**
   - Show agent made decisions without you
   - Highlight decision logs with AI reasoning
   - Demonstrate 24/7 operation

4. **Technical Depth**
   - Reference AI_BUILD_LOG.md in submission
   - Explain risk scoring algorithm
   - Show gas optimization

5. **Future Vision**
   - Mention roadmap (multi-chain, DAO, copy-trading)
   - Show you built for production, not just hackathon

---

## 📞 Getting Help

**Hackathon Discord:** #vibe-coding channel

**Common Issues:** Check `docs/TROUBLESHOOTING.md`

**Questions?** Open GitHub issue

---

## ⏰ Time Remaining: ~3 Days

**Recommended Timeline:**

- **Day 1 (Today):**
  - Deploy contracts (1 hour)
  - Run agent (30 minutes)
  - Fix any bugs (2 hours)

- **Day 2:**
  - Let agent run and accumulate data (all day)
  - Build dashboard polish (2 hours)
  - Create video demo (1 hour)

- **Day 3 (Submission Day):**
  - Final testing (1 hour)
  - Deploy dashboard to Vercel (30 minutes)
  - Submit before 3:00 PM UTC ⚠️

---

## 🎉 You're Ready!

Follow this guide and you'll have a professional, working submission that demonstrates:

✅ Real autonomous agent behavior  
✅ Onchain proof of execution  
✅ AI-powered decision making  
✅ Production-ready code  
✅ Clear documentation  

**Now go build and win that $100,000 prize pool! 🚀**

---

**Good luck from the YieldHarvest team! 💰🤖**
