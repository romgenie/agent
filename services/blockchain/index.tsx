import { getMessageByTxHash } from "@/app/actions/getMessageByTxHash";
import { isTxValidEthereum } from "./ethereum";

export const isTxValid = async (
  txHash: string,
  blockchain: string,
  txExpiryMinutes?: number
) => {
  const message = await getMessageByTxHash(txHash, txExpiryMinutes);
  if (!message || !message.price) {
    console.log({ message });
    console.log(`Message not found with hash ${txHash} or price is not set`);
    return false;
  }

  switch (blockchain.toLowerCase()) {
    case "ethereum":
      return isTxValidEthereum(
        txHash,
        message.price,
        process.env.NEXT_PUBLIC_ETHEREUM_CONTRACT_ADDRESS!
      );
    default:
      throw new Error(`Unsupported blockchain: ${blockchain}`);
  }
};
