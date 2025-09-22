# How to Set Up InsureContent Pro on Your Computer

## Option 1: Download the Complete Project Files

I'll provide you with all the project files so you can run it locally on your computer.

### Step 1: Download Project Files
You'll need to download these folders from the sandbox:
- `insurance_content_api/` (Backend)
- `insurance-content-frontend/` (Frontend)

### Step 2: Install Prerequisites
Make sure you have these installed on your computer:

**Python 3.11+**
- Download from: https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

**Node.js 22.13.0+**
- Download from: https://nodejs.org/
- This includes npm automatically

**pnpm (Package Manager)**
- After installing Node.js, run: `npm install -g pnpm`

### Step 3: Set Up Backend

1. **Open Terminal/Command Prompt** and navigate to the backend folder:
   ```bash
   cd insurance_content_api
   ```

2. **Create Virtual Environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate Virtual Environment:**
   - **Windows:** `venv\Scripts\activate`
   - **Mac/Linux:** `source venv/bin/activate`

4. **Install Dependencies:**
   ```bash
   pip install flask flask-cors
   ```

5. **Start Backend Server:**
   ```bash
   cd src
   python main_local.py
   ```

   You should see:
   ```
   🚀 Starting InsureContent Pro Local Development Server...
   📍 Backend API: http://localhost:5000
   ✨ Features enabled:
      - User registration and authentication
      - AI-powered content generation
      - Content schedule management
   🔧 Ready for testing!
   ```

### Step 4: Set Up Frontend

1. **Open a NEW Terminal/Command Prompt** and navigate to frontend folder:
   ```bash
   cd insurance-content-frontend
   ```

2. **Install Dependencies:**
   ```bash
   pnpm install
   ```

3. **Start Frontend Server:**
   ```bash
   pnpm run dev
   ```

   You should see:
   ```
   VITE v6.3.5  ready in 740 ms
   ➜  Local:   http://localhost:5173/
   ```

### Step 5: Access the Application

1. **Open your web browser**
2. **Go to:** `http://localhost:5173`
3. **You should see the InsureContent Pro login page!**

---

## Option 2: Quick Test in Sandbox (Immediate Access)

If you want to test RIGHT NOW without downloading anything, I can expose the sandbox environment temporarily:

### Current Sandbox Status:
- **Backend:** Running on port 5001
- **Frontend:** Running on port 5174
- **Both servers are active and ready**

### To Access Sandbox Version:
The sandbox environment is running but only accessible within the sandbox. However, I can create a simple test interface that you can access immediately.

---

## Option 3: I'll Create a Downloadable Package

Let me create a complete downloadable package with everything pre-configured:

### What I'll Include:
- ✅ Complete backend with all features
- ✅ Complete frontend with professional UI
- ✅ Setup scripts for easy installation
- ✅ README with step-by-step instructions
- ✅ Sample data and test accounts
- ✅ All dependencies listed

### Package Contents:
```
InsureContentPro-LocalDev/
├── backend/
│   ├── main_local.py
│   ├── requirements.txt
│   └── setup.bat (Windows) / setup.sh (Mac/Linux)
├── frontend/
│   ├── src/ (all React components)
│   ├── package.json
│   └── setup.bat (Windows) / setup.sh (Mac/Linux)
├── README.md
└── START_HERE.md
```

---

## Which Option Would You Prefer?

**Option 1:** I'll provide download links for all project files
**Option 2:** I'll create a simple test interface you can access immediately  
**Option 3:** I'll create a complete downloadable package with setup scripts

**Recommendation:** Option 3 gives you the easiest setup experience with automated scripts that handle all the installation steps.

Let me know which option you'd prefer, and I'll get it ready for you immediately!
