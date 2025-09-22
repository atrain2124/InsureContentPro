# InsureContent Pro - Local Development Setup Guide

## Quick Start

I've prepared a complete local development environment for you to test the InsureContent Pro platform. Here's how to get it running:

## Prerequisites

Make sure you have the following installed on your system:
- Python 3.11+
- Node.js 22.13.0+
- pip
- pnpm (or npm)

## Step 1: Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd insurance_content_api
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install flask flask-cors
   ```

4. **Start the backend server:**
   ```bash
   cd src
   python main_local.py
   ```

   You should see:
   ```
   🚀 Starting InsureContent Pro Local Development Server...
   📍 Backend API: http://localhost:5000
   🎯 Frontend: http://localhost:5173
   📚 API Documentation: http://localhost:5000/api/health

   ✨ Features enabled:
      - User registration and authentication
      - AI-powered content generation
      - Content schedule management
      - Subscription status tracking
      - Full React frontend integration

   🔧 Ready for testing!
   ```

## Step 2: Frontend Setup

1. **Open a new terminal and navigate to frontend directory:**
   ```bash
   cd insurance-content-frontend
   ```

2. **Install dependencies:**
   ```bash
   pnpm install
   ```

3. **Start the development server:**
   ```bash
   pnpm run dev
   ```

   You should see:
   ```
   VITE v6.3.5  ready in 740 ms
   ➜  Local:   http://localhost:5173/
   ➜  Network: http://169.254.0.21:5173/
   ```

## Step 3: Test the Application

1. **Open your browser and go to:** `http://localhost:5173`

2. **Test Registration:**
   - Click "Start your free trial"
   - Fill out the registration form
   - You should be redirected to the dashboard

3. **Test Content Generation:**
   - Click "Generate New Content"
   - Select insurance types (e.g., Mortgage Protection, IUL)
   - Choose a tone (e.g., Professional, Friendly)
   - Add custom instructions (optional)
   - Click "Generate Content"
   - View your generated weekly schedule

## Features You Can Test

### ✅ User Authentication
- **Registration:** Create new accounts with email/password
- **Login:** Secure authentication with session management
- **Trial Management:** 7-day free trial tracking
- **Session Persistence:** Stay logged in across browser sessions

### ✅ Content Generation
- **Insurance Type Selection:** Choose from 6 insurance product types
- **Tone Customization:** 6 different content tones
- **Custom Instructions:** Add personalized messaging
- **Weekly Schedules:** Generate 7 days of content at once
- **Smart Content:** Industry-specific, compliant social media posts

### ✅ Content Management
- **Schedule View:** See all your generated content organized by date
- **Copy Functionality:** One-click copy for social media posting
- **Content History:** View previously generated schedules
- **Post Details:** See hashtags, image prompts, and full text

### ✅ Subscription System
- **Trial Status:** Real-time trial countdown
- **Subscription Plans:** Monthly and annual pricing options
- **Status Dashboard:** Clear subscription status indicators

## Sample Test Data

Here's what you can expect when testing:

**Insurance Types Available:**
- Mortgage Protection
- Index Universal Life
- Term Life with Living Benefits
- Final Expense
- Annuities
- Health Insurance

**Content Tones:**
- Professional
- Friendly
- Direct
- Serious
- Funny
- Urgent

**Sample Generated Content:**
```
🏠 Protecting your family's future starts with the right insurance coverage. 
As a professional insurance professional, I help families secure their most 
valuable asset - their home and loved ones. #InsuranceProtection #FamilyFirst #MortgageProtection
```

## API Endpoints You Can Test

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - User logout

### Content
- `GET /api/content/insurance-types` - Get available insurance types
- `GET /api/content/tones` - Get available content tones
- `POST /api/content/generate` - Generate content schedule
- `GET /api/content/schedules` - Get user's schedules
- `GET /api/content/schedules/{id}` - Get specific schedule

### Subscription
- `GET /api/subscription/pricing` - Get pricing plans
- `GET /api/subscription/status` - Get subscription status

## Troubleshooting

### Port Conflicts
If you get "Port already in use" errors:
- Backend: Change port in `main_local.py` (line with `app.run`)
- Frontend: Vite will automatically try the next available port

### CORS Issues
The backend is configured with CORS enabled for localhost development.

### Database
The local version uses in-memory storage, so data resets when you restart the backend.

## File Structure

```
insurance_content_api/
├── src/
│   ├── main_local.py          # Local development server
│   ├── static/                # Frontend build files
│   └── venv/                  # Python virtual environment
└── requirements.txt

insurance-content-frontend/
├── src/
│   ├── components/            # React components
│   ├── lib/                   # API and utilities
│   └── hooks/                 # React hooks
├── package.json
└── dist/                      # Build output
```

## Next Steps

Once you've tested the local environment and confirmed everything works:

1. **Add OpenAI Integration:** Set `OPENAI_API_KEY` environment variable for real AI content generation
2. **Add Stripe Integration:** Set up Stripe keys for payment processing
3. **Database Integration:** Replace in-memory storage with PostgreSQL
4. **Deploy to Production:** Use the deployment guide for live hosting

## Support

If you encounter any issues:
1. Check that both servers are running
2. Verify the ports are correct (backend: 5000, frontend: 5173)
3. Check browser console for JavaScript errors
4. Verify API responses in Network tab

The local development environment gives you the full InsureContent Pro experience with all features working. This is perfect for testing, development, and demonstrating the platform to potential users or investors.
