import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from src.controllers.rental_controller import RentalController
from datetime import datetime
from src.utils.image_helper import ImageHelper
from src.utils.gui_helpers import RoundedFrame, RoundedButton, ScrollableFrame
import os

class MemberDashboard(tk.Frame):
    def __init__(self, parent, user, logout_callback):
        super().__init__(parent)
        self.user = user
        self.logout_callback = logout_callback
        self.rental_controller = RentalController()
        self.pack(fill="both", expand=True)
        
        self.create_layout()
        self.show_rent_view()

    def create_layout(self):
        # Top Bar
        self.top_bar = tk.Frame(self, bg="#2c3e50", height=60)
        self.top_bar.pack(side="top", fill="x")
        self.top_bar.pack_propagate(False)

        tk.Label(self.top_bar, text="Vehicle Rental System", bg="#2c3e50", fg="white", font=("Segoe UI", 18, "bold")).pack(side="left", padx=20)
        
        user_info = tk.Frame(self.top_bar, bg="#2c3e50")
        user_info.pack(side="right", padx=20)
        
        tk.Label(user_info, text=f"Welcome, {self.user.full_name}", bg="#2c3e50", fg="#ecf0f1", font=("Segoe UI", 12)).pack(side="left", padx=10)
        RoundedButton(user_info, width=80, height=30, corner_radius=10, bg_color="#e74c3c", fg_color="white", text="Logout", command=self.logout_callback).pack(side="left")

        # Main Container
        self.main_container = tk.Frame(self)
        self.main_container.pack(side="top", fill="both", expand=True)

        # Side Bar
        self.side_bar = tk.Frame(self.main_container, bg="#34495e", width=200)
        self.side_bar.pack(side="left", fill="y")
        self.side_bar.pack_propagate(False)

        self.create_sidebar_button("Rent a Vehicle", self.show_rent_view)
        self.create_sidebar_button("My Reservations", self.show_history_view)

        # Content Area
        self.content_area = tk.Frame(self.main_container, bg="white")
        self.content_area.pack(side="left", fill="both", expand=True, padx=20, pady=20)

    def create_sidebar_button(self, text, command):
        btn = RoundedButton(self.side_bar, width=180, height=40, corner_radius=10, bg_color="#34495e", fg_color="white", text=text, command=command)
        btn.pack(pady=5)

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def show_rent_view(self):
        self.clear_content()
        tk.Label(self.content_area, text="Rent a Vehicle", font=("Segoe UI", 20, "bold"), bg="white").pack(anchor="w", pady=(0, 20))
        
        self.rent_frame = tk.Frame(self.content_area, bg="white")
        self.rent_frame.pack(fill="both", expand=True)
        self.setup_rent_view()

    def show_history_view(self):
        self.clear_content()
        tk.Label(self.content_area, text="My Reservations", font=("Segoe UI", 20, "bold"), bg="white").pack(anchor="w", pady=(0, 20))
        
        self.history_frame = tk.Frame(self.content_area, bg="white")
        self.history_frame.pack(fill="both", expand=True)
        self.setup_history_view()

    def setup_rent_view(self):
        # Filters
        filter_frame = tk.Frame(self.rent_frame, bg="white")
        filter_frame.pack(fill="x", pady=10)
        
        tk.Label(filter_frame, text="Type:", bg="white", font=("Segoe UI", 10)).pack(side="left", padx=5)
        self.type_var = tk.StringVar(value="All")
        type_cb = ttk.Combobox(filter_frame, textvariable=self.type_var, values=["All", "Car", "Truck", "SUV", "Van", "Motorcycle"])
        type_cb.pack(side="left", padx=5)
        RoundedButton(filter_frame, width=80, height=30, corner_radius=10, bg_color="#3498db", fg_color="white", text="Search", command=self.load_vehicles).pack(side="left", padx=10)

        # Vehicle Grid (Scrollable)
        self.rent_scroll = ScrollableFrame(self.rent_frame)
        self.rent_scroll.pack(fill="both", expand=True, padx=10)

        self.load_vehicles()

    def load_vehicles(self):
        # Clear existing
        for widget in self.rent_scroll.scrollable_frame.winfo_children():
            widget.destroy()
        
        vehicles = self.rental_controller.get_available_vehicles(self.type_var.get())
        
        # Grid settings
        columns = 4  # Increased columns for better density
        row = 0
        col = 0

        for v in vehicles:
            self.create_vehicle_card(v, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

    def create_vehicle_card(self, vehicle, row, col):
        # Card Frame
        card = RoundedFrame(self.rent_scroll.scrollable_frame, width=250, height=220, corner_radius=15, bg_color="#f8f9fa")
        card.grid(row=row, column=col, padx=10, pady=10)
        
        # Image
        img_path = self.get_image_path(vehicle['model'])
        img = ImageHelper.load_resized_image(img_path, size=(150, 100))
        
        if img:
            img_label = tk.Label(card.inner_frame, image=img, bg="#f8f9fa")
            img_label.image = img # Keep reference
            img_label.pack(pady=5)
            img_label.bind("<Button-1>", lambda e, v=vehicle: self.show_rent_popup(v))

        # Info
        tk.Label(card.inner_frame, text=f"{vehicle['brand']} {vehicle['model']}", font=("Segoe UI", 11, "bold"), bg="#f8f9fa").pack()
        tk.Label(card.inner_frame, text=f"{vehicle['year']} - {vehicle['type']}", font=("Segoe UI", 9), bg="#f8f9fa", fg="#7f8c8d").pack()
        tk.Label(card.inner_frame, text=f"₱{vehicle['daily_rate']}/day", font=("Segoe UI", 10, "bold"), bg="#f8f9fa", fg="#27ae60").pack(pady=5)

        # Click Event on Card
        card.bind("<Button-1>", lambda e, v=vehicle: self.show_rent_popup(v))
        card.inner_frame.bind("<Button-1>", lambda e, v=vehicle: self.show_rent_popup(v))
        for child in card.inner_frame.winfo_children():
            child.bind("<Button-1>", lambda e, v=vehicle: self.show_rent_popup(v))

    def get_image_path(self, model):
        base_path = os.path.join(os.path.dirname(__file__), "..", "img", "vehicles")
        clean_model = model.replace(" ", "")
        candidates = [
            f"{model}.jpg", f"{model}.png",
            f"{model.lower()}.jpg", f"{model.lower()}.png",
            f"{clean_model}.jpg", f"{clean_model}.png",
            f"{clean_model.lower()}.jpg", f"{clean_model.lower()}.png"
        ]
        for c in candidates:
            p = os.path.join(base_path, c)
            if os.path.exists(p):
                return p
        return ""

    def show_rent_popup(self, vehicle):
        popup = tk.Toplevel(self)
        popup.title(f"Rent {vehicle['brand']} {vehicle['model']}")
        popup.geometry("400x600")
        popup.configure(bg="white")
        popup.grab_set() # Modal

        # Image
        img_path = self.get_image_path(vehicle['model'])
        img = ImageHelper.load_resized_image(img_path, size=(300, 200))
        if img:
            lbl = tk.Label(popup, image=img, bg="white")
            lbl.image = img
            lbl.pack(pady=10)

        # Details
        tk.Label(popup, text=f"{vehicle['brand']} {vehicle['model']}", font=("Segoe UI", 16, "bold"), bg="white").pack()
        tk.Label(popup, text=f"Rate: ₱{vehicle['daily_rate']}/day", font=("Segoe UI", 12), fg="#27ae60", bg="white").pack()

        # Form
        form_frame = tk.Frame(popup, bg="white", padx=20)
        form_frame.pack(fill="both", expand=True, pady=10)

        tk.Label(form_frame, text="Start Date:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        start_date = DateEntry(form_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        start_date.grid(row=0, column=1, sticky="w", pady=5)

        tk.Label(form_frame, text="End Date:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        end_date = DateEntry(form_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        end_date.grid(row=1, column=1, sticky="w", pady=5)

        insurance_var = tk.BooleanVar()
        tk.Checkbutton(form_frame, text="Add Insurance (500/day)", variable=insurance_var, bg="white").grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        # Equipment
        tk.Label(form_frame, text="Add Equipment:", bg="white", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 5))
        
        equipment_vars = {}
        equipments = self.rental_controller.get_equipment()
        r = 4
        for eq in equipments:
            var = tk.BooleanVar()
            equipment_vars[eq['equipment_id']] = var
            tk.Checkbutton(form_frame, text=f"{eq['name']} (+{eq['daily_rate']})", variable=var, bg="white").grid(row=r, column=0, columnspan=2, sticky="w")
            r += 1

        # Action Button
        def confirm_rent():
            eq_ids = [eid for eid, var in equipment_vars.items() if var.get()]
            try:
                success = self.rental_controller.create_reservation(
                    self.user.user_id,
                    vehicle['vehicle_id'],
                    start_date.get_date(),
                    end_date.get_date(),
                    insurance_var.get(),
                    eq_ids
                )
                if success:
                    messagebox.showinfo("Success", "Reservation created! Waiting for staff approval.")
                    popup.destroy()
                    self.load_vehicles()
                else:
                    messagebox.showerror("Error", "Failed to create reservation.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(popup, text="Confirm Reservation", command=confirm_rent, bg="#27ae60", fg="white", font=("Segoe UI", 12, "bold"), relief="flat", pady=10).pack(fill="x", padx=20, pady=20)

    def setup_history_view(self):
        self.history_scroll = ScrollableFrame(self.history_frame)
        self.history_scroll.pack(fill="both", expand=True, padx=10)

        # Load Reservations
        reservations = self.rental_controller.get_user_reservations(self.user.user_id)
        
        columns = 3
        row = 0
        col = 0

        for res in reservations:
            self.create_reservation_card(self.history_scroll.scrollable_frame, res, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

    def create_reservation_card(self, parent, res, row, col):
        card = RoundedFrame(parent, width=280, height=200, corner_radius=15, bg_color="#f8f9fa")
        card.grid(row=row, column=col, padx=10, pady=10)

        # Image
        img_path = self.get_image_path(res['model'])
        img = ImageHelper.load_resized_image(img_path, size=(150, 100))
        if img:
            lbl = tk.Label(card.inner_frame, image=img, bg="#f8f9fa")
            lbl.image = img
            lbl.pack(pady=5)

        tk.Label(card.inner_frame, text=f"{res['brand']} {res['model']}", font=("Segoe UI", 11, "bold"), bg="#f8f9fa").pack()
        
        # Status with color coding
        status_colors = {
            'Pending': '#f39c12',    # Orange
            'Active': '#27ae60',     # Green
            'Completed': '#7f8c8d',  # Gray
            'Cancelled': '#e74c3c'   # Red
        }
        status_color = status_colors.get(res['status'], 'black')
        tk.Label(card.inner_frame, text=f"Status: {res['status']}", font=("Segoe UI", 9, "bold"), 
                 fg=status_color, bg="#f8f9fa").pack()
        tk.Label(card.inner_frame, text=f"{res['start_date']} to {res['end_date']}", font=("Segoe UI", 9), bg="#f8f9fa").pack()

        # Click to view details/cancel
        card.bind("<Button-1>", lambda e, r=res: self.show_reservation_popup(r))
        card.inner_frame.bind("<Button-1>", lambda e, r=res: self.show_reservation_popup(r))
        for child in card.inner_frame.winfo_children():
            child.bind("<Button-1>", lambda e, r=res: self.show_reservation_popup(r))

    def show_reservation_popup(self, res):
        popup = tk.Toplevel(self)
        popup.title(f"Reservation #{res['reservation_id']}")
        popup.geometry("350x400")
        popup.configure(bg="white")
        popup.grab_set()

        tk.Label(popup, text="Reservation Details", font=("Segoe UI", 14, "bold"), bg="white").pack(pady=10)
        
        details = f"""
        Vehicle: {res['brand']} {res['model']}
        Dates: {res['start_date']} - {res['end_date']}
        Total Cost: ₱{res['total_cost']}
        Status: {res['status']}
        """
        tk.Label(popup, text=details, justify="left", bg="white", font=("Segoe UI", 10)).pack(pady=10)

        # Only allow cancellation of Pending reservations
        if res['status'] == 'Pending':
            def cancel():
                if messagebox.askyesno("Confirm", "Are you sure you want to cancel this reservation?"):
                    try:
                        self.rental_controller.cancel_reservation(res['reservation_id'])
                        messagebox.showinfo("Success", "Reservation cancelled.")
                        popup.destroy()
                        self.show_history_view() # Refresh
                    except Exception as e:
                        messagebox.showerror("Error", str(e))

            tk.Button(popup, text="Cancel Reservation", command=cancel, bg="#e74c3c", fg="white", 
                     font=("Segoe UI", 10, "bold"), relief="flat", pady=5).pack(pady=20)
        elif res['status'] == 'Active':
            tk.Label(popup, text="Contact staff to return the vehicle", bg="white", fg="#7f8c8d", 
                    font=("Segoe UI", 9, "italic")).pack(pady=10)
        elif res['status'] == 'Completed':
            tk.Label(popup, text="This rental has been completed", bg="white", fg="#27ae60", 
                    font=("Segoe UI", 9, "italic")).pack(pady=10)
        elif res['status'] == 'Cancelled':
            tk.Label(popup, text="This reservation was cancelled", bg="white", fg="#e74c3c", 
                    font=("Segoe UI", 9, "italic")).pack(pady=10)




