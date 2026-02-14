import "dotenv/config";

export const ENV = {
  PORT: process.env.PORT || 8080,
  N8N_WEBHOOK_URL: process.env.N8N_WEBHOOK_URL!,
};
