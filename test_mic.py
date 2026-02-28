import sounddevice as sd
import speech_recognition as sr
import time

def test_mic():
    print("Testing audio devices...")
    try:
        devices = sd.query_devices()
        print(f"Found {len(devices)} devices.")
        for d in devices:
            if d['max_input_channels'] > 0:
                print(f"Input Device: {d['name']} (Channels: {d['max_input_channels']})")
    except Exception as e:
        print(f"Error querying devices: {e}")
        return

    duration = 5
    samplerate = 16000
    
    print("\nRecording for 5 seconds... PLEASE SPEAK NOW.")
    try:
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()
        
        print(f"Recording finished. Array shape: {recording.shape}, max amplitude: {recording.max()}, min amplitude: {recording.min()}")
        
        if recording.max() == 0 and recording.min() == 0:
            print("WARNING: Captured audio is completely silent (all zeros). Check microphone permissions/settings.")
        
        print("\nAttempting speech recognition...")
        audio_data = sr.AudioData(recording.tobytes(), samplerate, 2)
        r = sr.Recognizer()
        text = r.recognize_google(audio_data)
        print(f"SUCCESS! Recognized: '{text}'")
        
    except sr.UnknownValueError:
        print("Google STT could not understand audio (might be silence or noise).")
    except sr.RequestError as e:
        print(f"Could not request results from STT service; {e}")
    except Exception as e:
        print(f"Recording/Processing Error: {e}")

if __name__ == "__main__":
    test_mic()
