#!/usr/bin/env python3
"""
Launcher script for database population
Provides a menu to choose which population script to run
"""

import os
import sys
import subprocess

def show_menu():
    """Display the main menu"""
    print("🎨 Art Database Population Launcher")
    print("=" * 40)
    print("1. 🧪 Test System (Recommended first)")
    print("2. 🚀 Quick Population (100 artworks)")
    print("3. 📊 Comprehensive Population (1000+ artworks)")
    print("4. 🔧 Custom Population")
    print("5. 📖 View Documentation")
    print("6. ❌ Exit")
    print()

def run_script(script_name, *args):
    """Run a Python script with arguments"""
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        return False
    
    try:
        # Build command
        cmd = [sys.executable, script_path] + list(args)
        
        # Run the script
        result = subprocess.run(cmd, cwd=os.path.dirname(os.path.dirname(__file__)))
        
        if result.returncode == 0:
            print(f"\n✅ {script_name} completed successfully")
        else:
            print(f"\n❌ {script_name} failed with exit code {result.returncode}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def custom_population():
    """Handle custom population parameters"""
    print("\n🔧 Custom Population")
    print("-" * 20)
    
    try:
        target = input("Enter target artwork count (default: 500): ").strip()
        target_count = int(target) if target else 500
        
        max_per_source = input("Enter max artworks per source (default: 100): ").strip()
        max_per_source = int(max_per_source) if max_per_source else 100
        
        print(f"\n🎯 Target: {target_count} total artworks")
        print(f"📊 Max per source: {max_per_source}")
        
        confirm = input("\nProceed? (y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            return run_script("populate_db_comprehensive.py", str(target_count), str(max_per_source))
        else:
            print("❌ Cancelled")
            return False
            
    except ValueError:
        print("❌ Invalid number entered")
        return False

def show_documentation():
    """Show documentation"""
    doc_path = os.path.join(os.path.dirname(__file__), "README_DATABASE_POPULATION.md")
    
    if os.path.exists(doc_path):
        print("\n📖 Documentation:")
        print("-" * 20)
        try:
            with open(doc_path, 'r') as f:
                content = f.read()
                # Show first 50 lines
                lines = content.split('\n')[:50]
                print('\n'.join(lines))
                if len(content.split('\n')) > 50:
                    print("\n... (truncated - see README_DATABASE_POPULATION.md for full docs)")
        except Exception as e:
            print(f"❌ Error reading documentation: {e}")
    else:
        print("❌ Documentation file not found")

def main():
    """Main launcher function"""
    while True:
        show_menu()
        
        try:
            choice = input("Select an option (1-6): ").strip()
            
            if choice == "1":
                print("\n🧪 Running system test...")
                run_script("test_population.py")
                
            elif choice == "2":
                print("\n🚀 Running quick population...")
                run_script("quick_populate.py")
                
            elif choice == "3":
                print("\n📊 Running comprehensive population...")
                run_script("populate_db_comprehensive.py")
                
            elif choice == "4":
                custom_population()
                
            elif choice == "5":
                show_documentation()
                
            elif choice == "6":
                print("\n👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid option. Please select 1-6.")
            
            if choice in ["1", "2", "3", "4"]:
                input("\nPress Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
