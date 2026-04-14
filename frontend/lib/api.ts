const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface StreamDonePayload {
  fullResponse: string;
  topicsCovered: string[];
}

/**
 * Stream a chat response from the Attune tutor API.
 * Calls onChunk with each text token, calls onDone with the full response and updated topics.
 */
export async function streamChat(
  sessionId: string,
  message: string,
  mode: string,
  onChunk: (text: string) => void,
  onDone: (payload: StreamDonePayload) => void,
  onError: (err: string) => void
): Promise<void> {
  try {
    const response = await fetch(`${API_URL}/tutor/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message, mode }),
    });

    if (!response.ok) {
      onError("The tutor is unavailable right now. Please try again.");
      return;
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    if (!reader) { onError("Stream unavailable"); return; }

    let fullResponse = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split("\n");

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6).trim();
          try {
            const parsed = JSON.parse(data);
            if (parsed.text) {
              fullResponse += parsed.text;
              onChunk(parsed.text);
            } else if (parsed.done) {
              onDone({
                fullResponse,
                topicsCovered: parsed.topics_covered ?? [],
              });
              return;
            }
          } catch {}
        }
      }
    }

    onDone({ fullResponse, topicsCovered: [] });
  } catch (e) {
    onError("Connection error. Is the backend running?");
  }
}

/**
 * Fetch full session data for export (messages + metadata).
 */
export async function fetchSessionExport(sessionId: string) {
  const res = await fetch(`${API_URL}/tutor/session/${sessionId}/export`);
  if (!res.ok) throw new Error("Export failed");
  return res.json();
}
