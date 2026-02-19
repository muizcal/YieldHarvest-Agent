const { ethers } = require("hardhat");

async function main() {
  console.log("🔧 Fixing session key...\n");

  const [deployer] = await ethers.getSigners();
  console.log("Using account:", deployer.address);

  const SessionKeyManager = await ethers.getContractAt(
    "SessionKeyManager", 
    "0x24988f6313cFA0c76aAA930Fbe81b6dd3f871F5B"
  );

  const VaultManager = await ethers.getContractAt(
    "YieldVaultManager",
    "0x2bd1c8a9638391974d2940Ffbb0f53778d54bA49"
  );

  const yourAddress = "0x5e85E8500cF6Ff329e081dd5Fb9f41Ba301DFA8e";

  // Check current status
  const currentKey = await SessionKeyManager.sessionKeys(yourAddress);
  console.log("Current key status:");
  console.log("  Address:", currentKey.key);
  console.log("  Is Active:", currentKey.isActive);
  console.log("  Expiry:", new Date(Number(currentKey.expiryTimestamp) * 1000).toISOString());
  
  if (!currentKey.isActive) {
    console.log("\n❌ Key is INACTIVE - this is why transactions fail!");
    console.log("\n💡 SOLUTION: The vault owner (you) can bypass session key check");
    console.log("   Let me check if you're the owner...\n");
    
    const vaultOwner = await VaultManager.owner();
    console.log("Vault owner:", vaultOwner);
    console.log("Your address:", yourAddress);
    
    if (vaultOwner.toLowerCase() === yourAddress.toLowerCase()) {
      console.log("\n✅ YOU ARE THE OWNER!");
      console.log("   But the contract doesn't have owner bypass...");
      console.log("\n🔧 We need to modify the YieldVaultManager modifier:");
      console.log("   Change: onlyAuthorized() to check owner OR session key");
      console.log("\n⚠️ This requires redeploying the contract.");
      console.log("\n📝 Alternative: Create a NEW session key with different address");
      
      // Create new session key with deployer address
      console.log("\n🔑 Creating new session key for agent...");
      
      const oneYear = 365 * 24 * 60 * 60;
      
      try {
        const tx = await SessionKeyManager.createSessionKey(
          deployer.address,  // Use deployer as session key
          ethers.parseEther("1.0"),
          oneYear,
          "Agent Session Key - Feb 2026"
        );
        
        await tx.wait();
        console.log("\n✅ New session key created!");
        console.log("   Address:", deployer.address);
        console.log("   Update your .env PRIVATE_KEY to use this address");
        
      } catch (error) {
        console.log("\n❌ Could not create new key:", error.message);
      }
    }
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
