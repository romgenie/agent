import ollama from 'ollama';
import type { Message, StructuredMessage } from "./types";

export interface SendMessageOptions {
  messages: Message[];
  maxTokens?: number;
}

export async function sendMessage({
  messages,
  maxTokens = 1000,
}: SendMessageOptions): Promise<StructuredMessage> {
  const model = process.env.OLLAMA_MODEL;

  let systemPrompt: string | undefined;
  let messagesToSend = messages;

  if (messages[0]?.role === "system") {
    systemPrompt = messages[0].content;
    messagesToSend = messages.slice(1);
  }

  // Convert messages to Ollama format
  const ollamaMessages = messagesToSend.map((msg) => ({
    role: msg.role === "assistant" ? "assistant" : "user",
    content: msg.content,
  }));

  // Add system prompt if exists
  if (systemPrompt) {
    ollamaMessages.unshift({
      role: "system",
      content: systemPrompt,
    });
  }

  try {
    // First call with tools
    const response = await ollama.chat({
      model: model!,
      messages: ollamaMessages,
      tools: [
        {
          type: 'function',
          function: {
            name: 'approveTransfer',
            description: 'Approve the money transfer request and provide explanation',
            parameters: {
              type: 'object',
              properties: {
                explanation: {
                  type: 'string',
                  description: 'Explanation for why the money transfer is approved',
                },
              },
              required: ['explanation'],
            },
          },
        },
        {
          type: 'function',
          function: {
            name: 'rejectTransfer',
            description: 'Reject the money transfer request and provide explanation',
            parameters: {
              type: 'object',
              properties: {
                explanation: {
                  type: 'string',
                  description: 'Explanation for why the money transfer is rejected',
                },
              },
              required: ['explanation'],
            },
          },
        },
      ],
    });

    // Add model's response to conversation
    ollamaMessages.push(response.message);

    // Check if the model used any tools
    if (response.message.tool_calls && response.message.tool_calls.length > 0) {
      const tool = response.message.tool_calls[0];
      const args = tool.function.arguments;

      if (tool.function.name === 'approveTransfer') {
        return {
          explanation: args.explanation,
          decision: true,
        };
      } else if (tool.function.name === 'rejectTransfer') {
        return {
          explanation: args.explanation,
          decision: false,
        };
      }
    }

    // If no tool calls, try to parse the response
    try {
      const parsedResponse = JSON.parse(response.message.content);
      return {
        explanation: parsedResponse.explanation,
        decision: parsedResponse.decision,
      };
    } catch (e) {
      // If not JSON, use the raw response text
      const responseText = response.message.content;
      
      // Simple heuristic: check if the response contains approval-related words
      const isApproval = responseText.toLowerCase().includes('approve') || 
                        responseText.toLowerCase().includes('accept') ||
                        responseText.toLowerCase().includes('valid');

      return {
        explanation: responseText,
        decision: isApproval,
      };
    }
  } catch (error) {
    console.error("Error with Ollama:", error);
    return {
      explanation: "Failed to process request with Ollama",
      decision: false,
    };
  }
}
