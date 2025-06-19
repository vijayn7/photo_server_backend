#!/usr/bin/env python3
"""
Thumbnail implementation verification script
Checks that all components are properly installed and configured
"""

import sys
import importlib.util

def check_dependencies():
    """Check that all required dependencies are available"""
    print("🔍 Checking Dependencies...")
    
    dependencies = [
        ("fastapi", "FastAPI web framework"),
        ("PIL", "Pillow image processing library"),
        ("os", "Operating system interface (built-in)"),
        ("json", "JSON handling (built-in)")
    ]
    
    all_good = True
    for module, description in dependencies:
        try:
            if module == "PIL":
                import PIL
                from PIL import Image, ImageOps
                print(f"  ✅ {module} - {description} (version: {PIL.__version__})")
            else:
                importlib.import_module(module)
                print(f"  ✅ {module} - {description}")
        except ImportError:
            print(f"  ❌ {module} - {description} (MISSING)")
            all_good = False
    
    return all_good

def check_photo_utils():
    """Check that photo_utils has the new thumbnail functions"""
    print("\n🔍 Checking Photo Utils Functions...")
    
    try:
        from python import photo_utils
        
        functions = [
            ("is_image", "Image file detection"),
            ("ensure_thumbnails_dir", "Thumbnail directory creation"),
            ("generate_thumbnail", "Thumbnail generation"),
            ("get_thumbnail_path", "Thumbnail path resolution")
        ]
        
        all_good = True
        for func_name, description in functions:
            if hasattr(photo_utils, func_name):
                print(f"  ✅ {func_name} - {description}")
            else:
                print(f"  ❌ {func_name} - {description} (MISSING)")
                all_good = False
        
        # Test image detection
        if hasattr(photo_utils, 'is_image'):
            test_result = photo_utils.is_image("test.jpg")
            print(f"  ✅ is_image test: {test_result}")
        
        return all_good
        
    except ImportError as e:
        print(f"  ❌ Cannot import photo_utils: {e}")
        return False

def check_main_py():
    """Check that main.py has the thumbnail endpoint"""
    print("\n🔍 Checking Main Application...")
    
    try:
        # Read main.py to check for thumbnail endpoint
        with open("main.py", "r") as f:
            content = f.read()
        
        checks = [
            ("FileResponse", "FileResponse import for serving files"),
            ("/thumbnails/{filename}", "Thumbnail endpoint definition"),
            ("get_thumbnail", "Thumbnail handler function"),
            ("get_thumbnail_path", "Thumbnail path function usage")
        ]
        
        all_good = True
        for check, description in checks:
            if check in content:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description} (MISSING)")
                all_good = False
        
        return all_good
        
    except FileNotFoundError:
        print("  ❌ main.py not found")
        return False
    except Exception as e:
        print(f"  ❌ Error reading main.py: {e}")
        return False

def check_requirements():
    """Check that requirements.txt includes pillow"""
    print("\n🔍 Checking Requirements...")
    
    try:
        with open("requirements.txt", "r") as f:
            content = f.read().lower()
        
        if "pillow" in content:
            print("  ✅ Pillow listed in requirements.txt")
            return True
        else:
            print("  ❌ Pillow not found in requirements.txt")
            return False
            
    except FileNotFoundError:
        print("  ❌ requirements.txt not found")
        return False

def main():
    print("🖼️  Thumbnail Implementation Verification")
    print("=" * 50)
    
    checks = [
        check_dependencies,
        check_photo_utils,
        check_main_py,
        check_requirements
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("✨ Thumbnail feature is ready for use!")
        print("\nNext steps:")
        print("1. Start the server: ./start_server.sh")
        print("2. Upload an image through the web interface")
        print("3. Test thumbnail access: GET /thumbnails/{filename}")
    else:
        print("❌ SOME CHECKS FAILED")
        print("Please review the errors above and fix any missing components.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
