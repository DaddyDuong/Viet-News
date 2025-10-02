#!/bin/bash

# Railway Deployment Checker
echo "🔍 Checking deployment readiness..."
echo "=================================="

echo "✅ Repository: DaddyDuong/Viet-News"
echo "✅ Branch: main"

echo -e "\n📋 Key files check:"
if [ -f "Procfile" ]; then
    echo "✅ Procfile exists"
    echo "   Content: $(cat Procfile)"
else
    echo "❌ Procfile missing"
fi

if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt exists"
    echo "   Dependencies: $(wc -l < requirements.txt) packages"
else
    echo "❌ requirements.txt missing"
fi

if [ -f "main.py" ]; then
    echo "✅ main.py exists (FastAPI app)"
else
    echo "❌ main.py missing"
fi

if [ -f "gunicorn.conf.py" ]; then
    echo "✅ gunicorn.conf.py exists"
else
    echo "❌ gunicorn.conf.py missing"
fi

echo -e "\n🚀 Ready for Railway deployment!"
echo "Next steps:"
echo "1. Go to railway.app"
echo "2. Login with GitHub"
echo "3. Deploy from DaddyDuong/Viet-News"
echo "4. Wait 2-3 minutes for deployment"
echo "5. Get your live URL!"