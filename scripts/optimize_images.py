import os
from PIL import Image
from pathlib import Path

def optimize_image(input_path, output_path, max_size=(400, 400), quality=85):
    try:
        with Image.open(input_path) as img:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
        print(f"Optimized: {input_path} -> {output_path}")
    except Exception as e:
        print(f"Error {input_path}: {e}")

def main():
    images_dir = Path("static/images")
    if not images_dir.exists():
        print("No static/images/ directory")
        return
    
    for root, dirs, files in os.walk(images_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                input_path = Path(root) / file
                output_path = input_path
                
                # Backup original
                backup_path = input_path.with_suffix(input_path.suffix + '.original')
                if not backup_path.exists():
                    input_path.rename(backup_path)
                
                # For PNG, convert to JPG; else optimize JPG
                if file.lower().endswith('.png'):
                    output_path = input_path.with_suffix('.jpg')
                
                optimize_image(backup_path, output_path)

if __name__ == "__main__":
    main()

