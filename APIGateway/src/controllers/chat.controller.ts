import { Request, Response } from "express";
import { routeFlow } from "../mcp/flowManager.js";

export async function chatController(req: Request, res: Response) {
  try {
    const { input, mode } = req.body;

    if (!input || !mode) {
      return res.status(400).json({ error: "input and mode required" });
    }

    const result = await routeFlow({
      mode, // chat | voice | video
      input,
    });

    res.json(result);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Internal server error" });
  }
}
