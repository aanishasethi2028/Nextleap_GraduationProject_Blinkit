import os
import sys
import unittest
from unittest.mock import MagicMock

# Add workspace root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../data")))

# Mock Streamlit to allow importing dashboard.py without Streamlit runtime errors
# Mock Streamlit to allow importing dashboard.py without Streamlit runtime errors
mock_st = MagicMock()
mock_st.columns.side_effect = lambda n: [MagicMock() for _ in range(n if isinstance(n, int) else len(n))]
mock_st.tabs.side_effect = lambda titles: [MagicMock() for _ in range(len(titles))]
sys.modules['streamlit'] = mock_st
sys.modules['streamlit.components'] = MagicMock()
sys.modules['streamlit.components.v1'] = MagicMock()

# Import functions to test
from data.sanitizeReviews import is_low_signal, get_source_type

class TestLENSPipelineEdgeCases(unittest.TestCase):
    
    def test_low_signal_detection(self):
        """Test how the sanitization pipeline flags low-signal and emoji-only noise."""
        # Emoji only reviews must be flagged as low-signal
        self.assertTrue(is_low_signal("😊😊😊😊😊"))
        self.assertTrue(is_low_signal("🛵🚀👍"))
        
        # Reviews with less than 10 latin or devanagari letters must be flagged
        self.assertTrue(is_low_signal("Blinkit ok")) # 9 letters
        self.assertTrue(is_low_signal("123456789")) # 0 letters
        
        # Proper Hinglish or English reviews (>= 10 letters) should pass
        self.assertFalse(is_low_signal("Blinkit very good")) # 16 letters
        self.assertFalse(is_low_signal("delivery boy behavior was bad"))
        self.assertFalse(is_low_signal("समय पर डिलीवरी हुई")) # Devanagari letters count
        
        # Empty string handling
        self.assertTrue(is_low_signal(""))
        self.assertTrue(is_low_signal("   "))

    def test_source_type_parsing(self):
        """Test that the source channel classification is case-insensitive and robust."""
        self.assertEqual(get_source_type("https://youtube.com/watch?v=123"), "youtube")
        self.assertEqual(get_source_type("http://YOUTU.BE/abc"), "youtube")
        self.assertEqual(get_source_type("Google Play Store Reviews"), "playstore")
        self.assertEqual(get_source_type("App Store"), "appstore")
        self.assertEqual(get_source_type("MouthShut.com Review Site"), "mouthshut")
        self.assertEqual(get_source_type("reddit thread on r/india"), "reddit")
        self.assertEqual(get_source_type("trustpilot feedback"), "trustpilot")
        self.assertEqual(get_source_type("random website"), "other")
        self.assertEqual(get_source_type(None), "other")

    def test_source_link_mapping(self):
        """Test defensive mapping of source strings to actual web URLs in the dashboard."""
        # Import the helper from src.dashboard
        from src.dashboard import get_source_url
        
        # Test exact Play Store mappings
        self.assertEqual(get_source_url("Google Play Store"), "https://play.google.com/store/apps/details?id=com.grofers.customerapp")
        self.assertEqual(get_source_url("playstore"), "https://play.google.com/store/apps/details?id=com.grofers.customerapp")
        
        # Test App Store mappings
        self.assertEqual(get_source_url("App Store"), "https://apps.apple.com/in/app/blinkit-grocery-delivery/id960984733")
        self.assertEqual(get_source_url("appstore"), "https://apps.apple.com/in/app/blinkit-grocery-delivery/id960984733")
        
        # Test direct URLs are preserved
        self.assertEqual(get_source_url("https://youtube.com/watch?v=123"), "https://youtube.com/watch?v=123")
        
        # Test fallback
        self.assertEqual(get_source_url(None), "https://blinkit.com")
        self.assertEqual(get_source_url(12345), "https://blinkit.com")
        self.assertEqual(get_source_url("some invalid channel"), "https://blinkit.com")

if __name__ == "__main__":
    print("==========================================================")
    print("   RUNNING LENS PROGRAMMATIC PIPELINE EDGE CASE TESTS     ")
    print("==========================================================")
    unittest.main()
