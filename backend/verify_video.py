import os
import cv2
import numpy as np

def analyze_and_compare():
    input_path = "uploads/e84c9584-78d4-4681-879d-6deb01d5770b.mp4"
    output_path = "uploads/output/e84c9584-78d4-4681-879d-6deb01d5770b_processed.mp4"
    
    print("=" * 60)
    print("VIDEO ANIMATION VERIFIER (OPENCV)")
    print("=" * 60)
    
    if not os.path.exists(input_path):
        print(f"ERROR: Input video not found at {input_path}")
        return
    if not os.path.exists(output_path):
        print(f"ERROR: Processed video not found at {output_path}")
        return

    # Open video captures
    cap_in = cv2.VideoCapture(input_path)
    cap_out = cv2.VideoCapture(output_path)
    
    # Read properties
    fps_in = cap_in.get(cv2.CAP_PROP_FPS)
    fps_out = cap_out.get(cv2.CAP_PROP_FPS)
    frames_in = int(cap_in.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_out = int(cap_out.get(cv2.CAP_PROP_FRAME_COUNT))
    width_in = int(cap_in.get(cv2.CAP_PROP_FRAME_WIDTH))
    height_in = int(cap_in.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width_out = int(cap_out.get(cv2.CAP_PROP_FRAME_WIDTH))
    height_out = int(cap_out.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Original Video:  {width_in}x{height_in} | {frames_in} frames | {fps_in:.2f} FPS")
    print(f"Processed Video: {width_out}x{height_out} | {frames_out} frames | {fps_out:.2f} FPS")
    print("-" * 60)
    
    # Extract a representative frame (middle frame)
    target_frame = min(frames_in, frames_out) // 2
    
    cap_in.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
    cap_out.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
    
    ret_in, frame_in = cap_in.read()
    ret_out, frame_out = cap_out.read()
    
    cap_in.release()
    cap_out.release()
    
    if not ret_in or not ret_out:
        print("ERROR: Failed to extract frame for analysis")
        return
        
    print(f"Analyzing Frame {target_frame}...")
    
    # 1. Color Quantization Check (Unique color values)
    # Get total unique pixel values on each channel
    unique_in = [len(np.unique(frame_in[:, :, i])) for i in range(3)]
    unique_out = [len(np.unique(frame_out[:, :, i])) for i in range(3)]
    
    print("\n[1] Color Quantization (Palette Reduction)")
    print(f"  - Original frame unique values per channel:  B: {unique_in[0]}, G: {unique_in[1]}, R: {unique_in[2]}")
    print(f"  - Processed frame unique values per channel: B: {unique_out[0]}, G: {unique_out[1]}, R: {unique_out[2]}")
    
    # Check if values are multiples of 25 (standard cartoon quantization uses (pixel // 25) * 25)
    quantized_matches = 0
    total_pixels = frame_out.size
    # Count how many pixels have values that are multiples of 25 (or close due to compression artifacts)
    multiples_of_25 = np.sum((frame_out % 25 == 0) | (frame_out % 25 == 24) | (frame_out % 25 == 1))
    pct_quantized = (multiples_of_25 / total_pixels) * 100
    print(f"  - Pixels matching quantization bins (~multiples of 25): {pct_quantized:.1f}%")

    # 2. Edge Outlines Check (Solid Black Pixels)
    # The cartoon filter overlays black outlines (color [0,0,0])
    black_pixels_in = np.sum(np.all(frame_in == [0, 0, 0], axis=-1))
    black_pixels_out = np.sum(np.all(frame_out == [0, 0, 0], axis=-1))
    
    pct_black_in = (black_pixels_in / (frame_in.shape[0] * frame_in.shape[1])) * 100
    pct_black_out = (black_pixels_out / (frame_out.shape[0] * frame_out.shape[1])) * 100
    
    print("\n[2] Edge Outlines (Black Outlines Overlay)")
    print(f"  - Original frame pure black pixels:  {black_pixels_in} ({pct_black_in:.3f}%)")
    print(f"  - Processed frame pure black pixels: {black_pixels_out} ({pct_black_out:.3f}%)")

    # 3. Overall Image Difference
    mae = np.mean(np.abs(frame_in.astype(float) - frame_out.astype(float)))
    print("\n[3] Difference Metric")
    print(f"  - Mean Absolute Error (MAE) between frames: {mae:.2f}")
    
    # 4. Final Verdict
    print("-" * 60)
    print("VERDICT:")
    is_animated = False
    reasons = []
    
    if mae > 5:
        reasons.append("Significant pixel-level modification detected")
        
        # Unique color reduction check
        avg_unique_in = sum(unique_in) / 3
        avg_unique_out = sum(unique_out) / 3
        if avg_unique_out < avg_unique_in * 0.7:
            reasons.append(f"Color palette reduced significantly (Average unique values: {avg_unique_in:.1f} -> {avg_unique_out:.1f})")
            is_animated = True
            
        # Black lines check
        if pct_black_out > pct_black_in + 0.1:
            reasons.append(f"Bold black cartoon outline pixels added (+{pct_black_out - pct_black_in:.2f}%)")
            is_animated = True
            
        if pct_quantized > 50:
            reasons.append(f"Color values show active step-quantization (cartoon flats: {pct_quantized:.1f}%)")
            is_animated = True
    else:
        reasons.append("No significant modification detected between input and output frames")
        
    if is_animated:
        print("[YES] The video is genuinely ANIMATED!")
        print("  Detected features:")
        for r in reasons:
            print(f"  * {r}")
    else:
        print("[NO] The video is NOT animated (or the filter was bypassed/failed).")
        for r in reasons:
            print(f"  * {r}")
            
    # Save a side-by-side comparison image for visual check
    h, w, _ = frame_in.shape
    comparison = np.zeros((h, w * 2, 3), dtype=np.uint8)
    comparison[:, :w] = frame_in
    comparison[:, w:] = frame_out
    
    # Put labels on the frames
    cv2.putText(comparison, "ORIGINAL", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3, cv2.LINE_AA)
    cv2.putText(comparison, "CARTOON ANIMATED", (w + 20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3, cv2.LINE_AA)
    
    cv2.imwrite("comparison.png", comparison)
    print("\nVisual side-by-side frame comparison saved as 'comparison.png'!")
    print("=" * 60)

if __name__ == "__main__":
    analyze_and_compare()
