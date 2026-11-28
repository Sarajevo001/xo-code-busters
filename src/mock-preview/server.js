"use strict";
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const routes = new Map([
    ["/", ["client/mock.html", "text/html"]],
    ["/client/mock.html", ["client/mock.html", "text/html"]],
    ["/public/js/user-mock.js", ["public/js/user-mock.js", "text/javascript"]],
    ["/admin/", ["admin-client/index.html", "text/html"]],
    ["/admin/app.js", ["admin-client/app.js", "text/javascript"]],
    ["/admin/styles.css", ["admin-client/styles.css", "text/css"]]
]);
const port = Number(process.env.MOCK_PORT || 3100);
http.createServer((req, res) => {
    const route = routes.get(req.url);
    if (req.method !== "GET" || !route) {
        res.writeHead(404).end();
        return;
    }
    fs.readFile(path.join(root, route[0]), (error, data) => {
        if (error) {
            res.writeHead(500).end();
            return;
        }
        res.writeHead(200, {
            "Content-Type": route[1] + "; charset=utf-8",
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff"
        }).end(data);
    });
}).listen(port, "127.0.0.1", () => {
    console.log("Mock preview: http://127.0.0.1:" + port);
});
