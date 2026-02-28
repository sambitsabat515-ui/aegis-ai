import sounddevice as sd
import numpy as np

def test_all_devices():
    devices = sd.query_devices()
    print(f"Total devices found: {len(devices)}")
    
    working_devices = []
    
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            print(f"\n--- Testing Device [{i}]: {dev['name']} ---")
            try:
                # Record 2 seconds
                duration = 2
                samplerate = int(dev['default_samplerate'])
                channels = min(1, dev['max_input_channels'])
                
                print(f"  Recording {duration}s at {samplerate}Hz (Channels: {channels}). PLEASE MAKE SOME NOISE...")
                
                # Use a block context to ensure streams are closed properly
                recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype='float32', device=i)
                sd.wait()
                
                max_amp = np.max(np.abs(recording))
                print(f"  Max Amplitude: {max_amp:.6f}")
                
                if max_amp > 0.001:  # Threshold for noise vs absolute silence
                    print("  >> SUCCESS: DEVICE HEARD AUDIO! <<")
                    working_devices.append((i, dev['name'], max_amp))
                else:
                    print("  >> FAILED: Device recorded silence.")
                    
            except Exception as e:
                print(f"  >> ERROR testing device: {e}")
                
    print("\n================ SUMMARY ================")
    if working_devices:
        print("Working input devices found:")
        for idx, name, amp in working_devices:
            print(f"  ID {idx}: {name} (Peak: {amp:.4f})")
    else:
        print("CRITICAL: NO DEVICES DETECTED ANY SOUND. Check hardware mute buttons or Windows Privacy settings (Allow apps to access microphone).")

if __name__ == "__main__":
    test_all_devices()
