# TryllEngine Website

A marketing website for TryllEngine with backend API for contact form submissions.

## Features

- Static marketing website with modern design
- Contact form with backend API
- SQLite database for storing submissions
- Team page with project showcase
- Rate limiting and basic validation
- Responsive design

## Setup

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. For production:
   ```bash
   npm start
   ```

The server will start on `http://localhost:3000`

### Database

The application uses SQLite for storing contact form submissions. The database file (`contacts.db`) will be created automatically when you first run the server.

### API Endpoints

- `POST /api/contact` - Submit contact form
- `GET /api/admin/contacts` - View all submissions (admin only)

### Project Structure

```
TryllEngine/
├── index.html          # Main landing page
├── team.html           # Team page with project showcase
├── server.js           # Backend API server
├── package.json        # Dependencies and scripts
├── contacts.db         # SQLite database (created automatically)
├── logo/              # Logo assets
└── README.md          # This file
```

### Features

#### Contact Form
- Name, email, and category fields
- Client-side and server-side validation
- Rate limiting (5 submissions per 15 minutes per IP)
- Stores submissions in SQLite database

#### Team Page
- Showcases team expertise and game projects
- Placeholder portraits for team members
- Project details with platforms and contributions

### Development

For development with auto-reload:
```bash
npm run dev
```

For production deployment:
```bash
npm start
```

### Security Notes

- Rate limiting implemented for contact form
- Basic input validation
- CORS enabled for development
- Admin endpoint needs authentication in production

### Deployment

1. Install dependencies on server
2. Set `NODE_ENV=production`
3. Start with `npm start`
4. Use process manager like PM2 for production

### Contact Form Data

Submissions include:
- Name
- Email
- Category (Studio, Solo Developer, Modder, Other)
- Timestamp
- IP address (for rate limiting)

Access submissions via `/api/admin/contacts` (add authentication for production use).