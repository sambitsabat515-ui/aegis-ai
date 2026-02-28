import re
import logging
from core.overlay import overlay

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        self.current_risk = "GREEN"
        self.threat_confidence = 0.0
        self.recent_alerts = []
        self.audio_engine = None  # To be injected

    def set_audio_engine(self, audio_engine):
        self.audio_engine = audio_engine

    def analyze_text(self, text: str):
        # Fallback for old calls
        self.analyze_text_with_boxes(text, [])

    def analyze_text_with_boxes(self, text: str, boxes: list):
        text_lower = text.lower()
        
        # Threat patterns
        red_patterns = [
            r"account suspended",
            r"immediate action required",
            r"verify your account immediately",
            r"netflix-verify\.tk",
            r"bank-verify",
        ]
        
        yellow_patterns = [
            r"urgent",
            r"one-time password",
            r"otp",
            r"click here",
            r"payment needed"
        ]
        
        risk = "GREEN"
        confidence = 0.0
        message = ""
        speech_warning = ""

        # Check RED
        for p in red_patterns:
            if re.search(p, text_lower):
                risk = "RED"
                confidence = 0.95
                message = f"Phishing attempt detected: Found high-risk phrase '{p.replace('.*', '')}'"
                speech_warning = "Excuse me, I've detected a high-risk phishing attempt on your screen. I strongly advise against interacting with it."
                break
                
        # Check YELLOW if not RED
        if risk == "GREEN":
            for p in yellow_patterns:
                if re.search(p, text_lower):
                    risk = "YELLOW"
                    confidence = 0.60
                    message = f"Suspicious activity: Found caution phrase '{p}'"
                    speech_warning = "Caution, I've noticed suspicious or urgent language on your screen. Please be careful."
                    break

        if risk != "GREEN":
            self.add_alert(risk, confidence, message)
            
            # Highlight detected words on screen
            if boxes:
                # Find which boxes contain the matched pattern (simplified to any part of pattern)
                matched_words = [w for w in message.split("'")[1].split() if len(w) > 3] if "'" in message else []
                for (word, x, y, w, h) in boxes:
                    if word.lower() in text_lower and any(mw.lower() in word.lower() for mw in matched_words):
                        overlay.draw_highlight(x, y, w, h, risk=risk, duration=5.0)

            if self.audio_engine:
                self.audio_engine.speak(speech_warning)
        else:
            self.current_risk = "GREEN"
            self.threat_confidence = 0.0
            logger.info("No threats detected.")

    def add_alert(self, risk_level: str, confidence: float, message: str):
        self.current_risk = risk_level
        self.threat_confidence = confidence
        self.recent_alerts.append({"message": message, "risk": risk_level})
        logger.warning(f"ALERT [{risk_level}]: {message}")
        
    def clear_alerts(self):
        self.current_risk = "GREEN"
        self.threat_confidence = 0.0
        self.recent_alerts = []
        logger.info("Alerts cleared by user.")
        
    def get_state(self):
        return {
            "risk_level": self.current_risk,
            "confidence": self.threat_confidence,
            "alerts": self.recent_alerts[-5:] # last 5 alerts
        }
