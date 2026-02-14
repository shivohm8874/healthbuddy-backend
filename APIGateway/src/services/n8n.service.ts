import axios from "axios";
import { ENV } from "../config/env.js";

export async function callN8N(data: {
  type: string;
  payload: string;
}) {
  const res = await axios.post(ENV.N8N_WEBHOOK_URL, data, {
    timeout: 60000,
  });

  return res.data;
}
