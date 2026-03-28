require('dotenv').config();
const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');

const app = express();

const allowedOrigins = [
  /^https?:\/\/(www\.)?mikewatson\.us$/,
  /^https?:\/\/localhost(:\d+)?$/,
  /^https?:\/\/127\.0\.0\.1(:\d+)?$/,
];

app.use(cors({
  origin: (origin, callback) => {
    // Allow requests with no origin (e.g., curl, same-origin file://)
    if (!origin) return callback(null, true);
    if (allowedOrigins.some(pattern => pattern.test(origin))) {
      return callback(null, true);
    }
    callback(new Error('Not allowed by CORS'));
  },
}));

app.get('/api/tableau-token', (req, res) => {
  const { TABLEAU_CLIENT_ID, TABLEAU_SECRET_ID, TABLEAU_SECRET_VALUE, TABLEAU_USER_EMAIL } = process.env;

  if (!TABLEAU_CLIENT_ID || !TABLEAU_SECRET_ID || !TABLEAU_SECRET_VALUE || !TABLEAU_USER_EMAIL) {
    return res.status(500).json({ error: 'Missing Tableau configuration in .env' });
  }

  const now = Math.floor(Date.now() / 1000);

  const token = jwt.sign(
    {
      sub: TABLEAU_USER_EMAIL,
      aud: 'tableau',
      jti: uuidv4(),
      iss: TABLEAU_CLIENT_ID,
      scp: ['tableau:views:embed'],
      exp: now + 300, // 5 minutes
    },
    TABLEAU_SECRET_VALUE,
    {
      algorithm: 'HS256',
      header: {
        alg: 'HS256',
        typ: 'JWT',
        iss: TABLEAU_CLIENT_ID,
        kid: TABLEAU_SECRET_ID,
      },
    }
  );

  res.json({ token });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Tableau token server running on http://localhost:${PORT}`);
});
