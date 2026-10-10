import os
from PIL import Image, ImageDraw

def create_star_sticker(filepath):
    # Create a 200x200 transparent image
    img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple yellow star polygon
    # Points for a 5-point star
    star_points = [
        (100, 10), (120, 75), (190, 75), (135, 115), 
        (155, 185), (100, 140), (45, 185), (65, 115), 
        (10, 75), (80, 75)
    ]
    # Draw star with yellow color and orange outline
    draw.polygon(star_points, fill=(255, 215, 0, 255), outline=(255, 140, 0, 255), width=4)
    
    # Draw a cute simple face
    # Left eye
    draw.ellipse([80, 80, 95, 100], fill=(0, 0, 0, 255))
    # Right eye
    draw.ellipse([105, 80, 120, 100], fill=(0, 0, 0, 255))
    # Smile
    draw.arc([80, 90, 120, 120], start=20, end=160, fill=(0, 0, 0, 255), width=4)
    
    img.save(filepath)
    print(f"Created {filepath}")

def create_smiley_sticker(filepath):
    img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Face circle
    draw.ellipse([10, 10, 190, 190], fill=(255, 220, 50, 255), outline=(230, 150, 20, 255), width=6)
    
    # Left eye
    draw.ellipse([60, 60, 85, 95], fill=(0, 0, 0, 255))
    # Right eye
    draw.ellipse([115, 60, 140, 95], fill=(0, 0, 0, 255))
    
    # Cheeks
    draw.ellipse([35, 100, 65, 120], fill=(255, 100, 100, 150))
    draw.ellipse([135, 100, 165, 120], fill=(255, 100, 100, 150))
    
    # Smile
    draw.arc([60, 90, 140, 150], start=20, end=160, fill=(0, 0, 0, 255), width=8)
    
    img.save(filepath)
    print(f"Created {filepath}")

if __name__ == "__main__":
    os.makedirs("assets/stickers", exist_ok=True)
    create_star_sticker("assets/stickers/star.png")
    create_smiley_sticker("assets/stickers/smiley.png")
