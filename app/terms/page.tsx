import { getGameState } from "@/app/actions/getGameState";
import { Terms } from "./components/Terms";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function Page() {
  const gameState = await getGameState();

  return <Terms gameState={gameState} />;
}
