#!/usr/bin/env python3
"""
Demonstration script showing thumbnail generation workflow
"""

import os
import tempfile
from PIL import Image, ImageDraw, ImageFont

def create_sample_image(width=800, height=600, text="Sample Image"):
    """Create a sample image for testing"""
    # Create a new image with a gradient background
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    # Create a simple gradient
    for y in range(height):
        color_value = int(255 * (y / height))
        draw.line([(0, y), (width, y)], fill=(color_value, 100, 255 - color_value))
    
    # Add some text
    try:
        # Try to use a default font
        font = ImageFont.load_default()
        draw.text((width//2 - 50, height//2), text, fill=(255, 255, 255), font=font)
    except:
        # Fallback if font loading fails
        draw.text((width//2 - 50, height//2), text, fill=(255, 255, 255))
    
    return img

def simulate_thumbnail_generation():
    """Simulate the thumbnail generation process"""
    print("🖼️  Thumbnail Generation Simulation")
    print("=" * 50)
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Working in temporary directory: {temp_dir}")
        
        # Create sample images
        sample_images = [
            ("landscape.jpg", 1200, 800),
            ("portrait.jpg", 600, 900), 
            ("square.jpg", 500, 500)
        ]
        
        for filename, width, height in sample_images:
            print(f"\n📷 Creating sample image: {filename} ({width}x{height})")
            
            # Create the sample image
            img = create_sample_image(width, height, f"{width}x{height}")
            image_path = os.path.join(temp_dir, filename)
            img.save(image_path, 'JPEG', quality=90)
            
            # Simulate thumbnail generation
            print(f"   Original size: {img.size}")
            
            # Create thumbnail (same logic as in photo_utils.py)
            thumbnail_size = 256
            thumb_img = img.copy()
            thumb_img.thumbnail((thumbnail_size, thumbnail_size), Image.Resampling.LANCZOS)
            
            # Save thumbnail
            thumb_filename = f"thumb_{filename}"
            thumb_path = os.path.join(temp_dir, thumb_filename)
            thumb_img.save(thumb_path, 'JPEG', quality=85, optimize=True)
            
            # Get file sizes
            original_size = os.path.getsize(image_path)
            thumb_size = os.path.getsize(thumb_path)
            
            print(f"   Thumbnail size: {thumb_img.size}")
            print(f"   Original file: {original_size:,} bytes")
            print(f"   Thumbnail file: {thumb_size:,} bytes")
            print(f"   Size reduction: {((original_size - thumb_size) / original_size * 100):.1f}%")
        
        print(f"\n✨ Simulation complete!")
        print(f"   Files created in: {temp_dir}")
        print(f"   (Files will be cleaned up automatically)")

def main():
    try:
        simulate_thumbnail_generation()
        
        print("\n🎯 Key Benefits:")
        print("   • Faster loading on mobile/slow connections")
        print("   • Reduced bandwidth usage")  
        print("   • Better user experience in file browsers")
        print("   • Automatic generation and caching")
        
        print("\n🚀 Next Steps:")
        print("   1. Start your server: ./start_server.sh")
        print("   2. Upload some images via the web interface")
        print("   3. Check /mnt/photos/{username}/thumbnails/")
        print("   4. Test API: GET /thumbnails/{filename}")
        
    except ImportError:
        print("❌ Error: Pillow (PIL) is required for thumbnail generation")
        print("   Install it with: pip install pillow")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
