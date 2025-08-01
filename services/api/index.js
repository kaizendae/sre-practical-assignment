require('dotenv').config();
const express = require('express');
const promBundle = require("express-prom-bundle");
const { Pool } = require('pg');
const pino = require('pino');
const pinoHttp = require('pino-http');

const logger = pino({
  level: 'info',
  timestamp: pino.stdTimeFunctions.isoTime,
  formatters: {
    level: (label) => {
      return { level: label };
    },
  },
});

const httpLogger = pinoHttp({ logger });


const app = express();
const port = 3000;
app.use(httpLogger);

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
});

// Add the options to the prometheus middleware most option are for http_request_duration_seconds histogram metric
const metricsMiddleware = promBundle({
 includeMethod: true, 
 includePath: true, 
 includeStatusCode: true, 
 includeUp: true,
 customLabels: {project_name: 'hello_world', project_type: 'test_metrics_labels'},
 promClient: {
 collectDefaultMetrics: {
  prefix: 'my_app_',
 }
 }
});

// add the prometheus middleware to all routes
app.use(metricsMiddleware)

function getRandomNumber(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min);
}

app.get('/', (req, res) => {
  res.send(`
    <h1>Node.js API Service</h1>
    <p>Welcome! Here are the available endpoints:</p>
    <ul>
      <li><b>GET <a href="/">/</a></b> - Show this directory</li>
      <li><b>GET <a href="/healthz">/healthz</a></b> - Liveness probe, returns 200 OK if service is up</li>
      <li><b>GET <a href="/readyz">/readyz</a></b> - Readiness probe, returns 200 OK if DB is ready, 500 otherwise</li>
      <li><b>GET <a href="/metrics">/metrics</a></b> - Prometheus metrics endpoint</li>
      <li><b>GET <a href="/rolldice">/rolldice</a></b> - Roll a dice, returns a random number between 1 and 6</li>
    </ul>
  `);
});

app.get('/healthz', (req, res) => {
  res.status(200).send('OK');
});

app.get('/readyz', async (req, res) => {
  try {
    const client = await pool.connect();
    client.release();
    logger.info('Database connection successful');
    res.status(200).send('OK');
  } catch (err) {
    logger.error({ error: err }, 'Database connection failed');
    res.status(500).send('db not ready');
  }
});

app.get('/rolldice', (req, res) => {
  const result = getRandomNumber(1, 6);
  logger.info({ result }, 'Dice rolled');
  res.send(result.toString());
});

app.listen(port, () => {
  logger.info(`API service listening at http://localhost:${port}`);
});
