const express = require("express");
const path = require("node:path");

const app = express();
const port = Number(process.env.PORT || 3000);

app.use(express.json());

app.get("/api/health", (req, res) => {
    res.json({ status: "ok" });
});

app.post("/api/hello", (req, res) => {
    res.json({ message: `Hello, ${req.body.name}` });
});

app.use(express.static(path.join(__dirname, "../client")));

app.use((req, res) => {
    res.status(404).json({ error: "Not Found" });
});

app.listen(port, "127.0.0.1", () => {
    console.log(`Server started: http://127.0.0.1:${port}`);
});
