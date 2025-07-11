const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const cors = require('cors');
const rateLimit = require('express-rate-limit');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(cors());
app.use(express.static('.'));

// Rate limiting
const contactLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // limit each IP to 5 requests per windowMs
  message: 'Too many contact form submissions, please try again later.'
});

// Database setup
const db = new sqlite3.Database('./contacts.db');

// Create contacts table if it doesn't exist
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    category TEXT,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT
  )`);
});

// Contact form submission endpoint
app.post('/api/contact', contactLimiter, (req, res) => {
  const { name, email, category } = req.body;
  const ip_address = req.ip || req.connection.remoteAddress;

  // Basic validation
  if (!name || !email) {
    return res.status(400).json({ error: 'Name and email are required' });
  }

  // Email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return res.status(400).json({ error: 'Invalid email format' });
  }

  // Insert into database
  const stmt = db.prepare(`INSERT INTO contacts (name, email, category, ip_address) VALUES (?, ?, ?, ?)`);
  stmt.run([name, email, category || null, ip_address], function(err) {
    if (err) {
      console.error('Database error:', err);
      return res.status(500).json({ error: 'Internal server error' });
    }
    
    res.json({ 
      success: true, 
      message: `Thank you, ${name}! We'll keep ${email} updated on Tryll Engine's progress.`,
      id: this.lastID 
    });
  });
  stmt.finalize();
});

// Admin endpoint to view submissions (basic auth would be needed in production)
app.get('/api/admin/contacts', (req, res) => {
  db.all('SELECT * FROM contacts ORDER BY submitted_at DESC', (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Database error' });
    }
    res.json(rows);
  });
});

// Serve static files
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  db.close((err) => {
    if (err) {
      console.error(err.message);
    }
    console.log('Database connection closed.');
    process.exit(0);
  });
});