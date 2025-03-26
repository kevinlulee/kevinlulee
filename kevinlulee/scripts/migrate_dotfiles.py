#!/usr/bin/env python3
import os
import shutil
import argparse
from pathlib import Path

def handle_existing_target(src: Path, dst: Path):
    """Resolve conflicts when destination already exists"""
    if not dst.exists():
        return True  # No conflict
    
    # Case 1: Destination is identical to source (already migrated)
    if src.is_symlink() and os.path.samefile(src, dst):
        print(f"🔗 Already properly symlinked: {src} -> {dst}")
        return False
    
    # Case 2: Destination is different file
    print(f"⚠️  Conflict: {dst} already exists")
    action = input(f"Overwrite (o), Backup (b), or Skip (s)? [o/b/s]: ").lower()
    
    if action == 'o':
        if dst.is_dir():
            shutil.rmtree(dst)
        else:
            dst.unlink()
        return True
    elif action == 'b':
        backup = dst.with_name(dst.name + ".bak")
        print(f"📦 Backing up to {backup}")
        shutil.move(str(dst), str(backup))
        return True
    else:
        print("⏩ Skipping")
        return False

def migrate_to_dotfiles(dotfiles_dir):
    dotfiles_dir = Path(dotfiles_dir).expanduser()
    dotfiles_dir.mkdir(parents=True, exist_ok=True)
    
    PERSONAL_CONFIGS = [
        # Shell
        ".bash_aliases", ".bash_commands", ".bash_profile",
        ".bashrc", ".fzf.bash", ".profile",
        
        # Dev Tools
        ".clasprc.json", ".gitconfig", ".ignore",
        ".kdogignore", ".prettierrc", ".pyrightconfig.json",
        ".vimrc",
        
        # Security/Networking
        # ".netrc",
        
        # Directories
        # ".fzf", ".kdog3682", ".snippets", ".vscode",
    ]

    for config in PERSONAL_CONFIGS:
        src = Path.home() / config
        dst = dotfiles_dir / config
        
        if not src.exists():
            print(f"⚠️  Source doesn't exist: {src}")
            continue

        try:
            # Case 1: Already a correct symlink
            if src.is_symlink() and os.path.exists(src) and os.path.samefile(src, dst):
                print(f"🔗 Already correctly symlinked: {src} -> {dst}")
                continue
                
            # Case 2: Regular file/dir that needs migration
            if handle_existing_target(src, dst):
                shutil.move(str(src), str(dst))
                src.symlink_to(dst, target_is_directory=src.is_dir())
                print(f"✅ Migrated: {src} -> {dst}")
                
        except Exception as e:
            print(f"❌ Failed to process {src}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(
        description='Safely migrate dotfiles with conflict resolution',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dotfiles-dir', 
                       default='~/dotfiles/personal',
                       help='Target directory for config files')
    args = parser.parse_args()

    print(f"🚀 Starting migration to: {args.dotfiles_dir}")
    migrate_to_dotfiles(args.dotfiles_dir)
    print("\n🎉 Migration complete! Verify with:")
    print(f"ls -la ~ | grep '^l'  # Check symlinks")

if __name__ == "__main__":
    main()
