import { ethers } from "hardhat";

async function main() {
  console.log("🚀 Deploying YieldHarvest Agent contracts to BSC...\n");

  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);
  console.log("Account balance:", ethers.formatEther(await ethers.provider.getBalance(deployer.address)), "BNB\n");

  // Deploy SessionKeyManager
  console.log("📝 Deploying SessionKeyManager...");
  const SessionKeyManager = await ethers.getContractFactory("SessionKeyManager");
  const sessionKeyManager = await SessionKeyManager.deploy();
  await sessionKeyManager.waitForDeployment();
  const sessionKeyManagerAddress = await sessionKeyManager.getAddress();
  console.log("✅ SessionKeyManager deployed to:", sessionKeyManagerAddress, "\n");

  // Deploy DecisionLogger
  console.log("📝 Deploying DecisionLogger...");
  const DecisionLogger = await ethers.getContractFactory("DecisionLogger");
  const decisionLogger = await DecisionLogger.deploy();
  await decisionLogger.waitForDeployment();
  const decisionLoggerAddress = await decisionLogger.getAddress();
  console.log("✅ DecisionLogger deployed to:", decisionLoggerAddress, "\n");

  // Deploy YieldVaultManager
  console.log("📝 Deploying YieldVaultManager...");
  const emergencyAddress = deployer.address; // Use deployer as emergency address
  const YieldVaultManager = await ethers.getContractFactory("YieldVaultManager");
  const vaultManager = await YieldVaultManager.deploy(
    sessionKeyManagerAddress,
    decisionLoggerAddress,
    emergencyAddress
  );
  await vaultManager.waitForDeployment();
  const vaultManagerAddress = await vaultManager.getAddress();
  console.log("✅ YieldVaultManager deployed to:", vaultManagerAddress, "\n");

  // Set vault manager as owner of decision logger
  console.log("📝 Setting permissions...");
  await decisionLogger.transferOwnership(vaultManagerAddress);
  console.log("✅ DecisionLogger ownership transferred to VaultManager\n");

  // Create session key for agent
  console.log("📝 Creating session key for agent...");
  const sessionKeyAddress = deployer.address; // For demo, use deployer as session key
  const spendingLimit = ethers.parseEther("0.1"); // 0.1 BNB limit
  const duration = 24 * 60 * 60; // 24 hours
  
  await sessionKeyManager.createSessionKey(
    sessionKeyAddress,
    spendingLimit,
    duration,
    "AI Agent Session Key"
  );
  console.log("✅ Session key created for:", sessionKeyAddress, "\n");

  // Whitelist protocols
  console.log("📝 Whitelisting protocols...");
  
  // PancakeSwap MasterChef
  const pancakeMasterChef = "0xa5f8C5Dbd5F286960b9d90548680aE5ebFf07652";
  await vaultManager.whitelistProtocol(pancakeMasterChef, true);
  console.log("✅ Whitelisted PancakeSwap MasterChef");

  // Venus Comptroller
  const venusComptroller = "0xfD36E2c2a6789Db23113685031d7F16329158384";
  await vaultManager.whitelistProtocol(venusComptroller, true);
  console.log("✅ Whitelisted Venus Protocol");

  // Thena Router
  const thenaRouter = "0xd4ae6eCA985340Dd434D38F470aCCce4DC78D109";
  await vaultManager.whitelistProtocol(thenaRouter, true);
  console.log("✅ Whitelisted Thena Protocol\n");

  // Fund vault with initial capital
  console.log("📝 Funding vault with initial capital...");
  const initialCapital = ethers.parseEther("1.0"); // 1 BNB
  await deployer.sendTransaction({
    to: vaultManagerAddress,
    value: initialCapital
  });
  console.log("✅ Vault funded with 1 BNB\n");

  // Print deployment summary
  console.log("=" .repeat(80));
  console.log("DEPLOYMENT SUMMARY");
  console.log("=".repeat(80));
  console.log("\n📋 Contract Addresses:");
  console.log("---");
  console.log(`SessionKeyManager:  ${sessionKeyManagerAddress}`);
  console.log(`DecisionLogger:     ${decisionLoggerAddress}`);
  console.log(`YieldVaultManager:  ${vaultManagerAddress}`);
  console.log("\n🔑 Session Key:");
  console.log("---");
  console.log(`Address:            ${sessionKeyAddress}`);
  console.log(`Spending Limit:     0.1 BNB`);
  console.log(`Duration:           24 hours`);
  console.log("\n💰 Initial State:");
  console.log("---");
  console.log(`Vault Balance:      1.0 BNB`);
  console.log(`Whitelisted:        PancakeSwap, Venus, Thena`);
  
  console.log("\n📝 Next Steps:");
  console.log("---");
  console.log("1. Update .env with contract addresses:");
  console.log(`   VAULT_MANAGER_ADDRESS=${vaultManagerAddress}`);
  console.log(`   SESSION_KEY_MANAGER_ADDRESS=${sessionKeyManagerAddress}`);
  console.log(`   DECISION_LOGGER_ADDRESS=${decisionLoggerAddress}`);
  console.log("\n2. Verify contracts on BscScan:");
  console.log(`   npx hardhat verify --network bsc ${sessionKeyManagerAddress}`);
  console.log(`   npx hardhat verify --network bsc ${decisionLoggerAddress}`);
  console.log(`   npx hardhat verify --network bsc ${vaultManagerAddress} ${sessionKeyManagerAddress} ${decisionLoggerAddress} ${emergencyAddress}`);
  console.log("\n3. Start the agent:");
  console.log(`   python agent/core/agent.py`);
  console.log("\n4. Start the dashboard:");
  console.log(`   cd dashboard && npm run dev`);
  console.log("\n" + "=".repeat(80));
  console.log("✅ Deployment complete! Good luck in the hackathon! 🚀");
  console.log("=".repeat(80) + "\n");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
