"use client";
import { getSolanaBalance } from "@/app/actions/solana";
import Image from "next/image";
import { useState, useEffect } from "react";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { Button } from "@/components/ui/button";

import { getConnectedAddress, solanaConfig } from "@/app/wagmi";

export function ConnectWallet() {
  return (
    <div className="flex items-center gap-2">
      {/* Commenting out solana wallet for now */}
      {/* <SolanaWallet /> */}
      <ConnectButton />
    </div>
  );
}

export function SolanaWallet() {
  const [solanaBalance, setSolanaBalance] = useState(0);
  const [solanaAddress, setSolanaAddress] = useState("");

  useEffect(() => {
    getConnectedAddress().then((address) => {
      console.log("address", address);
      setSolanaAddress(address);
    });
  }, []);
  useEffect(() => {
    if (!solanaAddress) return;
    async function fetchBalance() {
      const { balance, success } = await getSolanaBalance(solanaAddress);
      if (success && balance) setSolanaBalance(balance);
    }
    fetchBalance();
  }, [solanaAddress]);

  if (!solanaAddress) return null;
  return (
    <Button
      variant="outline"
      className="flex items-center gap-2 h-10 px-4 border rounded-lg"
    >
      <Image aria-hidden src="/solana.png" alt="" width={40} height={40} />
      <span className="font-medium">{solanaBalance} SOL</span>

      <span>{solanaConfig.network === "devnet" ? "Devnet" : ""}</span>
      <span className="text-muted-foreground text-sm">
        {solanaAddress.slice(0, 4)}...{solanaAddress.slice(-4)}
      </span>
    </Button>
  );
}
