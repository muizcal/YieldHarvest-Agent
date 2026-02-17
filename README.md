# YieldHarvest Agent 🤖💰

> **Autonomous AI agent that discovers, evaluates, and compounds DeFi yields 24/7 on BNB Chain**

**Good Vibes Only: OpenClaw Edition Submission**  
**Track:** Agent (AI Agent × Onchain Actions)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 The Problem

DeFi users manually hunt for yields, miss optimal entry/exit points, and fail to compound frequently enough. Existing yield aggregators require manual deposits and don't autonomously rebalance based on changing market conditions.

## 💡 The Solution

**YieldHarvest Agent** is a fully autonomous AI agent that:
- 🔍 **Discovers** new yield opportunities across BSC/opBNB in real-time
- 🧠 **Evaluates** safety using onchain metrics (TVL, contract age, APY sustainability)
- 💸 **Deploys** capital to highest risk-adjusted yields automatically
- 🔄 **Compounds** rewards every 4-12 hours (configurable)
- ⚖️ **Rebalances** when better opportunities emerge
- 📝 **Logs** every decision onchain for full transparency

## 🏆 Why This Stands Out

Unlike existing submissions that are:
- Security scanners (reactive, not proactive)
- Chat interfaces (require human input)
- One-off tools (no continuous operation)

**YieldHarvest is:**
- ✅ Fully autonomous economic agent
- ✅ Makes real money onchain (verifiable ROI)
- ✅ Learns and adapts to market conditions
- ✅ Decision logic posted onchain as events
- ✅ Non-custodial using session keys

## 🎬 Demo

**Live Agent:** [Dashboard URL]
**Contract Address:** `0x...` (BSC)
**Session Key Manager:** `0x...` (BSC)

Watch the agent work in real-time:
1. Scanning for opportunities
2. Evaluating risk scores
3. Making deployment decisions
4. Compounding rewards
5. Rebalancing portfolio

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     YieldHarvest Agent                       │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Discovery  │    │  Evaluation  │    │  Execution   │
│    Engine    │───▶│    Engine    │───▶│    Engine    │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│              Smart Contract Layer (BSC)                  │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────┐  │
│  │ YieldVault │  │ SessionKey │  │ DecisionLogger   │  │
│  │  Manager   │  │  Manager   │  │   (Events)       │  │
│  └────────────┘  └────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ PancakeSwap  │    │    Venus     │    │    Thena     │
│   Protocol   │    │   Protocol   │    │   Protocol   │
└──────────────┘    └──────────────┘    └──────────────┘
```

## 📁 Project Structure

```
yieldharvest-agent/
├── contracts/                 # Smart contracts
│   ├── YieldVaultManager.sol    # Main vault management
│   ├── SessionKeyManager.sol    # Non-custodial key management
│   ├── DecisionLogger.sol       # Onchain decision logging
│   └── interfaces/
│       ├── IYieldSource.sol     # Yield protocol interface
│       └── IPancakeRouter.sol   # DEX router interface
│
├── agent/                     # AI Agent logic
│   ├── core/
│   │   ├── agent.py            # Main agent orchestrator
│   │   └── config.py           # Agent configuration
│   ├── engines/
│   │   ├── discovery.py        # Opportunity scanner
│   │   ├── evaluation.py       # Risk assessment
│   │   └── execution.py        # Transaction executor
│   ├── strategies/
│   │   ├── yield_optimizer.py  # Yield optimization logic
│   │   └── risk_manager.py     # Risk management rules
│   └── utils/
│       ├── blockchain.py       # Web3 utilities
│       └── logger.py           # Logging utilities
│
├── dashboard/                 # Next.js frontend
│   ├── app/
│   │   ├── page.tsx           # Main dashboard
│   │   └── layout.tsx         # Layout
│   ├── components/
│   │   ├── AgentStatus.tsx    # Live agent status
│   │   ├── PortfolioView.tsx  # Portfolio positions
│   │   ├── DecisionLog.tsx    # Decision history
│   │   └── PerformanceChart.tsx # ROI metrics
│   └── lib/
│       ├── web3.ts            # Web3 connection
│       └── api.ts             # API client
│
├── scripts/                   # Deployment & utilities
│   ├── deploy.ts              # Contract deployment
│   ├── setup-agent.ts         # Agent initialization
│   └── test-agent.ts          # Agent testing
│
├── tests/                     # Test suite
│   ├── contracts/             # Contract tests
│   ├── agent/                 # Agent logic tests
│   └── integration/           # E2E tests
│
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md        # System architecture
│   ├── AI_BUILD_LOG.md        # How AI was used
│   └── DEPLOYMENT.md          # Deployment guide
│
├── .env.example              # Environment template
├── hardhat.config.ts         # Hardhat config
├── package.json              # Node dependencies
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- BNB Chain RPC URL
- Private key with BNB for gas

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/yieldharvest-agent.git
cd yieldharvest-agent

