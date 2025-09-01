#!/usr/bin/env python3
"""
Fix deprecated Streamlit use_container_width parameters
Replace with new width parameter
"""

import os
import re

def fix_file(file_path):
    """Fix deprecated use_container_width parameters in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace use_container_width=True with width='stretch'
        content = re.sub(
            r'use_container_width=True',
            "width='stretch'",
            content
        )
        
        # Replace use_container_width=False with width='content'
        content = re.sub(
            r'use_container_width=False',
            "width='content'",
            content
        )
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Fixed {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Main function to fix all Python files"""
    files_to_fix = [
        'seas-financial-tracker.py',
        'app_refactored_with_service.py',
        'app_with_database.py'
    ]
    
    fixed_count = 0
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if fix_file(file_path):
                fixed_count += 1
    
    print(f"\n🎉 Fixed {fixed_count} files successfully!")
    print("All deprecated use_container_width parameters have been updated to use the new width parameter.")

if __name__ == "__main__":
    main()
