#!/usr/bin/env python3
"""
Deploy script for Hugging Face Spaces
Run this after setting up your Hugging Face Space
"""
import os
import subprocess
import sys
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command with description"""
    print(f"\n{description}")
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    else:
        print(f"Success: {result.stdout}")
        return True

def copy_project_files(source_dir, dest_dir):
    """Copy only necessary project files, excluding virtual environments and cache"""
    exclude_patterns = {
        '.venv', 'venv', '__pycache__', '.git', 'node_modules', 
        '.env', 'temp', 'output', '.pytest_cache', '.coverage'
    }
    
    source_path = Path(source_dir)
    dest_path = Path(dest_dir)
    
    print(f"Copying project files from {source_path} to {dest_path}")
    
    for item in source_path.iterdir():
        if item.name in exclude_patterns:
            print(f"Skipping: {item.name}")
            continue
            
        dest_item = dest_path / item.name
        
        try:
            if item.is_dir():
                if dest_item.exists():
                    shutil.rmtree(dest_item)
                shutil.copytree(item, dest_item, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
                print(f"Copied directory: {item.name}")
            else:
                if dest_item.exists():
                    dest_item.unlink()
                shutil.copy2(item, dest_item)
                print(f"Copied file: {item.name}")
        except Exception as e:
            print(f"Warning: Could not copy {item.name}: {e}")
            continue
    
    return True

def deploy_to_huggingface():
    """Deploy to Hugging Face Spaces"""
    print("🚀 Deploying Aquaverse Video Generator to Hugging Face Spaces")
    print("="*60)
    
    # Check if we're in a Hugging Face Space directory
    if os.path.exists('.git'):
        result = subprocess.run("git remote get-url origin", shell=True, capture_output=True, text=True)
        if result.returncode == 0 and 'huggingface.co/spaces' in result.stdout:
            print("✅ Already in a Hugging Face Space directory")
            # Add all files
            if not run_command("git add .", "Adding files to git"):
                return False
            
            # Commit changes
            if not run_command('git commit -m "Update Aquaverse Video Generator"', "Committing changes"):
                print("Note: No changes to commit (this is normal for subsequent deployments)")
            
            # Push to Hugging Face
            if not run_command("git push origin main", "Pushing to Hugging Face Spaces"):
                return False
            
            print("\n✅ Deployment complete!")
            return True
    
    print("\n⚠️  You need to set up the Hugging Face Space first:")
    print("1. Create a new Space at https://huggingface.co/new-space")
    print("2. Choose 'Gradio' as the SDK")
    print("3. Clone the Space to a different directory:")
    print("   git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME")
    print("4. Run this script from the cloned Space directory")
    
    # Check if user wants to proceed with automatic setup
    current_dir = os.getcwd()
    print(f"\nCurrent directory: {current_dir}")
    
    response = input("\nDo you want to copy files to an existing Space directory? (y/n): ")
    if response.lower() == 'y':
        space_dir = input("Enter the path to your Hugging Face Space directory: ")
        if not os.path.exists(space_dir):
            print(f"❌ Directory not found: {space_dir}")
            return False
        
        if copy_project_files(current_dir, space_dir):
            print(f"\n✅ Files copied to {space_dir}")
            print("Now run the following commands:")
            print(f"cd {space_dir}")
            print("git add .")
            print('git commit -m "Deploy Aquaverse Video Generator"')
            print("git push origin main")
            return True
    
    return False

if __name__ == "__main__":
    success = deploy_to_huggingface()
    sys.exit(0 if success else 1)