#!/bin/bash

# Deploy script for AI Trade Report to GitHub Pages

echo "🚀 Deploying AI Trade Report to GitHub Pages..."

# Create public directory
mkdir -p public

# Copy static files
cp -r static public/
cp -r templates public/

# Copy main files
cp app.py public/
cp generate_prompt.py public/
cp requirements.txt public/
cp README.md public/
cp .env_example public/

# Copy the GitHub Pages index.html
cp index.html public/

echo "✅ Files copied to public directory"
echo "📁 Public directory contents:"
ls -la public/

echo "🎉 Ready for GitHub Pages deployment!"
echo "💡 To deploy:"
echo "   1. Commit and push these changes"
echo "   2. Go to repository Settings > Pages"
echo "   3. Select 'Deploy from a branch'"
echo "   4. Choose 'main' branch and '/public' folder"
echo "   5. Save and wait for deployment"
