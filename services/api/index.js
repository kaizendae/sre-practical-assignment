require('dotenv').config();
const express = require('express');
const { Pool } = require('pg');

const app = express();
const port = 3000;

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
});

app.get('/', (req, res) => {
  res.send('Hello from Node.js API service!');
});

app.get('/healthz', (req, res) => {
  res.status(200).send('OK');
});

app.get('/readyz', async (req, res) => {
  try {
    const client = await pool.connect();
    client.release();
    res.status(200).send('OK');
  } catch (err) {
    res.status(500).send('db not ready');
  }
});

app.listen(port, () => {
  console.log(`API service listening at http://localhost:${port}`);
});
