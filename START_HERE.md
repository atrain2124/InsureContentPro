# 🚀 START HERE - InsureContent Pro Local Development

## Welcome to InsureContent Pro!

This package contains everything you need to run the complete InsureContent Pro platform on your computer for testing and development.

## 📋 What's Included

- ✅ **Complete Backend API** with authentication and content generation
- ✅ **Professional React Frontend** with modern UI/UX
- ✅ **Automated Setup Scripts** for easy installation
- ✅ **Sample Data & Content** for immediate testing
- ✅ **Comprehensive Documentation** for all features

## 🎯 Quick Start (Choose Your Platform)

### Windows Users
1. **Double-click:** `setup_windows.bat`
2. **Wait for setup to complete** (2-3 minutes)
3. **Double-click:** `start_both.bat`
4. **Open browser:** `http://localhost:5173`

### Mac/Linux Users
1. **Open Terminal** in this folder
2. **Run:** `chmod +x setup_mac_linux.sh && ./setup_mac_linux.sh`
3. **Run:** `./start_both.sh`
4. **Open browser:** `http://localhost:5173`

## 🧪 Test the Platform

### 1. Create Account
- Click "Start your free trial"
- Use any email (e.g., `test@example.com`)
- Password: minimum 6 characters
- Name: Your name

### 2. Generate Content
- Click "Generate New Content"
- Select insurance types (try "Mortgage Protection" + "IUL")
- Choose tone (try "Professional")
- Add custom instructions (optional)
- Click "Generate Content"

### 3. View Results
- See your 7-day content schedule
- Click "Copy Post" to copy content
- View hashtags and image prompts
- Navigate between different days

## 🎨 What You'll See

**Professional Social Media Posts Like:**
```
🏠 Protecting your family's future starts with the right insurance coverage. 
As a professional insurance professional, I help families secure their most 
valuable asset - their home and loved ones. 
#InsuranceProtection #FamilyFirst #MortgageProtection
```

**Features to Test:**
- User registration and login
- Content generation with multiple insurance types
- Different content tones (Professional, Friendly, Urgent, etc.)
- Weekly content schedules
- Copy-to-clipboard functionality
- Subscription status tracking
- Responsive design (try on mobile)

## 🔧 Manual Setup (If Scripts Don't Work)

### Backend Setup
```bash
cd insurance_content_api
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install flask flask-cors
cd src
python main_local.py
```

### Frontend Setup (New Terminal)
```bash
cd insurance-content-frontend
npm install -g pnpm
pnpm install
pnpm run dev
```

## 🌐 Access URLs

- **Frontend (Main App):** http://localhost:5173
- **Backend API:** http://localhost:5000
- **API Health Check:** http://localhost:5000/api/health

## 📚 Documentation

- **README.md** - Project overview
- **USER_GUIDE.md** - How to use the platform
- **DEVELOPER_GUIDE.md** - Technical documentation
- **LOCAL_SETUP_GUIDE.md** - Detailed setup instructions

## 🎯 Key Features to Test

### Content Generation
- **6 Insurance Types:** Mortgage Protection, IUL, Term Life, Final Expense, Annuities, Health
- **6 Content Tones:** Professional, Friendly, Direct, Serious, Funny, Urgent
- **Custom Instructions:** Add personalized messaging
- **Weekly Schedules:** 7 days of content at once

### User Management
- **Registration:** Email-based account creation
- **Authentication:** Secure login/logout
- **Trial Management:** 7-day free trial tracking
- **Session Persistence:** Stay logged in

### Professional UI
- **Modern Design:** Clean, trustworthy interface
- **Responsive Layout:** Works on desktop, tablet, mobile
- **Intuitive Navigation:** Easy-to-use dashboard
- **Professional Branding:** Insurance industry focused

## 🚨 Troubleshooting

### Port Already in Use
- **Backend:** Edit `main_local.py`, change port from 5000 to 5001
- **Frontend:** Vite will automatically try next available port

### Python Not Found
- Install Python 3.11+ from https://python.org
- Make sure "Add to PATH" is checked during installation

### Node.js Not Found
- Install Node.js from https://nodejs.org
- Restart terminal after installation

### Permission Denied (Mac/Linux)
```bash
chmod +x setup_mac_linux.sh
chmod +x start_both.sh
```

## 💡 Pro Tips

1. **Test Different Tones:** Try "Urgent" vs "Friendly" to see content variations
2. **Mix Insurance Types:** Select multiple types for diverse content
3. **Custom Instructions:** Add "focus on young families" or "mention local events"
4. **Copy Content:** Use the copy button to test in real social media platforms
5. **Mobile Testing:** Resize browser window to test responsive design

## 🎉 Success Indicators

You'll know it's working when you see:
- ✅ Professional login page loads
- ✅ Registration creates account successfully
- ✅ Dashboard shows trial status
- ✅ Content generator creates 7 posts
- ✅ Posts have realistic insurance content
- ✅ Copy button works
- ✅ Navigation is smooth and responsive

## 📞 Next Steps

Once you've tested locally:
1. **Customize Content:** Modify templates in `main_local.py`
2. **Add OpenAI:** Set `OPENAI_API_KEY` for real AI generation
3. **Add Stripe:** Set up payment processing
4. **Deploy Live:** Use deployment guide for production

---

**🎯 Ready to test? Start with the setup script for your platform and you'll be running InsureContent Pro in minutes!**
