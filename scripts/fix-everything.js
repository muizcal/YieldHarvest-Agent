const { ethers } = require("hardhat");

async function main() {
  console.log("🔧 FIXING EVERYTHING...\n");

  const [deployer] = await ethers.getSigners();
  console.log("Using account:", deployer.address);
  console.log("");

  // ═══════════════════════════════════════════════════════
  // STEP 1: WHITELIST PROTOCOLS
  // ═══════════════════════════════════════════════════════
  console.log("📝 STEP 1: Whitelisting protocols...");
  
  const VaultManager = await ethers.getContractAt(
    "YieldVaultManager", 
    "0x2bd1c8a9638391974d2940Ffbb0f53778d54bA49"
  );

  console.log("   Whitelisting PancakeSwap...");
  await VaultManager.whitelistProtocol("0xa5f8C5Dbd5F286960b9d90548680aE5ebFf07652", true);
  console.log("   ✅ PancakeSwap whitelisted");

  console.log("   Whitelisting Venus...");
  await VaultManager.whitelistProtocol("0xfD36E2c2a6789Db23113685031d7F16329158384", true);
  console.log("   ✅ Venus whitelisted");

  console.log("   Whitelisting Thena...");
  await VaultManager.whitelistProtocol("0xd4ae6eCA985340Dd434D38F470aCCce4DC78D109", true);
  console.log("   ✅ Thena whitelisted");

  console.log("");

  // ═══════════════════════════════════════════════════════
  // STEP 2: FIX SESSION KEY
  // ═══════════════════════════════════════════════════════
  console.log("🔑 STEP 2: Fixing session key...");
  
  const SessionManager = await ethers.getContractAt(
    "SessionKeyManager", 
    "0x24988f6313cFA0c76aAA930Fbe81b6dd3f871F5B"
  );

  const yourAddress = "0x5e85E8500cF6Ff329e081dd5Fb9f41Ba301DFA8e";

  console.log("   Revoking old session key...");
  await SessionManager.revokeSessionKey(yourAddress, "Creating fresh key");
  console.log("   ✅ Old key revoked");

  console.log("   Creating new 1-year session key...");
  await SessionManager.createSessionKey(
    yourAddress,
    ethers.parseEther("1.0"),
    365 * 24 * 60 * 60,
    "Fresh 1-Year Agent Key"
  );
  console.log("   ✅ New key created (valid for 1 year)");

  console.log("");
  console.log("═══════════════════════════════════════════════");
  console.log("✅ ALL FIXED!");
  console.log("═══════════════════════════════════════════════");
  console.log("");
  console.log("Now restart your agent:");
  console.log("   python3 agent/core/agent.py");
  console.log("");
  console.log("You should see:");
  console.log("   Whitelisted protocols: 3  ✅");
  console.log("   ✅ Session key is valid");
  console.log("");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
