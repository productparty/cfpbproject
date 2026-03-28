const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');

const allowedOrigins = [
  /^https?:\/\/(www\.)?mikewatson\.us$/,
  /^https?:\/\/localhost(:\d+)?$/,
  /^https?:\/\/127\.0\.0\.1(:\d+)?$/,
];

module.exports = (req, res) => {
  const origin = req.headers.origin || '';
  const allowed = !origin || allowedOrigins.some(p => p.test(origin));

  res.setHeader('Access-Control-Allow-Origin', allowed ? origin || '*' : '');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Vary', 'Origin');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (!allowed) return res.status(403).json({ error: 'Forbidden' });

  const { TABLEAU_CLIENT_ID, TABLEAU_SECRET_ID, TABLEAU_SECRET_VALUE, TABLEAU_USER_EMAIL } = process.env;

  if (!TABLEAU_CLIENT_ID || !TABLEAU_SECRET_ID || !TABLEAU_SECRET_VALUE || !TABLEAU_USER_EMAIL) {
    return res.status(500).json({ error: 'Missing Tableau configuration' });
  }

  const now = Math.floor(Date.now() / 1000);

  const token = jwt.sign(
    {
      sub: TABLEAU_USER_EMAIL,
      aud: 'tableau',
      jti: uuidv4(),
      iss: TABLEAU_CLIENT_ID,
      scp: ['tableau:views:embed'],
      exp: now + 300,
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
};
