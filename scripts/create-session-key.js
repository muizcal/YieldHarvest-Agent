const { ethers } = require("hardhat");

async function main() {
  console.log("🔑 Creating 1-year session key...\n");

  const [deployer] = await ethers.getSigners();
  console.log("Using account:", deployer.address);

  const SessionKeyManager = await ethers.getContractAt(
    "SessionKeyManager", 
    "0x24988f6313cFA0c76aAA930Fbe81b6dd3f871F5B"
  );

  const spendingLimit = ethers.parseEther("1.0"); // 1 BNB
  const duration = 365 * 24 * 60 * 60; // 1 year
  const yourAddress = "0x5e85E8500cF6Ff329e081dd5Fb9f41Ba301DFA8e";

  console.log("Creating session key with:");
  console.log("- Address:", yourAddress);
  console.log("- Spending limit: 1.0 BNB");
  console.log("- Duration: 1 year\n");

  const tx = await SessionKeyManager.createSessionKey(
    yourAddress,
    spendingLimit,
    duration,
    "1-Year Agent Session Key"
  );

  console.log("Transaction sent:", tx.hash);
  await tx.wait();

  console.log("\n✅ 1-year session key created successfully!");
  console.log("\nYour agent can now operate for 1 year without renewal.");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
