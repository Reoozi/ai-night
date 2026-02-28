"""Trim README to remove duplicate content"""
with open('README.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with "Built with ❤️ for AI Night Challenge"
end_line = 0
for i, line in enumerate(lines):
    if 'Built with' in line and 'AI Night Challenge' in line:
        end_line = i + 1
        break

if end_line > 0:
    with open('README.md', 'w', encoding='utf-8') as f:
        f.writelines(lines[:end_line])
    print(f"✓ Trimmed README to {end_line} lines")
else:
    print("❌ Could not find end marker")
