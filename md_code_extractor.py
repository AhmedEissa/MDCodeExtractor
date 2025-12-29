#!/usr/bin/env python3
"""
Markdown Code Extractor Tool (FINAL UNIVERSAL VERSION)
Extracts source code from Markdown code blocks and builds the folder structure.

Supports three formats:
1. Format A: ## FILE N: path/to/file.ext
2. Format B: ### path/to/file.ext
3. Format C: ### FILE N: path/to/file.ext

Usage:
    python3 md_code_extractor_FINAL.py <markdown_file> [output_directory]

The tool automatically detects and handles all three formats.
"""

import re
import os
import sys
from pathlib import Path


def extract_code_blocks(markdown_content):
    """
    Extract code blocks with their file paths from Markdown content.
    Supports multiple formats:
    - Format A: ## FILE N: path/to/file.ext
    - Format B: ### path/to/file.ext
    - Format C: ### FILE N: path/to/file.ext
    
    Returns a list of tuples: (file_path, code_content)
    """
    code_blocks = []
    
    # Pattern 1: ## FILE N: path/to/file.ext (Format A)
    # This handles: ## FILE 1: backend/src/agents/AgentRegistry.ts
    pattern_a = r'##\s+FILE\s+\d+:\s*([^\n]+)\n+```[^\n]*\n(.*?)```'
    matches_a = re.findall(pattern_a, markdown_content, re.DOTALL)
    
    for file_path, code_content in matches_a:
        file_path = file_path.strip()
        code_content = code_content.rstrip()
        code_blocks.append((file_path, code_content))
    
    # Pattern 2: ### FILE N: path/to/file.ext (Format C - NEW)
    # This handles: ### FILE 1: backend/src/config/env.config.ts
    pattern_c = r'###\s+FILE\s+\d+:\s*([^\n]+)\n+```[^\n]*\n(.*?)```'
    matches_c = re.findall(pattern_c, markdown_content, re.DOTALL)
    
    for file_path, code_content in matches_c:
        file_path = file_path.strip()
        code_content = code_content.rstrip()
        code_blocks.append((file_path, code_content))
    
    # Pattern 3: ### path/to/file.ext (Format B)
    # This handles: ### backend/src/index.ts
    # More restrictive to avoid matching headings
    pattern_b = r'###\s+([^\n]+?)\n+```[^\n]*\n(.*?)```'
    matches_b = re.findall(pattern_b, markdown_content, re.DOTALL)
    
    for file_path, code_content in matches_b:
        file_path = file_path.strip()
        # Skip if it's a FILE N: format (already handled by pattern_c)
        # Skip if it looks like a heading (contains special characters or is too short)
        if (file_path and 
            not file_path.startswith('*') and 
            not file_path.startswith('FILE') and
            '.' in file_path):
            code_content = code_content.rstrip()
            code_blocks.append((file_path, code_content))
    
    return code_blocks


def create_files(code_blocks, output_dir):
    """
    Create folder structure and write code files.
    
    Args:
        code_blocks: List of tuples (file_path, code_content)
        output_dir: Base directory where files will be created
    """
    created_files = []
    failed_files = []
    
    for file_path, code_content in code_blocks:
        try:
            # Construct full path
            full_path = os.path.join(output_dir, file_path)
            
            # Create parent directories if they don't exist
            parent_dir = os.path.dirname(full_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            
            # Write the file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(code_content)
            
            created_files.append(full_path)
            print(f"✅ Created: {file_path}")
            
        except Exception as e:
            failed_files.append((file_path, str(e)))
            print(f"❌ Failed: {file_path} - {str(e)}")
    
    return created_files, failed_files


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 md_code_extractor_FINAL.py <markdown_file> [output_directory]")
        print("\nExample:")
        print("  python3 md_code_extractor_FINAL.py source.md ./output")
        print("  python3 md_code_extractor_FINAL.py source.md  # Uses current directory")
        print("\nSupported formats:")
        print("  - Format A: ## FILE N: path/to/file.ext")
        print("  - Format B: ### path/to/file.ext")
        print("  - Format C: ### FILE N: path/to/file.ext")
        sys.exit(1)
    
    markdown_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    # Validate markdown file exists
    if not os.path.isfile(markdown_file):
        print(f"❌ Error: Markdown file '{markdown_file}' not found")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n📖 Reading Markdown file: {markdown_file}")
    print(f"📁 Output directory: {os.path.abspath(output_dir)}\n")
    
    # Read markdown file
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        sys.exit(1)
    
    # Extract code blocks
    print("🔍 Extracting code blocks...\n")
    code_blocks = extract_code_blocks(markdown_content)
    
    if not code_blocks:
        print("⚠️  No code blocks found in the Markdown file.")
        print("   Make sure your code blocks follow one of these formats:")
        print("   Format A: ## FILE N: path/to/file.ext")
        print("   Format B: ### path/to/file.ext")
        print("   Format C: ### FILE N: path/to/file.ext")
        print("   Followed by:")
        print("   ```language")
        print("   code content")
        print("   ```")
        sys.exit(0)
    
    print(f"Found {len(code_blocks)} code block(s)\n")
    
    # Create files
    print("📝 Creating files and folders...\n")
    created_files, failed_files = create_files(code_blocks, output_dir)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successfully created: {len(created_files)} file(s)")
    print(f"❌ Failed: {len(failed_files)} file(s)")
    
    if failed_files:
        print(f"\nFailed files:")
        for file_path, error in failed_files:
            print(f"  - {file_path}: {error}")
    
    print(f"\n📁 Output directory: {os.path.abspath(output_dir)}")
    print(f"{'='*60}\n")
    
    return 0 if not failed_files else 1


if __name__ == "__main__":
    sys.exit(main())
