#!/usr/bin/env python3
"""
Simple script to switch between testing and production modes
"""

import os
import sys

def switch_mode(mode):
    """Switch between testing and production modes"""
    if mode not in ['test', 'production']:
        print("Usage: python switch_mode.py [test|production]")
        sys.exit(1)
    
    # Read current config
    with open('config.py', 'r') as f:
        config_content = f.read()
    
    if mode == 'test':
        # Switch to testing mode (no ElevenLabs)
        new_config = config_content.replace(
            'USE_ELEVENLABS = True',
            'USE_ELEVENLABS = False'
        )
        new_config = new_config.replace(
            'USE_ELEVENLABS = False',
            'USE_ELEVENLABS = False'
        )
        print("✅ Switched to TESTING mode (macOS speech synthesis, no credits used)")
    else:
        # Switch to production mode (ElevenLabs)
        new_config = config_content.replace(
            'USE_ELEVENLABS = False',
            'USE_ELEVENLABS = True'
        )
        new_config = new_config.replace(
            'USE_ELEVENLABS = True',
            'USE_ELEVENLABS = True'
        )
        print("✅ Switched to PRODUCTION mode (ElevenLabs Jessica voice)")
    
    # Write updated config
    with open('config.py', 'w') as f:
        f.write(new_config)
    
    print(f"Configuration updated. Run 'python main.py' to start the assistant.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python switch_mode.py [test|production]")
        print("\nModes:")
        print("  test       - Use macOS speech synthesis (no credits)")
        print("  production - Use ElevenLabs Jessica voice (uses credits)")
        sys.exit(1)
    
    switch_mode(sys.argv[1]) 