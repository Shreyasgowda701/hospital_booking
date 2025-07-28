#!/bin/bash

echo "🏥 Hospital Management System - Setup Script"
echo "============================================"

# Check Python version
echo "📋 Checking Python installation..."
python_version=$(python3 --version 2>&1)
if [[ $? -eq 0 ]]; then
    echo "✅ $python_version found"
else
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [[ $? -eq 0 ]]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Run migrations
echo "🗃️ Setting up database..."
python3 manage.py migrate

if [[ $? -eq 0 ]]; then
    echo "✅ Database setup complete"
else
    echo "❌ Database setup failed"
    exit 1
fi

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "🚀 To start the server, run:"
echo "   python3 manage.py runserver"
echo ""
echo "🌐 Then open your browser to:"
echo "   http://127.0.0.1:8000"
echo ""
echo "👥 Default login credentials:"
echo "   Admin:   admin / admin123"
echo "   Doctor:  doctor1 / doctor123" 
echo "   Patient: patient1 / patient123"
echo ""
echo "📚 Check README.md for detailed instructions"
