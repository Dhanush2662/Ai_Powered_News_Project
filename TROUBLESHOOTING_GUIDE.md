# 🔧 Troubleshooting Guide: "Error Fetching Country News"

## 🎯 **Problem**
You're getting "error fetching country news" when filtering to India or USA in the frontend.

## 🔍 **Root Cause Analysis**

The issue is likely one of these:

1. **Backend not running** - The frontend can't connect to the backend
2. **Missing API function** - The `fetchFromAPI` function was missing (now fixed)
3. **CORS issues** - Browser blocking cross-origin requests
4. **Network/port issues** - Ports blocked or services not accessible

## 🚀 **Step-by-Step Fix**

### Step 1: Test Backend First
```bash
# Run the backend test
python test_backend_api.py

# Or run the debug tool
python debug_frontend_backend.py
```

**Expected Output:**
```
✅ Health endpoint working
✅ Root endpoint working  
✅ India endpoint working
   Articles: 45
   API Sources: ['newsapi', 'gnews', 'mediastack', 'currents']
```

### Step 2: Start Backend Properly
```bash
# Method 1: Using our script
python start_website.py

# Method 2: Manual start
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Check for these messages:**
```
✅ NewsAPI in: 15 articles
✅ GNews in: 12 articles
✅ Mediastack in: 8 articles
✅ Currents in: 10 articles
🔄 Final results: 45 unique articles
```

### Step 3: Test Backend API Directly
```bash
# Test India endpoint
curl http://localhost:8000/api/news/country/in

# Test USA endpoint  
curl http://localhost:8000/api/news/country/us
```

### Step 4: Start Frontend
```bash
# In a new terminal
cd frontend
npm start
```

### Step 5: Check Browser Console
1. Open http://localhost:3000
2. Open browser DevTools (F12)
3. Go to Console tab
4. Select India from dropdown
5. Look for error messages

## 🔧 **Common Issues & Solutions**

### Issue 1: "Backend not running"
**Symptoms:** Connection refused, timeout errors
**Solution:**
```bash
cd backend
python -m uvicorn main:app --reload
```

### Issue 2: "CORS errors in browser console"
**Symptoms:** CORS policy errors in browser console
**Solution:** Backend CORS is already configured, restart both services

### Issue 3: "Port already in use"
**Symptoms:** Port 8000 or 3000 already in use
**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Issue 4: "Module not found errors"
**Symptoms:** Import errors in backend
**Solution:**
```bash
cd backend
python -m pip install -r requirements.txt
```

### Issue 5: "Frontend build errors"
**Symptoms:** npm start fails
**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

## 🧪 **Testing the Fix**

### Test 1: Backend API
```bash
python test_backend_api.py
```

### Test 2: Frontend-Backend Communication
```bash
python debug_frontend_backend.py
```

### Test 3: Manual Browser Test
1. Start backend: `cd backend && python -m uvicorn main:app --reload`
2. Start frontend: `cd frontend && npm start`
3. Open http://localhost:3000
4. Select "🇮🇳 India" from dropdown
5. Check for articles loading

## 📊 **Expected Results**

### ✅ **Success Case**
- Backend shows ✅/❌ indicators in console
- Frontend loads articles without errors
- Browser console shows no CORS errors
- Articles appear in the UI

### ❌ **Failure Cases**
- **Backend not starting**: Check Python/uvicorn installation
- **Frontend not starting**: Check Node.js/npm installation
- **CORS errors**: Restart both services
- **No articles**: Check API keys in backend/.env

## 🔍 **Debugging Tools**

### 1. **Backend Logs**
Look for these in backend console:
```
✅ NewsAPI in: 15 articles
✅ GNews in: 12 articles
❌ Mediastack failed for in: API key invalid
✅ Currents in: 10 articles
🔄 Final results: 37 unique articles
```

### 2. **Browser Console**
Check for:
- Network errors (404, 500, etc.)
- CORS errors
- JavaScript errors

### 3. **Network Tab**
In browser DevTools:
- Check if requests to `/api/news/country/in` are being made
- Check response status codes
- Check response data

## 🎯 **Quick Fix Checklist**

- [ ] Backend is running on port 8000
- [ ] Frontend is running on port 3000
- [ ] Backend shows ✅/❌ indicators
- [ ] No CORS errors in browser console
- [ ] Network requests to backend are successful
- [ ] Articles are loading in the UI

## 🚀 **One-Click Solution**

If you're still having issues, try the complete setup:

```bash
# Windows
start_website_windows.bat

# Or Python script
python start_website.py
```

This will:
1. ✅ Install all dependencies
2. ✅ Start backend with proper error handling
3. ✅ Start frontend with correct API calls
4. ✅ Open browser automatically

---

**✅ The improved error handling should now work correctly!**
