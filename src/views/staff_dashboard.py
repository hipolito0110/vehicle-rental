import tkinter as tk
from tkinter import ttk, messagebox
from src.controllers.rental_controller import RentalController
from src.utils.image_helper import ImageHelper
from src.utils.gui_helpers import RoundedFrame, RoundedButton, ScrollableFrame
import os

class StaffDashboard(tk.Frame):
    def __init__(self, parent, user, logout_callback):
        super().__init__(parent)
        self.user = user
        self.logout_callback = logout_callback
        self.rental_controller = RentalController()
        self.pack(fill="both", expand=True)
        
        self.create_layout()
        self.show_pending_view()  # Show pending approvals by default

    def create_layout(self):
        # Top Bar
        self.top_bar = tk.Frame(self, bg="#2c3e50", height=60)
        self.top_bar.pack(side="top", fill="x")
        self.top_bar.pack_propagate(False)

        role_title = "Receptionist" if self.user.role == "Receptionist" else "Worker"
        tk.Label(self.top_bar, text=f"{role_title} Dashboard", bg="#2c3e50", fg="white", font=("Segoe UI", 18, "bold")).pack(side="left", padx=20)
        
        user_info = tk.Frame(self.top_bar, bg="#2c3e50")
        user_info.pack(side="right", padx=20)
        
        tk.Label(user_info, text=f"User: {self.user.full_name}", bg="#2c3e50", fg="#ecf0f1", font=("Segoe UI", 12)).pack(side="left", padx=10)
        RoundedButton(user_info, width=80, height=30, corner_radius=10, bg_color="#e74c3c", fg_color="white", text="Logout", command=self.logout_callback).pack(side="left")

        # Main Container
        self.main_container = tk.Frame(self)
        self.main_container.pack(side="top", fill="both", expand=True)

        # Side Bar
        self.side_bar = tk.Frame(self.main_container, bg="#34495e", width=200)
        self.side_bar.pack(side="left", fill="y")
        self.side_bar.pack_propagate(False)

        self.create_sidebar_button("Pending Approvals", self.show_pending_view)
        self.create_sidebar_button("Process Returns", self.show_returns_view)

        # Content Area
        self.content_area = tk.Frame(self.main_container, bg="white")
        self.content_area.pack(side="left", fill="both", expand=True, padx=20, pady=20)

    def create_sidebar_button(self, text, command):
        btn = RoundedButton(self.side_bar, width=180, height=40, corner_radius=10, bg_color="#34495e", fg_color="white", text=text, command=command)
        btn.pack(pady=5)

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def show_pending_view(self):
        self.clear_content()
        tk.Label(self.content_area, text="Pending Approvals", font=("Segoe UI", 20, "bold"), bg="white").pack(anchor="w", pady=(0, 20))
        
        self.pending_frame = tk.Frame(self.content_area, bg="white")
        self.pending_frame.pack(fill="both", expand=True)
        self.setup_pending_view()

    def setup_pending_view(self):
        self.pend_scroll = ScrollableFrame(self.pending_frame)
        self.pend_scroll.pack(fill="both", expand=True, padx=10)
        self.load_pending()

    def load_pending(self):
        for widget in self.pend_scroll.scrollable_frame.winfo_children():
            widget.destroy()
        
        pending = self.rental_controller.get_pending_reservations()
        
        if not pending:
            tk.Label(self.pend_scroll.scrollable_frame, text="No pending reservations", 
                    font=("Segoe UI", 14), fg="#7f8c8d").pack(pady=50)
            return
        
        columns = 3
        row = 0
        col = 0

        for p in pending:
            self.create_pending_card(p, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

    def create_pending_card(self, pending, row, col):
        card = RoundedFrame(self.pend_scroll.scrollable_frame, width=280, height=260, corner_radius=15, bg_color="#fff3cd")
        card.grid(row=row, column=col, padx=10, pady=10)

        # Header
        tk.Label(card.inner_frame, text=f"Reservation #{pending['reservation_id']}", 
                font=("Segoe UI", 10, "bold"), bg="#fff3cd", fg="#856404").pack(anchor="w", pady=(5,0))
        
        # Customer info
        tk.Label(card.inner_frame, text=f"Customer: {pending['full_name']}", 
                font=("Segoe UI", 10), bg="#fff3cd").pack(anchor="w")
        tk.Label(card.inner_frame, text=f"({pending['username']})", 
                font=("Segoe UI", 8), bg="#fff3cd", fg="#7f8c8d").pack(anchor="w")
        
        # Vehicle info
        tk.Label(card.inner_frame, text=f"{pending['brand']} {pending['model']}", 
                font=("Segoe UI", 11, "bold"), bg="#fff3cd").pack(anchor="w", pady=(10,0))
        tk.Label(card.inner_frame, text=f"Plate: {pending['license_plate']}", 
                font=("Segoe UI", 9), bg="#fff3cd").pack(anchor="w")
        
        # Dates
        tk.Label(card.inner_frame, text=f"{pending['start_date']} to {pending['end_date']}", 
                font=("Segoe UI", 9), bg="#fff3cd").pack(anchor="w", pady=(5,0))
        tk.Label(card.inner_frame, text=f"Cost: ₱{pending['total_cost']:,.2f}", 
                font=("Segoe UI", 10, "bold"), fg="#27ae60", bg="#fff3cd").pack(anchor="w", pady=(5,10))
        
        # Action buttons
        btn_frame = tk.Frame(card.inner_frame, bg="#fff3cd")
        btn_frame.pack(fill="x", pady=(5,0))
        
        def approve():
            try:
                self.rental_controller.approve_reservation(pending['reservation_id'])
                messagebox.showinfo("Success", f"Reservation #{pending['reservation_id']} approved!")
                self.load_pending()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        def reject():
            if messagebox.askyesno("Confirm", f"Reject reservation #{pending['reservation_id']}?"):
                try:
                    self.rental_controller.reject_reservation(pending['reservation_id'])
                    messagebox.showinfo("Success", f"Reservation #{pending['reservation_id']} rejected.")
                    self.load_pending()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
        
        RoundedButton(btn_frame, width=110, height=30, corner_radius=8, bg_color="#27ae60", 
                     fg_color="white", text="Approve", command=approve).pack(side="left", padx=2)
        RoundedButton(btn_frame, width=110, height=30, corner_radius=8, bg_color="#e74c3c", 
                     fg_color="white", text="Reject", command=reject).pack(side="left", padx=2)

    def show_returns_view(self):
        self.clear_content()
        tk.Label(self.content_area, text="Process Returns", font=("Segoe UI", 20, "bold"), bg="white").pack(anchor="w", pady=(0, 20))
        
        self.returns_frame = tk.Frame(self.content_area, bg="white")
        self.returns_frame.pack(fill="both", expand=True)
        self.setup_returns_view()

    def show_fleet_view(self):
        self.clear_content()
        tk.Label(self.content_area, text="Manage Fleet", font=("Segoe UI", 20, "bold"), bg="white").pack(anchor="w", pady=(0, 20))
        
        self.fleet_frame = tk.Frame(self.content_area, bg="white")
        self.fleet_frame.pack(fill="both", expand=True)
        self.setup_fleet_view()

    def setup_returns_view(self):
        self.ret_scroll = ScrollableFrame(self.returns_frame)
        self.ret_scroll.pack(fill="both", expand=True, padx=10)
        self.load_rentals()

    def load_rentals(self):
        for widget in self.ret_scroll.scrollable_frame.winfo_children():
            widget.destroy()
        
        rentals = self.rental_controller.get_all_active_rentals()
        
        columns = 3
        row = 0
        col = 0

        for r in rentals:
            self.create_rental_card(r, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

    def create_rental_card(self, rental, row, col):
        card = RoundedFrame(self.ret_scroll.scrollable_frame, width=280, height=220, corner_radius=15, bg_color="#f8f9fa")
        card.grid(row=row, column=col, padx=10, pady=10)

        # Image
        img_path = self.get_image_path(rental['model'])
        img = ImageHelper.load_resized_image(img_path, size=(150, 100))
        if img:
            lbl = tk.Label(card.inner_frame, image=img, bg="#f8f9fa")
            lbl.image = img
            lbl.pack(pady=5)

        tk.Label(card.inner_frame, text=f"{rental['brand']} {rental['model']}", font=("Segoe UI", 11, "bold"), bg="#f8f9fa").pack()
        tk.Label(card.inner_frame, text=f"Rented by: {rental['username']}", font=("Segoe UI", 9), bg="#f8f9fa").pack()
        tk.Label(card.inner_frame, text=f"Due: {rental['end_date']}", font=("Segoe UI", 9, "bold"), fg="#e74c3c", bg="#f8f9fa").pack()

        # Click
        card.bind("<Button-1>", lambda e, r=rental: self.show_return_popup(r))
        card.inner_frame.bind("<Button-1>", lambda e, r=rental: self.show_return_popup(r))
        for child in card.inner_frame.winfo_children():
            child.bind("<Button-1>", lambda e, r=rental: self.show_return_popup(r))

    def show_return_popup(self, rental):
        popup = tk.Toplevel(self)
        popup.title(f"Return Vehicle - {rental['brand']} {rental['model']}")
        popup.geometry("400x500")
        popup.configure(bg="white")
        popup.grab_set()

        tk.Label(popup, text="Process Return", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=10)
        
        info = f"""
        Reservation ID: {rental['reservation_id']}
        Customer: {rental['username']}
        Vehicle: {rental['brand']} {rental['model']}
        Due Date: {rental['end_date']}
        """
        tk.Label(popup, text=info, justify="left", bg="white", font=("Segoe UI", 10)).pack(pady=10)

        tk.Label(popup, text="Condition Notes:", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=20)
        notes_entry = tk.Entry(popup, width=40)
        notes_entry.pack(padx=20, pady=5)

        def confirm():
            notes = notes_entry.get() or "Standard return"
            try:
                self.rental_controller.return_vehicle(rental['reservation_id'], rental['vehicle_id'], notes)
                messagebox.showinfo("Success", "Vehicle returned successfully")
                popup.destroy()
                self.load_rentals()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(popup, text="Confirm Return", command=confirm, bg="#f39c12", fg="white", font=("Segoe UI", 12, "bold"), relief="flat", pady=10).pack(fill="x", padx=20, pady=20)

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






