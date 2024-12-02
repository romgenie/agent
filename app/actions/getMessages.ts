// import { db } from "@/app/lib/db";
// import { messages } from "@/lib/db/schema";
import { eq } from "drizzle-orm";

export type TMessage = {
  id: string;
  content: string;
  role: "user" | "assistant" | "system";
  userWallet?: string;
  createdAt: Date;
  isWinner?: boolean;
  fullConversation?: string;
  txHash?: string;
};

export async function getRecentMessages(userWallet?: string, limit: number = 50): Promise<TMessage[]> {
  try {
    // let query = db.select().from(messages).orderBy(messages.createdAt).limit(limit);
    //
    // if (userWallet) {
    //   query = query.where(eq(messages.userWallet, userWallet));
    // }
    //
    // const result = await query;
    // return result.map((msg) => ({
    //   id: msg.id,
    //   content: msg.content,
    //   role: msg.role,
    //   userWallet: msg.userWallet,
    //   createdAt: msg.createdAt,
    //   isWinner: msg.isWinner,
    //   fullConversation: msg.fullConversation,
    //   txHash: msg.txHash,
    // }));
    return []
  } catch (error) {
    console.error("Error fetching messages:", error);
    return [];
  }
}

export async function getMessageByTxHash(txHash: string): Promise<TMessage | undefined> {
  try {
    // const result = await db
    //   .select()
    //   .from(messages)
    //   .where(eq(messages.txHash, txHash))
    //   .limit(1);
    //
    // if (result.length === 0) return undefined;
    //
    // const msg = result[0];
    // return {
    //   id: msg.id,
    //   content: msg.content,
    //   role: msg.role,
    //   userWallet: msg.userWallet,
    //   createdAt: msg.createdAt,
    //   isWinner: msg.isWinner,
    //   fullConversation: msg.fullConversation,
    //   txHash: msg.txHash,
    // };
    return
  } catch (error) {
    console.error("Error fetching message by txHash:", error);
    return undefined;
  }
}
