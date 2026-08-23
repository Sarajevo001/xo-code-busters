const http = require("http");

const server = http.createServer((req, res) => {
    res.setHeader(
        "Access-Control-Allow-Origin",
        "http://127.0.0.1:5500"
    );

    res.setHeader(
        "Access-Control-Allow-Headers",
        "Content-Type"
    );

    if (req.method === "OPTIONS") {
        res.writeHead(204);
        res.end();
        return;
    }

    if (req.method === "GET" && req.url === "/api/health") {
        res.writeHead(200, {
            "Content-Type": "application/json; charset=utf-8"
        });

        res.end(JSON.stringify({
            status: "ok"
        }));

        return;
    }

    if (req.method === "POST" && req.url === "/api/hello") {
        let body = "";

        req.on("data", chunk => {
            body += chunk;
        });

        req.on("end", () => {
            const data = JSON.parse(body);

            res.writeHead(200, {
                "Content-Type": "application/json; charset=utf-8"
            });

            res.end(JSON.stringify({
                message: `Hello, ${data.name}`
            }));
        });

        return;
    }

    res.writeHead(404, {
        "Content-Type": "application/json; charset=utf-8"
    });

    res.end(JSON.stringify({
        error: "Not Found"
    }));
});

server.listen(3000, () => {
    console.log("Server started: http://localhost:3000");
});