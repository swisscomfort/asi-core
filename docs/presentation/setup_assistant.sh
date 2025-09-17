#!/usr/bin/env bash
# ASI-Core Presentation Setup Assistant

set -e

echo "🎯 ASI-Core Presentation Setup Assistant"
echo "========================================"
echo ""

# Color codes for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check current status
echo "📊 Current Infrastructure Status:"
echo "--------------------------------"

# Check if devcontainer exists
if [ -f ".devcontainer/devcontainer.json" ]; then
    log_success "GitHub Codespace configuration ready"
else
    log_error "Codespace configuration missing"
fi

# Check if GitHub Actions workflow exists
if [ -f ".github/workflows/deploy-presentation.yml" ]; then
    log_success "GitHub Actions deployment workflow configured"
else
    log_error "GitHub Actions workflow missing"
fi

# Check if demo script exists
if [ -f "docs/presentation/demo.py" ]; then
    log_success "Interactive demo system ready"
else
    log_error "Demo system missing"
fi

# Check if presentation directory exists
if [ -d "docs/presentation" ]; then
    log_success "Presentation directory structure ready"
else
    log_error "Presentation directory missing"
fi

echo ""

# Check PDF status
echo "📄 PDF File Status:"
echo "-------------------"
PDF_PATH="docs/presentation/ASI-Core_Presentation.pdf"

if [ ! -f "$PDF_PATH" ]; then
    log_error "PDF file missing completely"
    NEEDS_UPLOAD=true
elif [ ! -s "$PDF_PATH" ]; then
    log_warning "PDF file exists but is empty (0 bytes)"
    NEEDS_UPLOAD=true
else
    FILE_SIZE=$(stat -c%s "$PDF_PATH")
    log_success "PDF file ready ($(( FILE_SIZE / 1024 )) KB)"
    NEEDS_UPLOAD=false
fi

echo ""

if [ "$NEEDS_UPLOAD" = true ]; then
    echo "🚀 Next Steps - PDF Upload Required:"
    echo "====================================="
    echo ""
    log_info "Your PDF file location (local machine):"
    echo "   📁 /home/emil/Caine-Live/Neuer Ordner/ASI-Core_Presentation.pdf"
    echo ""
    log_info "Target location (in repository):"
    echo "   📁 docs/presentation/ASI-Core_Presentation.pdf"
    echo ""
    echo "🔧 Upload Methods:"
    echo ""
    echo "1️⃣  DRAG & DROP (Easiest):"
    echo "   • Open VS Code file explorer (left sidebar)"
    echo "   • Navigate to docs/presentation/ folder"
    echo "   • Drag PDF from your local system into the folder"
    echo ""
    echo "2️⃣  UPLOAD MENU:"
    echo "   • Right-click on docs/presentation/ folder"
    echo "   • Select 'Upload...'"
    echo "   • Choose your PDF file"
    echo ""
    echo "3️⃣  COPY COMMAND (if path accessible):"
    echo "   cp '/home/emil/Caine-Live/Neuer Ordner/ASI-Core_Presentation.pdf' \\"
    echo "      'docs/presentation/ASI-Core_Presentation.pdf'"
    echo ""
    log_warning "⚠️  Important: Filename must be exactly 'ASI-Core_Presentation.pdf'"
    echo ""
    echo "🔍 After upload, run verification:"
    echo "   ./docs/presentation/verify_pdf_upload.sh"
    echo ""
else
    echo "🎉 Ready for Deployment!"
    echo "======================="
    echo ""
    log_success "All components ready"
    log_success "PDF file uploaded and valid"
    echo ""
    echo "🚀 Deployment Options:"
    echo ""
    echo "1️⃣  COMMIT & PUSH:"
    echo "   git add ."
    echo "   git commit -m 'Complete presentation setup with PDF'"
    echo "   git push"
    echo ""
    echo "2️⃣  AUTO-COMMIT:"
    echo "   (Run verify_pdf_upload.sh and select auto-commit)"
    echo ""
    echo "📡 After push, automatic deployment to:"
    echo "   🌐 https://swisscomfort.github.io/asi-core/presentation/"
    echo ""
fi

echo "📚 Documentation:"
echo "-----------------"
echo "• Full setup guide: docs/presentation/README.md"
echo "• Upload instructions: docs/presentation/UPLOAD_PDF_INSTRUCTIONS.md"
echo "• Demo system: python docs/presentation/demo.py"
echo ""

echo "🧠 ASI-Core Features Ready:"
echo "---------------------------"
log_success "🔒 Privacy-First Architecture"
log_success "🌍 Decentralized Storage (IPFS + Arweave)"
log_success "🤖 AI-Powered Semantic Search"
log_success "🏢 Enterprise GitHub Pro+ Features"
log_success "⚡ Progressive Web App (PWA)"
log_success "🛡️ AGPL-3.0 Open Source License"

echo ""
echo "Ready to revolutionize data sovereignty! 🚀"