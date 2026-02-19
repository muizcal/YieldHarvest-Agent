const { ethers } = require("hardhat");

async function main() {
  console.log("🔄 Recreating session key...\n");

  const SessionKeyManager = await ethers.getContractAt(
    "SessionKeyManager", 
    "0x24988f6313cFA0c76aAA930Fbe81b6dd3f871F5B"
  );

  const yourAddress = "0x5e85E8500cF6Ff329e081dd5Fb9f41Ba301DFA8e";

  // Step 1: Revoke old key
  console.log("Step 1: Revoking old session key...");
  const revokeTx = await SessionKeyManager.revokeSessionKey(
    yourAddress,
    "Replacing with 1-year key"
  );
  await revokeTx.wait();
  console.log("✅ Old key revoked\n");

  // Step 2: Create new 1-year key
  console.log("Step 2: Creating new 1-year session key...");
  const spendingLimit = ethers.parseEther("1.0");
  const duration = 365 * 24 * 60 * 60; // 1 year

  const createTx = await SessionKeyManager.createSessionKey(
    yourAddress,
    spendingLimit,
    duration,
    "1-Year Agent Session Key"
  );
  await createTx.wait();
  console.log("✅ New key created\n");

  console.log("🎉 Session key recreated successfully!");
  console.log("Duration: 1 year");
  console.log("Spending limit: 1.0 BNB");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
