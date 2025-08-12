# 🌐 Complete Website Setup Guide

## 🎯 **What You'll Get**

A complete news aggregation website with:
- ✅ **React Frontend** - Modern, responsive UI
- ✅ **FastAPI Backend** - Robust API with improved error handling
- ✅ **India Filter** - Now works without breaking when APIs fail
- ✅ **Country Selection** - Filter news by country
- ✅ **Real-time Updates** - Live news from multiple sources

## 🚀 **Quick Start Options**

### Option 1: One-Click Start (Windows)
```bash
# Double-click this file:
start_website_windows.bat
```

### Option 2: Python Script (All Platforms)
```bash
python start_website.py
```

### Option 3: Manual Setup
```bash
# Terminal 1: Start Backend
cd backend
python -m uvicorn main:app --reload

# Terminal 2: Start Frontend
cd frontend
npm start
```

## 📋 **Prerequisites**

### Required Software:
1. **Python 3.8+** - [Download here](https://python.org)
2. **Node.js 16+** - [Download here](https://nodejs.org)

### Check Installation:
```bash
# Check Python
python --version

# Check Node.js
node --version

# Check npm
npm --version
```

## 🔧 **Automatic Setup**

The startup scripts will automatically:
1. ✅ Check dependencies
2. ✅ Install Python packages (uvicorn, fastapi, etc.)
3. ✅ Install frontend packages (React, etc.)
4. ✅ Start backend server (port 8000)
5. ✅ Start frontend server (port 3000)
6. ✅ Open browser automatically

## 📊 **Website Features**

### 🏠 **Homepage**
- Latest news from all sources
- Country filter dropdown
- Real-time updates

### 🇮🇳 **India Filter** (Now Fixed!)
- **Before**: Would crash if any API failed
- **After**: Shows partial results even if some APIs fail
- **Debugging**: Clear ✅/❌ indicators in console

### 🌍 **Country Selection**
- India 🇮🇳
- USA 🇺🇸
- UK 🇬🇧
- Australia 🇦🇺
- Canada 🇨🇦
- Germany 🇩🇪
- France 🇫🇷
- Japan 🇯🇵

## 🧪 **Testing the Improvements**

### 1. **Start the Website**
```bash
# Windows
start_website_windows.bat

# Or Python script
python start_website.py
```

### 2. **Test India Filter**
1. Open http://localhost:3000
2. Select "🇮🇳 India" from dropdown
3. Check console logs for ✅/❌ indicators

### 3. **Expected Results**
```
✅ NewsAPI in: 15 articles
✅ GNews in: 12 articles  
✅ Mediastack in: 8 articles
✅ Currents in: 10 articles
✅ RSS Feeds: 5 articles
🔄 Final results: 45 unique articles
```

## 🔍 **Troubleshooting**

### Issue: "uvicorn not recognized"
**Solution**: The startup scripts will install it automatically

### Issue: "npm not found"
**Solution**: Install Node.js from https://nodejs.org

### Issue: Port already in use
**Solution**: 
```bash
# Kill processes on ports 3000 and 8000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:3000 | xargs kill -9
```

### Issue: Frontend won't start
**Solution**: 
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

## 📁 **File Structure**
```
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── CountryFilter.tsx  # Country selection
│   │   └── App.tsx
│   └── package.json
├── backend/                  # FastAPI backend
│   ├── services/
│   │   └── news_service.py  # ✅ IMPROVED with error handling
│   └── main.py
├── start_website.py         # Python startup script
├── start_website_windows.bat # Windows startup script
└── WEBSITE_SETUP.md        # This guide
```

## 🎉 **Key Improvements**

1. **No More Crashes**: India filter works even if APIs fail
2. **Better Coverage**: Currents API uses keywords for India
3. **Easy Debugging**: Clear ✅/❌ indicators
4. **Partial Results**: You get news even if some APIs fail

## 🌐 **Access Points**

Once running:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **India Endpoint**: http://localhost:8000/api/news/country/in

## 🔮 **Next Steps**

1. **Test the website**: Visit http://localhost:3000
2. **Try India filter**: Select India from dropdown
3. **Check console logs**: Look for ✅/❌ indicators
4. **Test other countries**: Try different country selections

---

**✅ The complete website is now ready with improved India filter!**
