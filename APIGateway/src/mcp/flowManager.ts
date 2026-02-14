import { callN8N } from "../services/n8n.service.js";

type FlowInput = {
  mode: "chat" | "voice" | "video";
  input: string;
};

export async function routeFlow(data: FlowInput) {
  // later this becomes smarter
  return callN8N({
    type: data.mode,
    payload: data.input,
  });
}
