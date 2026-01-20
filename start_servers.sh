#!/bin/bash

echo "Starting Intelligent Recipe Generator..."
echo ""

echo "Starting Flask server (serves both frontend and backend)..."
cd backend/app
python main.py

echo ""
echo "Server is starting up..."
echo "Application will be available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
