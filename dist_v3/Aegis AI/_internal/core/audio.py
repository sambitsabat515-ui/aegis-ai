import threading
import time
import logging
import pyttsx3
import speech_recognition as sr
import webbrowser
import os

logger = logging.getLogger(__name__)

class AudioEngine:
    def __init__(self, ai_engine):
        self.ai_engine = ai_engine
        self.ai_engine.set_audio_engine(self)
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

    def _listen_loop(self):
        try:
            mic = sr.Microphone()
            with mic as source:
                self.recognizer.adjust_for_ambient_noise(source)
                logger.info("Microphone calibrated. Listening for 'Hey Aegis'...")
        except Exception as e:
            logger.error(f"Could not initialize microphone: {e}. Voice input disabled. Using mock timer instead.")
            mic = None

        while self.running:
            if not mic:
                time.sleep(5)
                # Mock a voice interaction to test the flow
                logger.info("[MOCK] Simulating 'Hey Aegis, scan this' command...")
                self._mock_handle_command("scan")
                time.sleep(15)
                continue
                
            try:
                with mic as source:
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                
                try:
                    text = self.recognizer.recognize_google(audio).lower()
                    logger.info(f"Heard: {text}")
                    
                    if "hey aegis" in text:
                        self.speak("Yes, sir. How can I help?")
                        self._handle_command(mic)
                        
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    logger.error(f"Could not request results from STT service; {e}")
                    
            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                logger.error(f"Error in listen loop: {e}")
                time.sleep(1)

    def _handle_command(self, mic):
        try:
            logger.info("Listening for command...")
            with mic as source:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            text = self.recognizer.recognize_google(audio).lower()
            logger.info(f"Command heard: {text}")
            self._process_text_command(text)
                
        except sr.UnknownValueError:
            self.speak("I didn't catch that command, sir.")
        except sr.WaitTimeoutError:
            self.speak("Command timed out.")
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
        elif text.startswith("open "):
            target = text.replace("open ", "").strip()
            self.speak(f"Opening {target}.")
            try:
                # Handle common websites
                if "google" in target:
                    webbrowser.open("https://www.google.com")
                elif "youtube" in target:
                    webbrowser.open("https://www.youtube.com")
                elif "netflix" in target:
                    webbrowser.open("https://www.netflix.com")
                else:
                    # Try to launch standard windows app (e.g. "whatsapp", "calculator", etc)
                    # Many windows 10/11 apps have protocol handlers like whatsapp: or ms-calculator:
                    os.system(f"start {target}: 2>nul || start {target} 2>nul")
            except Exception as e:
                logger.error(f"Failed to open {target}: {e}")
                self.speak(f"Sorry, I couldn't open {target}.")
        else:
            self.speak("I'm sorry, I didn't verify that command over the noise.")

    def speak(self, text):
        logger.info(f"[AEGIS AI SPEAKS]: {text}")
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
