const { ethers } = require("hardhat");

async function main() {
  console.log("⏰ Extending session key to 1 year...\n");

  const [deployer] = await ethers.getSigners();
  console.log("Using account:", deployer.address);

  const SessionKeyManager = await ethers.getContractAt(
    "SessionKeyManager", 
    "0x24988f6313cFA0c76aAA930Fbe81b6dd3f871F5B"
  );

  const yourAddress = "0x5e85E8500cF6Ff329e081dd5Fb9f41Ba301DFA8e";
  const oneYear = 365 * 24 * 60 * 60; // 1 year in seconds

  console.log("Extending session key for:", yourAddress);
  console.log("Adding: 1 year\n");

  const tx = await SessionKeyManager.extendExpiry(yourAddress, oneYear);
  
  console.log("Transaction sent:", tx.hash);
  await tx.wait();

  console.log("\n✅ Session key extended successfully!");
  console.log("Your key now expires in 1 year from now!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
