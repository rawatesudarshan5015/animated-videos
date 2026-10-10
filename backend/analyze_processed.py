import os
import cv2
import numpy as np

def analyze_single_video(path):
    print("=" * 60)
    print(f"ANALYZING VIDEO: {path}")
    print("=" * 60)
    
    if not os.path.exists(path):
        print("ERROR: File not found")
        return
        
    cap = cv2.VideoCapture(path)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"Dimensions: {width}x{height} | Frames: {frames} | FPS: {fps:.2f}")
    
    # Extract middle frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, frames // 2)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("ERROR: Failed to read frame")
        return
        
    # Check color quantization
    # In cartoon filter, color is quantized with // 25 * 25, or // 32 * 32, or // 20 * 20
    # Let's check unique values per channel
    unique_vals = [len(np.unique(frame[:, :, i])) for i in range(3)]
    print(f"Unique values per channel: B: {unique_vals[0]}, G: {unique_vals[1]}, R: {unique_vals[2]}")
    
    # Count how many pixel values are exact multiples of 20, 25, or 32
    matches_25 = np.sum((frame % 25 == 0) | (frame % 25 == 24) | (frame % 25 == 1))
    matches_32 = np.sum((frame % 32 == 0) | (frame % 32 == 31) | (frame % 32 == 1))
    matches_20 = np.sum((frame % 20 == 0) | (frame % 20 == 19) | (frame % 20 == 1))
    
    pct_25 = (matches_25 / frame.size) * 100
    pct_32 = (matches_32 / frame.size) * 100
    pct_20 = (matches_20 / frame.size) * 100
    
    print(f"Quantization statistics:")
    print(f"  - Matches cartoon filter (bin 25): {pct_25:.1f}%")
    print(f"  - Matches light_cartoon filter (bin 32): {pct_32:.1f}%")
    print(f"  - Matches heavy_cartoon filter (bin 20): {pct_20:.1f}%")
    
    # Check pure black outline pixels
    black_pixels = np.sum(np.all(frame == [0, 0, 0], axis=-1))
    pct_black = (black_pixels / (frame.shape[0] * frame.shape[1])) * 100
    print(f"Pure black pixels (outlines): {black_pixels} ({pct_black:.3f}%)")
    
    # Verdict
    is_animated = False
    filter_type = "None"
    
    if max(pct_25, pct_32, pct_20) > 40.0:
        is_animated = True
        if pct_25 > pct_32 and pct_25 > pct_20:
            filter_type = "Standard Cartoon (bin 25)"
        elif pct_32 > pct_25 and pct_32 > pct_20:
            filter_type = "Light Cartoon (bin 32)"
        else:
            filter_type = "Heavy Cartoon (bin 20)"
            
    # Also if unique values are very low (e.g. less than 40 per channel)
    if sum(unique_vals) / 3 < 50:
        is_animated = True
        filter_type = f"Quantized Colors (avg unique: {sum(unique_vals)/3:.1f})"
        
    print("\nVERDICT:")
    if is_animated:
        print(f"[YES] This video IS animated/processed using: {filter_type}!")
    else:
        print("[NO] This video is NOT cartoon animated. It has full-range, continuous gradients (regular video).")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    analyze_single_video("uploads/output/e84c9584-78d4-4681-879d-6deb01d5770b_processed.mp4")
    analyze_single_video("uploads/output/ae7a0180-69de-45d6-b9c7-b5180f797d85_processed.mp4")
