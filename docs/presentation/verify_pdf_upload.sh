#!/usr/bin/env bash
# PDF Upload Verification Script for ASI-Core Presentation

set -e

echo "🔍 ASI-Core PDF Upload Verification"
echo "=================================="
echo ""

PDF_PATH="$(pwd)/docs/presentation/ASI-Core_Presentation.pdf"
EXPECTED_NAME="ASI-Core_Presentation.pdf"

# Check if file exists
if [ ! -f "$PDF_PATH" ]; then
    echo "❌ PDF file not found at: $PDF_PATH"
    echo ""
    echo "📋 Upload Instructions:"
    echo "1. Open VS Code file explorer (left sidebar)"
    echo "2. Navigate to docs/presentation/"
    echo "3. Drag your PDF file into the folder"
    echo "4. Ensure filename is exactly: $EXPECTED_NAME"
    exit 1
fi

# Check file size
FILE_SIZE=$(stat -c%s "$PDF_PATH" 2>/dev/null || echo "0")
if [ "$FILE_SIZE" -eq 0 ]; then
    echo "⚠️  PDF file exists but is empty (0 bytes)"
    echo ""
    echo "📋 Upload Instructions:"
    echo "1. Delete the empty file: docs/presentation/$EXPECTED_NAME"
    echo "2. Upload your actual PDF from local system"
    echo "3. Ensure filename is exactly: $EXPECTED_NAME"
    exit 1
fi

# Check if it's actually a PDF
FILE_TYPE=$(file "$PDF_PATH" 2>/dev/null || echo "unknown")
if [[ "$FILE_TYPE" == *"PDF"* ]]; then
    PDF_STATUS="✅ Valid PDF"
else
    PDF_STATUS="⚠️  File type: $FILE_TYPE"
fi

# Display results
echo "📊 Verification Results:"
echo "------------------------"
echo "📁 Path: $PDF_PATH"
echo "📏 Size: $(( FILE_SIZE / 1024 )) KB ($FILE_SIZE bytes)"
echo "📄 Type: $PDF_STATUS"
echo ""

if [ "$FILE_SIZE" -gt 0 ] && [[ "$FILE_TYPE" == *"PDF"* ]]; then
    echo "✅ PDF Upload Successful!"
    echo ""
    echo "🚀 Next Steps:"
    echo "1. Commit changes with: git add . && git commit -m 'Add presentation PDF'"
    echo "2. Push to GitHub: git push"
    echo "3. Deployment will be automatic via GitHub Actions"
    echo "4. Live URL: https://swisscomfort.github.io/asi-core/presentation/"
    echo ""
    
    # Offer to commit automatically
    read -p "📝 Commit PDF automatically? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd /workspaces/asi-core
        git add docs/presentation/ASI-Core_Presentation.pdf
        git commit -m "Add ASI-Core presentation PDF for GitHub Pages deployment"
        echo "✅ PDF committed to git"
        echo ""
        echo "🚀 Ready to push to GitHub!"
    fi
else
    echo "❌ PDF Upload Issues Detected"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "- Ensure file is a valid PDF"
    echo "- Check file is not corrupted"
    echo "- Verify upload completed successfully"
fi

echo ""
echo "📚 Full documentation: docs/presentation/UPLOAD_PDF_INSTRUCTIONS.md"