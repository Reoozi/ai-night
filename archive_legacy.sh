#!/bin/bash
# Archive legacy documentation files

echo "🗂️  Archiving legacy documentation files..."
echo ""

# Create archive directory if it doesn't exist
if [ ! -d "archive" ]; then
    mkdir archive
    echo "✅ Created archive/ directory"
fi

# Move legacy files to archive
echo "📦 Moving legacy files..."

mv CHALLENGE_CHECKLIST.md archive/ 2>/dev/null && echo "   ✓ CHALLENGE_CHECKLIST.md"
mv CHALLENGE_MODIFICATIONS.md archive/ 2>/dev/null && echo "   ✓ CHALLENGE_MODIFICATIONS.md"
mv CHALLENGE_README.md archive/ 2>/dev/null && echo "   ✓ CHALLENGE_README.md"
mv CHALLENGE_STRUCTURE.md archive/ 2>/dev/null && echo "   ✓ CHALLENGE_STRUCTURE.md"
mv CHALLENGE_SUBMISSION.md archive/ 2>/dev/null && echo "   ✓ CHALLENGE_SUBMISSION.md"
mv CHALLENGE_TEST_GUIDE.md archive/ 2>/dev/null && echo "   ✓ CHALLENGE_TEST_GUIDE.md"
mv DELIVERABLE_FINAL.md archive/ 2>/dev/null && echo "   ✓ DELIVERABLE_FINAL.md"
mv FILE_INVENTORY.md archive/ 2>/dev/null && echo "   ✓ FILE_INVENTORY.md"
mv IMPLEMENTATION_SUMMARY.md archive/ 2>/dev/null && echo "   ✓ IMPLEMENTATION_SUMMARY.md"
mv INDEX.md archive/ 2>/dev/null && echo "   ✓ INDEX.md"
mv POSTGRES_SETUP.md archive/ 2>/dev/null && echo "   ✓ POSTGRES_SETUP.md"
mv QUICK_START.md archive/ 2>/dev/null && echo "   ✓ QUICK_START.md"
mv RAG_GUIDE.md archive/ 2>/dev/null && echo "   ✓ RAG_GUIDE.md"
mv RAG_IMPLEMENTATION.md archive/ 2>/dev/null && echo "   ✓ RAG_IMPLEMENTATION.md"
mv RAG_QUICK_REFERENCE.md archive/ 2>/dev/null && echo "   ✓ RAG_QUICK_REFERENCE.md"
mv README_EXECUTIF.md archive/ 2>/dev/null && echo "   ✓ README_EXECUTIF.md"
mv SOLUTION_COMPLETE.md archive/ 2>/dev/null && echo "   ✓ SOLUTION_COMPLETE.md"
mv STARTUP_GUIDE.md archive/ 2>/dev/null && echo "   ✓ STARTUP_GUIDE.md"

echo ""
echo "✅ Legacy files archived!"
echo ""
echo "📁 Current structure:"
echo "   Root: Essential files only"
echo "   archive/: Legacy documentation"
echo ""
echo "✨ Repository is now clean and organized!"
