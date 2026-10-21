"use strict";
const express = require("express");
const app = express();
const port = Number(process.env.ADMIN_PORT || 3001);
const host = process.env.ADMIN_HOST || "127.0.0.1";
app.disable("x-powered-by");
app.get("/api/health", (_req, res) => res.json({ status: "ok", service: "admin" }));
// Fail closed until administrator authentication and authorization are implemented.
// Neither the mock admin UI nor any management API is exposed.
app.use((_req, res) => res.status(503).json({ error: "Admin service not yet available" }));
app.listen(port, host, () => console.log("Admin server listening on " + host + ":" + port));
