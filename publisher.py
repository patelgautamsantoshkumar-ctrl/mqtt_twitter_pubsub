
import tkinter as tk
from tkinter import messagebox
import paho.mqtt.client as mqtt

# ---- MQTT Broker settings ----
BROKER_HOST = "test.mosquitto.org"
BROKER_PORT = 1883
BASE_TOPIC = "class/mqtt_twitter/hashtags"

# Function to clean hashtag input (removes "#" sign)
def clean_hashtag(s):
    s = s.strip()
    if s.startswith("#"):
        s = s[1:]
    return s


# ---- Main Publisher GUI class ----
class PublisherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tweet Poster (Publisher)")

        # --- GUI Layout ---
        tk.Label(root, text="Username").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.username_entry = tk.Entry(root, width=28)
        self.username_entry.grid(row=0, column=1, padx=6, pady=6)
        self.username_entry.insert(0, "user1")

        tk.Label(root, text="Tweet").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.tweet_entry = tk.Entry(root, width=28)
        self.tweet_entry.grid(row=1, column=1, padx=6, pady=6)
        self.tweet_entry.insert(0, "Hello MQTT!")

        tk.Label(root, text="Hashtag").grid(row=2, column=0, sticky="e", padx=6, pady=6)
        self.hashtag_entry = tk.Entry(root, width=28)
        self.hashtag_entry.grid(row=2, column=1, padx=6, pady=6)
        self.hashtag_entry.insert(0, "#Sports")

        # Label to show connection status
        self.status_label = tk.Label(root, text="Disconnected", fg="red")
        self.status_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=6, pady=6)

        # Button to send tweet
        publish_btn = tk.Button(root, text="Publish Tweet", command=self.publish_tweet)
        publish_btn.grid(row=4, column=0, columnspan=2, padx=6, pady=10)

        # --- MQTT setup ---
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

        try:
            self.client.connect(BROKER_HOST, BROKER_PORT, 60)
            self.client.loop_start()  # Start MQTT background thread
        except Exception as e:
            messagebox.showerror("MQTT Error", f"Could not connect.\n{e}")

        # Handle app closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---- MQTT Callbacks ----
    def on_connect(self, *args):
        self.status_label.config(text=f"Connected to {BROKER_HOST}:{BROKER_PORT}", fg="green")

    def on_disconnect(self, *args):
        self.status_label.config(text="Disconnected", fg="red")

    # ---- Publish tweet to broker ----
    def publish_tweet(self):
        user = self.username_entry.get().strip()
        msg = self.tweet_entry.get().strip()
        tag = clean_hashtag(self.hashtag_entry.get())

        # Validate input
        if not user:
            messagebox.showwarning("Missing", "Please enter a username.")
            return
        if not tag:
            messagebox.showwarning("Missing", "Please enter a hashtag like #Sports.")
            return

        topic = f"{BASE_TOPIC}/{tag}"
        payload = f"{user}: {msg}"  # Message format as per requirement

        try:
            # Publish message to the topic
            self.client.publish(topic, payload)
            messagebox.showinfo("Published", f"Topic: {topic}\nMessage: {payload}")
        except Exception as e:
            messagebox.showerror("Publish Error", str(e))

    # ---- Close app safely ----
    def on_close(self):
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception:
            pass
        self.root.destroy()


# ---- Main program ----
if __name__ == "__main__":
    root = tk.Tk()
    app = PublisherApp(root)
    root.mainloop()