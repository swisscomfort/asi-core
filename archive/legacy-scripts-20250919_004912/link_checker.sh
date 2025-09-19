#!/bin/bash

# ASI-Core Link Checker Script
# Tests all external links found in Markdown files

echo "🔍 ASI-Core Link Checker"
echo "========================"

# Array of links to test
links=(
    "https://github.com/swisscomfort/asi-core"
    "https://insights.github.com/swisscomfort/asi-core"
    "https://github.com/swisscomfort/asi-core/pkgs/container/asi-core"
    "https://github.com/swisscomfort"
    "https://github.com/swisscomfort/asi-core/actions"
    "https://github.com/swisscomfort/asi-core/security"
    "https://github.com/swisscomfort/asi-core/issues?q=label%3Abeta-testing"
    "https://www.gnu.org/licenses/agpl-3.0"
    "https://github.com/swisscomfort/asi-core/issues/new?template=beta-feedback.yml"
    "https://github.com/swisscomfort/asi-core/issues/new?template=bug-report.yml"
    "https://github.com/swisscomfort/asi-core/issues/new?template=feature-request.yml"
    "https://github.com/swisscomfort/asi-core.git"
    "https://github.com/swisscomfort/asi-core"
    "https://github.com/thomasm1/app-kafka-elasticsearch-tweets/blob/2c573149a96760793df4c3d084e633f5bf26803d/react-docker/README.md"
    "https://github.com/ppconrado/esports/blob/e87cc608f50724a19fbee4aa4f345bcd0c81fee2/README.md"
)

working=0
broken=0
total=${#links[@]}

echo "Testing $total links..."
echo ""

for link in "${links[@]}"; do
    echo -n "Testing: $link ... "
    
    # Use curl to check status
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$link")
    
    if [ "$status" -eq 200 ]; then
        echo "✅ OK ($status)"
        ((working++))
    elif [ "$status" -eq 301 ] || [ "$status" -eq 302 ]; then
        # Check redirect location
        redirect=$(curl -s -o /dev/null -w "%{redirect_url}" --max-time 10 "$link")
        echo "🔄 REDIRECT ($status) -> $redirect"
        ((working++))
    else
        echo "❌ BROKEN ($status)"
        ((broken++))
    fi
done

echo ""
echo "📊 Summary:"
echo "Total links: $total"
echo "Working: $working"
echo "Broken: $broken"

if [ $broken -gt 0 ]; then
    echo ""
    echo "⚠️  Found $broken broken links that need repair!"
else
    echo ""
    echo "🎉 All links are working!"
fi