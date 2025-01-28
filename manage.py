import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, timedelta
import uuid

class HotelManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Luxury Hotel Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")

        # Database Setup
        self.conn = sqlite3.connect("hotel_management.db")
        self.create_tables()

        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", font=("Arial", 12), background="#f0f0f0")
        self.style.configure("TButton", font=("Arial", 12))
        self.style.configure("Treeview", 
            background="#ffffff", 
            foreground="black", 
            rowheight=25, 
            fieldbackground="#ffffff"
        )

        # Main Frame
        self.main_frame = tk.Frame(root, bg="#f0f0f0")
        self.main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Create Sections
        self.create_room_section()
        self.create_booking_section()
        self.create_guest_section()

    def create_tables(self):
        """Create necessary database tables"""
        cursor = self.conn.cursor()
        
        # Rooms Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_number TEXT PRIMARY KEY,
                room_type TEXT,
                price REAL,
                status TEXT DEFAULT 'Available'
            )
        """)

        # Guests Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS guests (
                guest_id TEXT PRIMARY KEY,
                name TEXT,
                contact TEXT,
                email TEXT
            )
        """)

        # Bookings Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id TEXT PRIMARY KEY,
                guest_id TEXT,
                room_number TEXT,
                check_in DATE,
                check_out DATE,
                total_price REAL,
                FOREIGN KEY(guest_id) REFERENCES guests(guest_id),
                FOREIGN KEY(room_number) REFERENCES rooms(room_number)
            )
        """)

        self.conn.commit()

    def create_room_section(self):
        """Create Room Management Section"""
        room_frame = tk.LabelFrame(self.main_frame, text="Room Management", font=("Arial", 14), bg="#f0f0f0")
        room_frame.pack(fill=tk.X, pady=10)

        # Room Number
        tk.Label(room_frame, text="Room Number:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5)
        self.room_number = tk.Entry(room_frame)
        self.room_number.grid(row=0, column=1, padx=5, pady=5)

        # Room Type
        tk.Label(room_frame, text="Room Type:", bg="#f0f0f0").grid(row=0, column=2, padx=5, pady=5)
        self.room_type = ttk.Combobox(room_frame, values=["Standard", "Deluxe", "Suite"])
        self.room_type.grid(row=0, column=3, padx=5, pady=5)

        # Price
        tk.Label(room_frame, text="Price:", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=5)
        self.room_price = tk.Entry(room_frame)
        self.room_price.grid(row=1, column=1, padx=5, pady=5)

        # Add Room Button
        tk.Button(room_frame, text="Add Room", command=self.add_room, bg="#4CAF50", fg="white").grid(row=2, column=0, columnspan=4, pady=10)

        # Room List
        self.room_tree = ttk.Treeview(room_frame, columns=("Number", "Type", "Price", "Status"), show="headings")
        self.room_tree.grid(row=3, column=0, columnspan=4, padx=5, pady=5)
        
        for col in ("Number", "Type", "Price", "Status"):
            self.room_tree.heading(col, text=col)
            self.room_tree.column(col, width=150, anchor="center")

        self.load_rooms()

    def create_booking_section(self):
        """Create Booking Management Section"""
        booking_frame = tk.LabelFrame(self.main_frame, text="Booking Management", font=("Arial", 14), bg="#f0f0f0")
        booking_frame.pack(fill=tk.X, pady=10)

        # Guest Name
        tk.Label(booking_frame, text="Guest Name:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5)
        self.guest_name = tk.Entry(booking_frame)
        self.guest_name.grid(row=0, column=1, padx=5, pady=5)

        # Room Selection
        tk.Label(booking_frame, text="Select Room:", bg="#f0f0f0").grid(row=0, column=2, padx=5, pady=5)
        self.available_rooms = ttk.Combobox(booking_frame)
        self.available_rooms.grid(row=0, column=3, padx=5, pady=5)

        # Check-in and Check-out
        tk.Label(booking_frame, text="Check-in Date:", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=5)
        self.check_in_date = tk.Entry(booking_frame)
        self.check_in_date.grid(row=1, column=1, padx=5, pady=5)
        self.check_in_date.insert(0, "YYYY-MM-DD")

        tk.Label(booking_frame, text="Check-out Date:", bg="#f0f0f0").grid(row=1, column=2, padx=5, pady=5)
        self.check_out_date = tk.Entry(booking_frame)
        self.check_out_date.grid(row=1, column=3, padx=5, pady=5)
        self.check_out_date.insert(0, "YYYY-MM-DD")

        # Book Room Button
        tk.Button(booking_frame, text="Book Room", command=self.book_room, bg="#2196F3", fg="white").grid(row=2, column=0, columnspan=4, pady=10)

        # Bookings Tree
        self.booking_tree = ttk.Treeview(booking_frame, columns=("Guest", "Room", "Check-in", "Check-out"), show="headings")
        self.booking_tree.grid(row=3, column=0, columnspan=4, padx=5, pady=5)
        
        for col in ("Guest", "Room", "Check-in", "Check-out"):
            self.booking_tree.heading(col, text=col)
            self.booking_tree.column(col, width=200, anchor="center")

        self.load_bookings()
        self.update_available_rooms()

    def create_guest_section(self):
        """Create Guest Management Section"""
        guest_frame = tk.LabelFrame(self.main_frame, text="Guest Management", font=("Arial", 14), bg="#f0f0f0")
        guest_frame.pack(fill=tk.X, pady=10)

        # Contact and Email
        tk.Label(guest_frame, text="Contact Number:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5)
        self.guest_contact = tk.Entry(guest_frame)
        self.guest_contact.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(guest_frame, text="Email:", bg="#f0f0f0").grid(row=0, column=2, padx=5, pady=5)
        self.guest_email = tk.Entry(guest_frame)
        self.guest_email.grid(row=0, column=3, padx=5, pady=5)

        # Guest List
        self.guest_tree = ttk.Treeview(guest_frame, columns=("Name", "Contact", "Email"), show="headings")
        self.guest_tree.grid(row=1, column=0, columnspan=4, padx=5, pady=5)
        
        for col in ("Name", "Contact", "Email"):
            self.guest_tree.heading(col, text=col)
            self.guest_tree.column(col, width=250, anchor="center")

        self.load_guests()

    def add_room(self):
        """Add a new room to the system"""
        room_number = self.room_number.get()
        room_type = self.room_type.get()
        price = self.room_price.get()

        if not all([room_number, room_type, price]):
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO rooms VALUES (?, ?, ?, ?)", 
                           (room_number, room_type, float(price), "Available"))
            self.conn.commit()
            self.load_rooms()
            self.update_available_rooms()
            messagebox.showinfo("Success", "Room added successfully")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Room number already exists")

    def book_room(self):
        """Book a room for a guest"""
        guest_name = self.guest_name.get()
        room_number = self.available_rooms.get()
        check_in = self.check_in_date.get()
        check_out = self.check_out_date.get()

        if not all([guest_name, room_number, check_in, check_out]):
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            guest_id = str(uuid.uuid4())
            booking_id = str(uuid.uuid4())
            cursor = self.conn.cursor()

            # Insert Guest
            cursor.execute("INSERT INTO guests VALUES (?, ?, ?, ?)", 
                           (guest_id, guest_name, 
                            self.guest_contact.get(), 
                            self.guest_email.get()))

            # Calculate total price
            cursor.execute("SELECT price FROM rooms WHERE room_number = ?", (room_number,))
            room_price = cursor.fetchone()[0]
            nights = (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days
            total_price = room_price * nights

            # Insert Booking
            cursor.execute("INSERT INTO bookings VALUES (?, ?, ?, ?, ?, ?)", 
                           (booking_id, guest_id, room_number, check_in, check_out, total_price))

            # Update Room Status
            cursor.execute("UPDATE rooms SET status = 'Booked' WHERE room_number = ?", (room_number,))

            self.conn.commit()
            self.load_bookings()
            self.load_rooms()
            self.update_available_rooms()
            messagebox.showinfo("Success", f"Booking Successful. Total Price: ${total_price}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_rooms(self):
        """Load rooms into room treeview"""
        self.room_tree.delete(*self.room_tree.get_children())
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM rooms")
        for row in cursor.fetchall():
            self.room_tree.insert("", "end", values=row)

    def load_bookings(self):
        """Load bookings into booking treeview"""
        self.booking_tree.delete(*self.booking_tree.get_children())
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT g.name, b.room_number, b.check_in, b.check_out 
            FROM bookings b 
            JOIN guests g ON b.guest_id = g.guest_id
        """)
        for row in cursor.fetchall():
            self.booking_tree.insert("", "end", values=row)

    def load_guests(self):
        """Load guests into guest treeview"""
        self.guest_tree.delete(*self.guest_tree.get_children())
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, contact, email FROM guests")
        for row in cursor.fetchall():
            self.guest_tree.insert("", "end", values=row)

    def update_available_rooms(self):
        """Update available rooms dropdown"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT room_number FROM rooms WHERE status = 'Available'")
        available_rooms = [row[0] for row in cursor.fetchall()]
        self.available_rooms['values'] = available_rooms

    def __del__(self):
        """Close database connection"""
        self.conn.close()

def main():
    root = tk.Tk()
    app = HotelManagementSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()