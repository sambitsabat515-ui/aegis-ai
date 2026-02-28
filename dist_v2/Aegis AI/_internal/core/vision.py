import threading
import time
import logging
import mss
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)

# Basic setup, may need exact path on Windows like:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class VisionWatcher:
    def __init__(self, ai_engine):
        self.ai_engine = ai_engine
        self.running = False
        self.thread = None
        self.last_text = ""
        self.mock_mode = False

    def _watch_loop(self):
        with mss.mss() as sct:
            while self.running:
                try:
                    # Capture primary monitor
                    monitor = sct.monitors[1]
                    screenshot = sct.grab(monitor)
                    
                    # Convert to PIL Image
                    img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                    
                    text = ""
                    if not self.mock_mode:
                        try:
                            text = pytesseract.image_to_string(img)
                        except pytesseract.TesseractNotFoundError:
                            logger.warning("Tesseract not found. Falling back to mock OCR data.")
                            self.mock_mode = True
                    
                    if self.mock_mode:
                        # Provide mock data during demo if Tesseract is missing
                        text = "A fake mock text regarding urgent payment needed account suspended netflix-verify.tk"

                    # Only analyze if text changed significantly
                    if len(text) > 10 and text != self.last_text:
                        self.last_text = text
                        logger.info("Detected screen change via OCR, analyzing...")
                        self.ai_engine.analyze_text(text)
                except Exception as e:
                    logger.error(f"Error in Vision loop: {e}")
                    
                time.sleep(5)  # Poll every 5 seconds for proactive monitoring

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.thread.start()
        logger.info("VisionWatcher started.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("VisionWatcher stopped.")
