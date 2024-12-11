import tkinter as tk
import socket
import messages_pb2
import threading

# Initialize server socket
host = "10.0.0.74"
port = 3000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(3)

# Global variables
OctaveSocket = None
OctaveAddr = None
angle = 0  # Placeholder for angle data
TITLE = 36
SUBTITLE = 27
LABEL = 14

def packetReceiver(current_position_label):
    """Receive packets from the ESP32 and update the GUI."""
    global angle
    while True:
        try:
            message = OctaveSocket.recv(128)
            if not message:
                break

            # Print raw data received
            print(f"Raw data received: {message.hex()}")

            # Decode the message
            packet = messages_pb2.Packet()
            packet.ParseFromString(message)

            angle = packet.angle
            print(f"Received: type = {packet.type}, angle = {packet.angle}")

            # Update the position label
            current_position_label.config(text=f"Current position: {angle:.2f}")
        except Exception as e:
            print(f"Error receiving packet: {e}")
            break

def connectOctave(status_label, current_position_label):
    """Handle the connection with the ESP32."""
    global OctaveSocket, OctaveAddr
    print("Waiting for connection...")
    try:
        OctaveSocket, OctaveAddr = s.accept()
        print(f"Connection from {OctaveAddr} has been established")
        status_label.config(text="Connected!", fg="green")

        receiver_thread = threading.Thread(target=packetReceiver, args=(current_position_label,), daemon=True)
        receiver_thread.start()
    except Exception as e:
        print(f"Connection failed: {e}")
        status_label.config(text="Connection failed, try again", fg="red")

def sendNewAngle(new_angle):
    """Send a new commanded angle to the ESP32."""
    try:
        # Create the packet
        packet = messages_pb2.Packet()
        packet.type = 2  # Command type
        packet.angle = new_angle

        # Serialize the packet
        serialized_packet = packet.SerializeToString()

        # Send to ESP32
        OctaveSocket.sendall(serialized_packet)
        print(f"Sent new angle: {new_angle}")
    except Exception as e:
        print(f"Error sending new angle: {e}")

def GUI():
    """Create and manage the GUI."""
    window = tk.Tk()
    window.minsize(1200, 0)

    # Header section
    header = tk.Frame(width=600)
    header_title = tk.Label(master=header, text="Octave Control", font=("Arial", TITLE))
    header_title.pack(pady=5)

    status_label = tk.Label(master=header, text="Not Connected!", fg="red", font=("Arial", 20))
    status_label.pack()

    connectBtn = tk.Button(
        master=header,
        text="Connect",
        fg="white",
        bg="black",
        cursor="hand2",
        command=lambda: connectOctave(status_label, current_position_label)
    )
    connectBtn.pack(pady=(10, 0))

    header.pack(pady=10)

    # Live data section
    data_frame = tk.Frame(master=window)
    angle_title = tk.Label(master=data_frame, text="Data", font=("Arial", SUBTITLE))
    angle_title.pack(pady=5)

    current_position_label = tk.Label(master=data_frame, text="Current position: ---", font=("Arial", LABEL))
    current_position_label.pack()

    data_frame.pack(pady=10, expand=True)

    # Moving section
    moving_frame = tk.Frame(master=window)
    command_frame = tk.Frame(master=moving_frame)
    moving_title = tk.Label(master=command_frame, text="Move Octave", font=("Arial", SUBTITLE))
    moving_caption = tk.Label(
        master=command_frame,
        text="Currently only supports movements about the y axis",
        padx=50,
        wraplength=500,
        justify="center"
    )
    moving_title.pack()
    moving_caption.pack()

    rotAngle_label = tk.Label(master=command_frame, text="rot angle:", font=("Arial", LABEL))
    rotAngle_entry = tk.Entry(master=command_frame, width=10, justify="center")
    rotAngle_btn = tk.Button(
        master=command_frame,
        text="Move Octave!",
        bg="black",
        fg="white",
        cursor="hand2",
        command=lambda: sendNewAngle(float(rotAngle_entry.get()))
    )

    rotAngle_label.pack()
    rotAngle_entry.pack()
    rotAngle_btn.pack(pady=10)

    command_frame.pack(side=tk.LEFT, padx=25)
    moving_frame.pack(pady=20, fill=tk.X)

    window.mainloop()

# Start the GUI
if __name__ == "__main__":
    GUI()

