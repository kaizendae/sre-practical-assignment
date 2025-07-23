const express = require('express');
const app = express();
const port = 8082;

app.get('/', (req, res) => {
  res.send('Hello from Node.js API service!');
});

app.listen(port, () => {
  console.log(`API service listening at http://localhost:${port}`);
});
