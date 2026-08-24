const http = require("http");
const fs = require("fs");
const path = require("path");

const root = process.cwd();
const types = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".svg": "image/svg+xml", ".json": "application/json", ".png": "image/png", ".jpg": "image/jpeg" };

http.createServer((request, response) => {
  const relative = decodeURIComponent(request.url.split("?")[0] || "/");
  const file = path.resolve(root, relative === "/" ? "index.html" : `.${relative}`);
  if (!file.startsWith(root)) { response.statusCode = 403; response.end("Forbidden"); return; }
  fs.readFile(file, (error, data) => {
    if (error) { response.statusCode = 404; response.end("Not found"); return; }
    response.setHeader("Content-Type", types[path.extname(file).toLowerCase()] || "application/octet-stream");
    response.end(data);
  });
}).listen(8766, "127.0.0.1", () => console.log("http://127.0.0.1:8766/index.html"));
