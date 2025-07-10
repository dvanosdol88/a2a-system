#!/bin/bash
# Production Deployment Setup Script

echo "🚀 A2A System Production Deployment Setup"
echo "========================================"

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo "❌ Error: .env.production file not found!"
    echo "Please create it from .env.example"
    exit 1
fi

# Generate secure secret key if needed
if grep -q "CHANGE_ME_TO_SECURE_RANDOM_VALUE" .env.production; then
    echo "🔐 Generating secure secret key..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i "s/CHANGE_ME_TO_SECURE_RANDOM_VALUE/$SECRET_KEY/g" .env.production
    echo "✅ Secret key generated and saved"
fi

# Initialize database
echo "🗄️ Initializing production database..."
python3 -c "from database.db_manager import db; db.init_database()"

# Create initial API key
echo "🔑 Creating initial API key..."
API_KEY=$(python3 -c "from database.db_manager import db; print(db.create_api_key('Production API Key'))")
echo "✅ API Key created: $API_KEY"
echo "⚠️  Save this key securely - it won't be shown again!"

# Run production checks
echo "🔍 Running production readiness checks..."
python3 scripts/production_readiness_check.py

echo ""
echo "📋 Next Steps:"
echo "1. Update .env.production with your database URL"
echo "2. Deploy using: render blueprint launch"
echo "3. Set environment variables in cloud platform"
echo "4. Configure domain and SSL"
echo "5. Test with the API key above"

echo ""
echo "🎯 Production deployment ready!"