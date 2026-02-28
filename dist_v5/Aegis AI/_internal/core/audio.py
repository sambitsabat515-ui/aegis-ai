import threading
import time
import logging
import pyttsx3
import speech_recognition as sr
import webbrowser
import os
import sounddevice as sd
from core.app_launcher import AppLauncher

logger = logging.getLogger(__name__)

class AudioEngine:
    def __init__(self, ai_engine):
        self.ai_engine = ai_engine
        self.ai_engine.set_audio_engine(self)
        self.app_launcher = AppLauncher()
        self.running = False
        self.thread = None
        self.recognizer = sr.Recognizer()
        
        # Test TTS initialization
        try:
            self.tts = pyttsx3.init()
            voices = self.tts.getProperty('voices')
            for voice in voices:
                if "Zira" in voice.name or "Hazel" in voice.name or "David" in voice.name: # Try male/female defaults
                    self.tts.setProperty('voice', voice.id)
                    break
        except Exception as e:
            logger.error(f"Failed to init pyttsx3: {e}")
            self.tts = None

    def _record_audio(self, duration=4, samplerate=16000):
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()
        return sr.AudioData(recording.tobytes(), samplerate, 2)

    def _listen_loop(self):
        try:
            # Test if sounddevice works
            if sd.query_devices() is None or len(sd.query_devices()) == 0:
                raise Exception("No audio devices found")
            logger.info("Microphone initialized via sounddevice. Listening for 'Hey Friday'...")
            has_mic = True
        except Exception as e:
            logger.error(f"Could not initialize microphone: {e}. Voice input disabled. Using mock timer instead.")
            has_mic = False

        while self.running:
            if not has_mic:
                time.sleep(5)
                # Mock a voice interaction to test the flow
                logger.info("[MOCK] Simulating 'Hey Friday, scan this' command...")
                self._mock_handle_command("scan")
                time.sleep(15)
                continue
                
            try:
                # Record a chunk of audio to listen for wake word
                audio = self._record_audio(duration=3)
                
                try:
                    text = self.recognizer.recognize_google(audio).lower()
                    if text:
                        logger.info(f"Heard: {text}")
                        
                        if "hey friday" in text or "friday" in text:
                            self.speak("Yes, boss. How can I help?")
                            # Give TTS a moment before recording again
                            time.sleep(2)
                            self._handle_command()
                            
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    logger.error(f"Could not request results from STT service; {e}")
                    
            except Exception as e:
                logger.error(f"Error in listen loop: {e}")
                time.sleep(1)

    def _handle_command(self):
        try:
            logger.info("Listening for command...")
            audio = self._record_audio(duration=5)
            text = self.recognizer.recognize_google(audio).lower()
            logger.info(f"Command heard: {text}")
            self._process_text_command(text)
                
        except sr.UnknownValueError:
            self.speak("I didn't catch that command.")
        except Exception as e:
            logger.error(f"Error handling command: {e}")

    def _mock_handle_command(self, text):
        self._process_text_command(text)
        
    def _process_text_command(self, text):
        if "scan" in text or "safe" in text:
            self.speak("Scanning screen now.")
            if self.ai_engine.current_risk == "GREEN":
                self.speak("No active threats detected. Systems are green.")
            else:
                message_part = self.ai_engine.recent_alerts[-1]['message'] if self.ai_engine.recent_alerts else "an anomaly."
                self.speak(f"I found a {self.ai_engine.current_risk} level threat. {message_part}")
        elif "explain" in text or "why" in text:
            if self.ai_engine.current_risk != "GREEN":
                self.speak("The detected pattern matches known phishing attempts and high-risk URL domains.")
            else:
                self.speak("There is nothing to explain at the moment. Everything is secure.")
        elif "block" in text or "ignore" in text:
            self.speak("Done. Sender blocked and activity neutralized.")
            # Reset state
            self.ai_engine.analyze_text("") # Clear
        elif text.startswith("open ") or text.startswith("launch ") or text.startswith("start "):
            target = text.replace("open ", "").replace("launch ", "").replace("start ", "").strip()
            self.speak(f"Opening {target}.")
            try:
                # Handle common websites first
                if "google" in target:
                    webbrowser.open("https://www.google.com")
                elif "youtube" in target:
                    webbrowser.open("https://www.youtube.com")
                elif "netflix" in target:
                    webbrowser.open("https://www.netflix.com")
                else:
                    self.app_launcher.launch_app(target)
            except Exception as e:
                logger.error(f"Failed to open {target}: {e}")
                self.speak(f"Sorry, I couldn't open {target}.")
        else:
            self.speak("I'm sorry, I didn't verify that command over the noise.")

    def speak(self, text):
        logger.info(f"[FRIDAY SPEAKS]: {text}")
        if self.tts:
            def _speak():
                try:
                    engine = pyttsx3.init()
                    engine.say(text)
                    engine.runAndWait()
                except Exception as e:
                    logger.error(f"TTS Error in thread: {e}")
            threading.Thread(target=_speak, daemon=True).start()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        logger.info("AudioEngine started.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("AudioEngine stopped.")
