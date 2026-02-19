# YieldHarvest

An autonomous AI agent for yield farming on Binance Smart Chain. The system continuously scans DeFi protocols, evaluates opportunities based on risk and return metrics, and executes positions automatically.

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
│   ├── core/           
│   ├── engines/        
│   ├── strategies/     
│   └── utils/          
├── contracts/          
├── dashboard/          
├── scripts/            
└── tests/              
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

### Frontend (Vercel)

1. Connect repository to Vercel
2. Set root directory to `dashboard`
3. Deploy

### Backend (Railway)

1. Create new Railway project
2. Connect repository
3. Set start command: `python3 api-server.py`
4. Add environment variables
5. Deploy

### Agent (Self-hosted)

Run on a VPS or local machine with persistent connection:

```bash
# Using systemd service
sudo systemctl start yieldharvest-agent
```

## Limitations

- Currently supports BSC only (Ethereum support planned)
- Demo mode executes simulated positions (production mode requires additional setup)
- API rate limits may affect discovery frequency during high volatility
- Gas costs on BSC are not included in yield calculations



## Disclaimer

This software is for educational and research purposes. Users are responsible for their own capital and should understand the risks involved in DeFi yield farming. Past performance does not guarantee future results. Always do your own research.

## Contact

For questions or support, open an issue on GitHub.

## Acknowledgments

- DeFiLlama for aggregated protocol data
- OpenZeppelin for contract libraries
- BSC community for infrastructure support