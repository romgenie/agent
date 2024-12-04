export type StructuredMessage = {
  explanation: string;
  decision: boolean;
};

export async function verifyAndExecuteLLMPublic(hash: string): Promise<{ success: boolean; error?: string }> {
  try {
    // Placeholder implementation
    return {
      success: true
    };
  } catch (error) {
    console.error("Error in verifyAndExecuteLLM:", error);
    return {
      success: false,
      error: error instanceof Error ? error.message : "Something went wrong"
    };
  }
}

export async function submitPrompt(
  sessionId: string,
  hash: string,
  prompt: string,
  userWallet: string
): Promise<void> {
  try {
    const response = await fetch("/api/submitPrompt",  {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sessionId,
        hash,
        prompt,
        userWallet,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Failed to submit prompt");
    }

    return await response.json();

  } catch (error) {
    console.error("Error submitting prompt:", error);
    throw error;
  }
}
