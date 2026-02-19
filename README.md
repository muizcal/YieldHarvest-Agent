# YieldHarvest

An autonomous AI agent for yield farming on Binance Smart Chain. The system continuously scans DeFi protocols, evaluates opportunities based on risk and return metrics, and executes positions automatically.

## Live Deployment

**Dashboard:** [https://yieldharvest.vercel.app](https://yieldharvest.vercel.app)  
**API Server:** [https://yieldharvest-agent-production.up.railway.app](https://yieldharvest-agent-production.up.railway.app)

## Deployed Smart Contracts (BSC Mainnet)

All contracts are verified and viewable on BscScan:

- **YieldVaultManager:** [0x2bd1c8a9638391974d2940Ffbb0f53778d54bA49](https://bscscan.com/address/0x2bd1c8a9638391974d2940Ffbb0f53778d54bA49)
- **SessionKeyManager:** [0x24988f6313cFA0c76aAA930Fbe81b6dd3f871F5B](https://bscscan.com/address/0x24988f6313cFA0c76aAA930Fbe81b6dd3f871F5B)
- **DecisionLogger:** [0xe82347f28365333b6f6901E7b40c17099D556007](https://bscscan.com/address/0xe82347f28365333b6f6901E7b40c17099D556007)

**Network:** Binance Smart Chain (BSC)  
**Chain ID:** 56

### Whitelisted DeFi Protocols

The agent currently operates with these whitelisted protocols:

- **PancakeSwap MasterChef:** [0xa5f8C5Dbd5F286960b9d90548680aE5ebFf07652](https://bscscan.com/address/0xa5f8C5Dbd5F286960b9d90548680aE5ebFf07652)
- **Venus Comptroller:** [0xfD36E2c2a6789Db23113685031d7F16329158384](https://bscscan.com/address/0xfD36E2c2a6789Db23113685031d7F16329158384)
- **Thena Router:** [0xd4ae6eCA985340Dd434D38F470aCCce4DC78D109](https://bscscan.com/address/0xd4ae6eCA985340Dd434D38F470aCCce4DC78D109)

## Overview

YieldHarvest uses artificial intelligence to optimize yield farming strategies across multiple DeFi protocols on BSC. The agent operates autonomously, making data-driven decisions about where to allocate capital based on real-time market conditions.

### Key Features

- Real-time opportunity discovery via DeFiLlama API
- Risk-adjusted portfolio optimization
- Automated position management and compounding
- Multi-protocol support (PancakeSwap, Venus, Thena)
- Transparent decision logging
- Web-based monitoring dashboard

## Architecture

The system consists of three main components:

### 1. Autonomous Agent

The core Python-based agent that:
- Discovers yield opportunities from aggregated DeFi data
- Evaluates opportunities using a multi-factor risk model
- Makes allocation decisions based on portfolio optimization algorithms
- Executes and manages positions across protocols
- Compounds rewards automatically

### 2. API Server

A lightweight HTTP server that:
- Serves position data to the dashboard
- Provides real-time statistics and metrics
- Enables monitoring without direct blockchain queries

### 3. Web Dashboard

A clean, modern interface for:
- Monitoring active positions
- Viewing performance metrics
- Managing vault deposits and withdrawals
- Tracking agent decisions in real-time

## Technical Stack

**Backend**
- Python 3.10+
- Web3.py for blockchain interaction
- aiohttp for async HTTP requests
- APScheduler for task scheduling

**Frontend**
- Vanilla JavaScript (no framework dependencies)
- Ethers.js for wallet connection
- Responsive CSS Grid layout

**Blockchain**
- Binance Smart Chain (BSC Mainnet)
- Solidity smart contracts
- EIP-2535 inspired modular architecture

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/yieldharvest.git
cd yieldharvest
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your settings
```

Required environment variables:
- `BSC_RPC_URL` - BSC node RPC endpoint
- `PRIVATE_KEY` - Wallet private key
- `VAULT_MANAGER_ADDRESS` - Deployed vault contract address

## Usage

Start the autonomous agent:

```bash
python3 agent/core/agent.py
```

Start the API server (separate terminal):

```bash
python3 api-server.py
```

Start the dashboard (separate terminal):

```bash
cd dashboard
python3 -m http.server 8000
```

Access the dashboard at `http://localhost:8000`

## Configuration

The agent behavior can be customized via `agent/config.py`:

- `min_apy` - Minimum acceptable APY (default: 5%)
- `max_risk_score` - Maximum acceptable risk score (default: 7/10)
- `compound_interval` - How often to compound positions (default: 4 hours)
- `rebalance_threshold` - APY difference required to rebalance (default: 2%)
- `max_allocation_per_protocol` - Maximum allocation to single protocol (default: 20%)

## Smart Contracts

The system uses three deployed contracts on BSC:

**YieldVaultManager** - Main vault for managing positions
**SessionKeyManager** - Handles agent authorization and permissions
**DecisionLogger** - Records all agent decisions on-chain for transparency

Contract addresses can be found in `.env` file.

## Risk Evaluation

The agent evaluates opportunities using a proprietary scoring system that considers:

- Contract age and maturity
- Total Value Locked (TVL)
- APY sustainability and historical stability
- Protocol reputation and track record
- Smart contract security audits

Risk scores range from 0-10, where lower scores indicate safer opportunities.

## Development

Run tests:

```bash
python3 -m pytest tests/
```

Deploy contracts:

```bash
npx hardhat run scripts/deploy.js --network bsc
```

Verify contracts:

```bash
npx hardhat verify --network bsc <CONTRACT_ADDRESS>
```

## Project Structure

```
yieldharvest/
├── agent/
│   ├── core/           # Main agent logic
│   ├── engines/        # Discovery, evaluation, execution
│   ├── strategies/     # Portfolio optimization, risk management
│   └── utils/          # Blockchain client, logging
├── contracts/          # Solidity smart contracts
├── dashboard/          # Web interface
├── scripts/            # Deployment and utility scripts
└── tests/              # Test suite
```

## Performance

The agent tracks comprehensive metrics:

- Total capital deployed
- Cumulative yield earned
- Gas costs
- Net profit after fees
- Average APY across positions
- Win rate and position success metrics

All metrics are logged on-chain and available via the dashboard.

## Security Considerations

- Private keys are never exposed to the frontend
- Agent operates with limited session keys (when enabled)
- Emergency withdrawal function for owner
- Position size limits to prevent overexposure
- Multi-layered validation before execution

## Deployment

### Current Production Deployment

The system is deployed across multiple platforms:

**Frontend (Vercel):**
- URL: https://yield-harvest-agent.vercel.app
- Auto-deploys from GitHub main branch
- Serves static dashboard

**Backend (Railway):**
- URL: https://yieldharvest-agent-production.up.railway.app
- Runs both API server and autonomous agent
- Persistent storage for position tracking

### Deploy Your Own Instance

#### Frontend (Vercel)

1. Fork this repository
2. Connect to Vercel
3. Set root directory to `dashboard`
4. Add environment variable: `NEXT_PUBLIC_API_URL` (your Railway URL)
5. Deploy

#### Backend (Railway)

1. Create new Railway project
2. Connect your forked repository
3. Railway will detect Python automatically
4. Set environment variables (see .env.example)
5. Deploy

The system uses `railway.toml` for configuration and `start.sh` to run both services.

### Local Development

Run on a VPS or local machine with persistent connection:

```bash
# Using systemd service
sudo systemctl start yieldharvest-agent
```

## Limitations

- Currently supports BSC only (Ethereum support planned)
- **Demo mode:** Agent tracks positions locally without executing on-chain transactions to minimize gas costs during development
- Production mode available with full on-chain execution capability
- API rate limits may affect discovery frequency during high volatility
- Positions are simulated for demonstration purposes; real capital deployment requires additional configuration

## Demo vs Production Mode

**Current Deployment (Demo Mode):**
- Agent scans real DeFi protocols via DeFiLlama API
- Evaluates opportunities using actual market data
- Makes autonomous decisions based on AI optimization
- Tracks positions locally in JSON storage
- No on-chain transactions (saves gas fees)
- Perfect for testing and demonstration

**Production Mode:**
- All demo features plus:
- Executes real on-chain transactions
- Manages actual capital in smart contracts
- Compounds positions automatically
- Full session key authorization
- Emergency withdrawal capabilities

To enable production mode, update the ExecutionEngine to use actual contract calls instead of local tracking.



## License

MIT License - see LICENSE file for details

## Disclaimer

This software is for educational and research purposes. Users are responsible for their own capital and should understand the risks involved in DeFi yield farming. Past performance does not guarantee future results. Always do your own research.

## Contact

For questions or support, open an issue on GitHub.

## Acknowledgments

- DeFiLlama for aggregated protocol data
- OpenZeppelin for contract libraries
- BSC community for infrastructure support