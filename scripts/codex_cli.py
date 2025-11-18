#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI Codex CLI Tool

사용법:
  codex "Python code to calculate fibonacci"
  codex "SQL query to find top 10 users"
  codex "JavaScript function to validate email"

환경 변수:
  OPENAI_API_KEY - OpenAI API 키 (필수)
"""

import sys
import os
from openai import OpenAI


def get_api_key():
    """Get API key from environment variable"""
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("[ERROR] OPENAI_API_KEY environment variable is not set.")
        print("\nSetup Instructions:")
        print("1. Create OpenAI account: https://platform.openai.com/")
        print("2. Generate API key: https://platform.openai.com/api-keys")
        print("3. Set environment variable:")
        print("   Windows PowerShell:")
        print("     $env:OPENAI_API_KEY = 'your-api-key-here'")
        print("   Windows CMD:")
        print("     set OPENAI_API_KEY=your-api-key-here")
        print("   WSL/Git Bash:")
        print("     export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    return api_key


def generate_code(prompt):
    """Generate code using OpenAI Codex"""
    api_key = get_api_key()
    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant. Provide clean, well-commented code."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        code = response.choices[0].message.content
        return code

    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: codex \"your code request\"")
        print("\nExamples:")
        print('  codex "Python function to read CSV file"')
        print('  codex "SQL query to join two tables"')
        print('  codex "JavaScript async function example"')
        sys.exit(1)

    # Combine all arguments into a single prompt
    prompt = " ".join(sys.argv[1:])

    print("[Codex] Generating code...\n")
    code = generate_code(prompt)

    print("=" * 60)
    print(code)
    print("=" * 60)


if __name__ == '__main__':
    main()
