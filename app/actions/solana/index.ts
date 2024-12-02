import { Connection, PublicKey } from "@solana/web3.js";

export async function getSolanaBalance(address: string): Promise<number> {
  try {
    const connection = new Connection(
      process.env.NEXT_PUBLIC_SOLANA_RPC_URL || "https://api.mainnet-beta.solana.com"
    );
    
    const publicKey = new PublicKey(address);
    const balance = await connection.getBalance(publicKey);
    
    // Convert lamports to SOL (1 SOL = 1e9 lamports)
    return balance / 1e9;
  } catch (error) {
    console.error("Error fetching Solana balance:", error);
    return 0;
  }
}
