#!/usr/bin/env python3
"""
Fix deprecated Streamlit methods in the codebase
Replaces st.experimental_rerun() with st.rerun()
"""

import os
import re
from pathlib import Path

def fix_file(file_path):
    """Fix deprecated methods in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count occurrences
        old_count = content.count('st.experimental_rerun()')
        if old_count == 0:
            return 0
        
        # Replace deprecated method
        new_content = content.replace('st.experimental_rerun()', 'st.rerun()')
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Fixed {old_count} instances in {file_path}")
        return old_count
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return 0

def main():
    """Main function to fix all Python files"""
    project_root = Path(__file__).parent.parent
    total_fixed = 0
    
    print("🔧 Fixing deprecated Streamlit methods...")
    print("=" * 50)
    
    # Find all Python files
    python_files = list(project_root.rglob("*.py"))
    
    for file_path in python_files:
        if file_path.name != "fix_deprecated_streamlit.py":  # Skip this script
            fixed = fix_file(file_path)
            total_fixed += fixed
    
    print("=" * 50)
    print(f"🎉 Total instances fixed: {total_fixed}")
    
    if total_fixed > 0:
        print("\n📝 Summary of changes:")
        print("- Replaced st.experimental_rerun() with st.rerun()")
        print("- Updated all Python files in the project")
        print("\n💡 Note: st.rerun() is the modern replacement for st.experimental_rerun()")
        print("   It's available in Streamlit 1.27.0+ and is the recommended method.")

if __name__ == "__main__":
    main()
