import Quartz
from pynput import keyboard
import subprocess
import time
import threading

class HeadphoneScrollUtility:
    def __init__(self):
        self.listener = None
        self.running = True
        self.scroll_mode = True
        self.last_press_time = 0
        self.press_count = 0
        self.is_scrolling = False
        self.scroll_speed = 0.01  # Initial delay between scroll events
        self.acceleration = 0.95  # Factor by which delay decreases

    def disable_volume_changes(self):
        subprocess.run(["osascript", "-e", "set volume output muted true"])

    def restore_volume_changes(self):
        subprocess.run(["osascript", "-e", "set volume output muted false"])

    def on_press(self, key):
        try:
            current_time = time.time()
            if key == keyboard.Key.media_play_pause:
                if current_time - self.last_press_time < 0.5:
                    self.press_count += 1
                else:
                    self.press_count = 1
                self.last_press_time = current_time

                if self.press_count == 3:
                    self.toggle_scroll_mode()
                    self.press_count = 0
            elif key == keyboard.Key.media_volume_up:
                if self.scroll_mode and not self.is_scrolling:
                    self.is_scrolling = True
                    threading.Thread(target=self.smooth_scroll, args=(1,)).start()
            elif key == keyboard.Key.media_volume_down:
                if self.scroll_mode and not self.is_scrolling:
                    self.is_scrolling = True
                    threading.Thread(target=self.smooth_scroll, args=(-1,)).start()
            elif key == keyboard.Key.esc:
                self.running = False
                return False  # Stop listener
        except AttributeError:
            pass

    def on_release(self, key):
        if key in {keyboard.Key.media_volume_up, keyboard.Key.media_volume_down}:
            self.is_scrolling = False

    def toggle_scroll_mode(self):
        self.scroll_mode = not self.scroll_mode
        print(f"Scroll mode: {'ON' if self.scroll_mode else 'OFF'}")

    def smooth_scroll(self, direction):
        self.disable_volume_changes()
        delay = self.scroll_speed
        while self.is_scrolling:
            self.scroll_page(direction)
            time.sleep(delay)
            delay = max(0.001, delay * self.acceleration)  # Decrease delay to accelerate
        self.restore_volume_changes()

    def scroll_page(self, direction):
        scroll_unit = 10 if direction > 0 else -10  # Smaller unit for smoother scrolling
        event = Quartz.CGEventCreateScrollWheelEvent(
            None, Quartz.kCGScrollEventUnitPixel, 1, scroll_unit
        )
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)

    def run(self):
        print("Headphone Scroll Utility is running. Press ESC to exit.")
        print("Triple-press the play/pause button to toggle scroll mode.")
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as self.listener:
            while self.running:
                time.sleep(0.1)

if __name__ == "__main__":
    print("Starting Headphone Scroll Utility...")
    print("Please ensure you've granted the necessary permissions:")
    print("1. Go to System Preferences > Security & Privacy > Privacy > Accessibility")
    print("2. Add your terminal application (e.g., Terminal or iTerm) to the list")
    print("3. Restart the script after granting permissions")
    input("Press Enter to continue...")

    utility = HeadphoneScrollUtility()
    utility.run()

    print("Headphone Scroll Utility has been stopped.")
