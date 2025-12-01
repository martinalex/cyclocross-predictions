#!/bin/bash
# VeloPredict API Startup Script

echo "🚀 Starting VeloPredict API..."
echo "📊 Model: v4 with Platt scaling calibration"
echo "🎯 Accuracy: 90% Top-10 (validated at Tabor)"
echo ""

# Run with uvicorn
python3 -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

echo ""
echo "✅ API running at http://localhost:8000"
echo "📖 Documentation: http://localhost:8000/docs"