# Install contract dependencies
npm install

# Install agent dependencies
pip install -r requirements.txt

# Install dashboard dependencies
cd dashboard && npm install && cd ..
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required variables:
```env
# Blockchain
BSC_RPC_URL=https://bsc-dataseed1.binance.org
PRIVATE_KEY=your_private_key_here

# Agent Config
AGENT_MIN_APY=5.0
AGENT_MAX_RISK_SCORE=7.0
AGENT_COMPOUND_INTERVAL=14400  # 4 hours in seconds
AGENT_REBALANCE_THRESHOLD=2.0  # APY difference to trigger rebalance

# Session Keys (generated during setup)
SESSION_KEY_MANAGER=
VAULT_MANAGER=

# API Keys (optional for enhanced features)
ANTHROPIC_API_KEY=your_claude_api_key
BSCSCAN_API_KEY=your_bscscan_key
```

### 3. Deploy Contracts

```bash
npx hardhat compile
npx hardhat run scripts/deploy.ts --network bsc
```

Save contract addresses to `.env`

### 4. Run Agent

```bash
# Start the autonomous agent
python agent/core/agent.py

# In another terminal, start dashboard
cd dashboard
npm run dev
```

### 5. Watch It Work

Open `http://localhost:3000` to see:
- Live agent status
- Portfolio positions
- Decision history
- Performance metrics

## 🧪 How It Works

### Discovery Engine

Scans BSC for yield opportunities:
```python
# Monitors events from:
- PancakeSwap MasterChef (LP farms)
- Venus Protocol (lending pools)
- Thena (gauges & bribes)
- Alpaca Finance (leveraged yield)

# Filters by:
- Minimum liquidity ($10k+)
- Contract age (7+ days)
- APY thresholds (configurable)
```

### Evaluation Engine

Scores each opportunity (0-10):
```python
risk_score = weighted_average([
    contract_audit_score,      # 30% - Has audit?
    tvl_stability_score,       # 25% - TVL trend
    apy_sustainability_score,  # 20% - APY history
    protocol_reputation_score, # 15% - Known protocol?
    liquidity_depth_score      # 10% - Exit liquidity
])
```

### Execution Engine

Makes autonomous decisions:
```python
if new_opportunity.apy > current_position.apy + REBALANCE_THRESHOLD:
    if new_opportunity.risk_score <= MAX_RISK_SCORE:
        # Log decision onchain
        log_decision(reason, old_position, new_position)
        
        # Execute rebalance
        withdraw_from(current_position)
        deposit_to(new_opportunity)
        
        # Emit event
        emit OpportunitySeized(timestamp, details)
```

## 🔐 Security Features

### Non-Custodial Architecture
- ✅ Session keys with spending limits
- ✅ Time-locked withdrawals
- ✅ Whitelisted protocols only
- ✅ Emergency pause function
- ✅ Multi-sig recovery

### Risk Management
- ✅ Maximum allocation per protocol (20%)
- ✅ Daily transaction limits
- ✅ Slippage protection (1%)
- ✅ Automated circuit breakers
- ✅ Real-time anomaly detection

## 📊 Performance Tracking

All metrics logged onchain:
- Total Value Locked (TVL)
- Realized returns (daily/weekly/monthly)
- Number of compounds executed
- Number of rebalances performed
- Gas costs vs yield earned
- Risk-adjusted returns (Sharpe ratio)

## 🤖 AI Build Log

This project was built using:
- **Claude (Anthropic)** - Agent decision logic, risk evaluation
- **GitHub Copilot** - Smart contract development
- **Cursor** - Dashboard UI components

See [docs/AI_BUILD_LOG.md](docs/AI_BUILD_LOG.md) for detailed breakdown.

## 🧪 Testing

```bash
# Run contract tests
npx hardhat test

# Run agent tests
pytest tests/agent/

# Run integration tests
pytest tests/integration/
```

## 🎯 Roadmap

**Phase 1 (Hackathon):** ✅
- Core agent logic
- Basic yield sources (PancakeSwap, Venus)
- Dashboard MVP
- BSC deployment

**Phase 2 (Post-Hackathon):**
- Multi-chain support (opBNB, Ethereum)
- Advanced strategies (delta-neutral, arbitrage)
- Social features (copy trading)
- Mobile app

**Phase 3 (Production):**
- DAO governance
- Agent marketplace
- Institutional vaults
- Audit completion

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 🙏 Acknowledgments

- BNB Chain team for OpenClaw framework
- Good Vibes Only hackathon organizers
- PancakeSwap, Venus, Thena protocols

## 📞 Contact

- **Discord:** [Your Discord]
- **Twitter:** [@YourHandle]
- **Email:** your@email.com

---

**Built with ❤️ for Good Vibes Only: OpenClaw Edition**

*Autonomous yield farming is here. Let the agent work while you sleep.* 💤💰
