// server.js
import express from "express";
import fetch from "node-fetch";
import cors from "cors";

const app = express();
app.use(cors()); 
app.use(express.json());

const ARANGO_HOST = "http://10.21.86.67:8529";
const ARANGO_DB = "gtm";
const ARANGO_USER = "root";
const ARANGO_PASS = "";
const ARANGO_COLLECTION = "gtm_posts";
const ARANGO_GMT_WEEKLY_COLLECTION = "gmt_weekly_analysis";


async function arangoFetch(path, options = {}) {
  const url = `${ARANGO_HOST}/_db/${ARANGO_DB}${path}`;
  const headers = {
    Authorization: `Basic ${Buffer.from(`${ARANGO_USER}:${ARANGO_PASS}`).toString("base64")}`,
    "Content-Type": "application/json",
    ...options.headers,
  };

  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`ArangoDB Error ${res.status}: ${text}`);
  }
  return res.json();
}

app.get("/api/posts", async (req, res) => {
    try {
      const body = { collection: ARANGO_COLLECTION };
      const data = await arangoFetch("/_api/simple/all", {
        method: "PUT",
        body: JSON.stringify(body),
      });
  
      res.json(data.result || []); 
    } catch (err) {
      console.error("Error fetching from ArangoDB:", err.message);
      res.status(500).json({ error: err.message });
    }
  });
  // app.get("/api/weekly_report", async (req, res) => {
  //   try {
  //     const body = { collection: ARANGO_GMT_COLLECTION };
  //     const data = await arangoFetch("/_api/simple/all", {
  //       method: "PUT",
  //       body: JSON.stringify(body),
  //     });
  
  //     res.json(data.result || []); 
  //   } catch (err) {
  //     console.error("Error fetching from ArangoDB:", err.message);
  //     res.status(500).json({ error: err.message });
  //   }
  // });
app.get("/", (req, res) => {
  res.send("✅ Arango Proxy Server Running");
});

const PORT = 4000;
app.listen(PORT, () => console.log(`Proxy server running at http://localhost:${PORT}`));
