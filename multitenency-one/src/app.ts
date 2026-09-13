import express from "express";
import type { NextFunction, Request, Response } from "express";
import cors from "cors";
import tenantRoutes from "./routes/tenant.routes";
const app = express();

app.use(cors());
app.use(express.json());
app.use("/api", tenantRoutes);

// Without this, Express's default handler replies with an HTML stack trace that
// leaks absolute paths and source lines to the caller.
app.use((err: unknown, _req: Request, res: Response, _next: NextFunction) => {
  console.error(err);
  res.status(500).json({ error: "Internal server error" });
});

export default app;
