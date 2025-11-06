
import tkinter as tk
from tkinter import scrolledtext, messagebox
import paho.mqtt.client as mqtt

# ---- MQTT Broker settings ----
BROKER_HOST = "test.mosquitto.org"     # Public MQTT broker
BROKER_PORT = 1883                     # Default port for MQTT
BASE_TOPIC = "class/mqtt_twitter/hashtags"  # Base topic used by both apps


# Function to clean hashtag (e.g., "#Sports" → "Sports")
def clean_hashtag(s):
    s = s.strip()
    if s.startswith("#"):
        s = s[1:]
    return s


# ---- Main Subscriber GUI class ----
class SubscriberApp:
    def __init__(self, root):
        # Create main window
        self.root = root
        self.root.title("Hashtag Follower (Subscriber)")

        # Track current subscribed topic
        self.current_topic = None

        # --- GUI Layout Section ---
        tk.Label(root, text="Hashtag").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.hashtag_entry = tk.Entry(root, width=22)
        self.hashtag_entry.grid(row=0, column=1, padx=6, pady=6)
        self.hashtag_entry.insert(0, "#Sports")  # default hashtag

        # Buttons for subscribe and unsubscribe
        sub_btn = tk.Button(root, text="Subscribe", command=self.subscribe_now)
        sub_btn.grid(row=0, column=2, padx=4, pady=6)

        unsub_btn = tk.Button(root, text="Unsubscribe", command=self.unsubscribe_now)
        unsub_btn.grid(row=0, column=3, padx=4, pady=6)

        # Label to show connection status
        self.status_label = tk.Label(root, text="Disconnected", fg="red")
        self.status_label.grid(row=1, column=0, columnspan=4, sticky="w", padx=6, pady=6)

        # Text area to display live tweets
        self.feed = scrolledtext.ScrolledText(root, width=60, height=12, state="disabled")
        self.feed.grid(row=2, column=0, columnspan=4, padx=6, pady=6)

        # --- MQTT Setup ---
        # Create MQTT client
        self.client = mqtt.Client()
        # Assign callback functions
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        # Try to connect to the broker
        try:
            self.client.connect(BROKER_HOST, BROKER_PORT, 60)
            self.client.loop_start()  # Start background network thread
        except Exception as e:
            messagebox.showerror("MQTT Error", f"Could not connect.\n{e}")

        # Close the connection safely when GUI is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---- MQTT Callback Functions ----
    def on_connect(self, *args):
        # Called when connection succeeds
        self.status_label.config(text=f"Connected to {BROKER_HOST}:{BROKER_PORT}", fg="green")
        # Re-subscribe if user was already subscribed before reconnecting
        if self.current_topic:
            self.client.subscribe(self.current_topic)

    def on_disconnect(self, *args):
        # Called when disconnected
        self.status_label.config(text="Disconnected", fg="red")

    def on_message(self, client, userdata, message):
        # Called when a new tweet message is received
        text = message.payload.decode("utf-8", errors="ignore")
        self._append_line(text)

    # ---- Button Functions ----
    def subscribe_now(self):
        # Get hashtag and subscribe to its MQTT topic
        tag = clean_hashtag(self.hashtag_entry.get())
        if not tag:
            messagebox.showwarning("Missing", "Please enter a hashtag like #Sports.")
            return
        topic = f"{BASE_TOPIC}/{tag}"
        self.client.subscribe(topic)
        self.current_topic = topic
        self._append_line(f"[✓] Subscribed to #{tag}")

    def unsubscribe_now(self):
        # Unsubscribe from current topic
        if self.current_topic:
            self.client.unsubscribe(self.current_topic)
            self._append_line(f"[–] Unsubscribed from {self.current_topic}")
            self.current_topic = None

    # ---- Helper to display text in GUI ----
    def _append_line(self, line):
        self.feed.config(state="normal")
        self.feed.insert("end", line + "\n")
        self.feed.see("end")
        self.feed.config(state="disabled")

    # ---- Cleanup on close ----
    def on_close(self):
        try:
            if self.current_topic:
                self.client.unsubscribe(self.current_topic)
            self.client.loop_stop()
            self.client.disconnect()
        except Exception:
            pass
        self.root.destroy()


# ---- Main program ----
if __name__ == "__main__":
    root = tk.Tk()
    app = SubscriberApp(root)
    root.mainloop()
