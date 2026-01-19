import tkinter as tk
from tkinter import ttk, messagebox
from src.controllers.admin_controller import AdminController
from src.controllers.rental_controller import RentalController
from src.utils.gui_helpers import RoundedFrame, RoundedButton, ScrollableFrame
from src.utils.image_helper import ImageHelper
import os

class AdminDashboard(tk.Frame):
    def __init__(self, parent, user, logout_callback):
        super().__init__(parent)
        self.user = user
        self.logout_callback = logout_callback
        self.controller = AdminController()
        self.rental_controller = RentalController()
        self.pack(fill="both", expand=True)
        
        self.create_layout()
        self.show_overview_view()

    def create_layout(self):
        # Top Bar
        self.top_bar = tk.Frame(self, bg="#2c3e50", height=60)
        self.top_bar.pack(side="top", fill="x")
        self.top_bar.pack_propagate(False)

        tk.Label(self.top_bar, text="Admin Dashboard", bg="#2c3e50", fg="white", font=("Segoe UI", 18, "bold")).pack(side="left", padx=20)
        
        user_info = tk.Frame(self.top_bar, bg="#2c3e50")
        user_info.pack(side="right", padx=20)
        
        tk.Label(user_info, text=f"Admin: {self.user.full_name}", bg="#2c3e50", fg="#ecf0f1", font=("Segoe UI", 12)).pack(side="left", padx=10)
        RoundedButton(user_info, width=80, height=30, corner_radius=10, bg_color="#e74c3c", fg_color="white", text="Logout", command=self.logout_callback).pack(side="left")

        # Main Container
        self.main_container = tk.Frame(self)
        self.main_container.pack(side="top", fill="both", expand=True)

        # Side Bar
        self.side_bar = tk.Frame(self.main_container, bg="#34495e", width=200)
        self.side_bar.pack(side="left", fill="y")
        self.side_bar.pack_propagate(False)

        self.create_sidebar_button("Overview", self.show_overview_view)
        self.create_sidebar_button("Fleet Management", self.show_fleet_view)
        self.create_sidebar_button("Reservations", self.show_reservations_view)
        self.create_sidebar_button("Analytics", self.show_analytics_view)
        self.create_sidebar_button("User Management", self.show_users_view)

        # Content Area
        self.content_area = tk.Frame(self.main_container, bg="white")
        self.content_area.pack(side="left", fill="both", expand=True, padx=20, pady=20)

    def create_sidebar_button(self, text, command):
        btn = RoundedButton(self.side_bar, width=180, height=40, corner_radius=10, bg_color="#34495e", fg_color="white", text=text, command=command)
        btn.pack(pady=5)

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    # --- Overview View ---
    def show_overview_view(self):
        self.clear_content()
        tk.Label(self.content_area, text="Overview", font=("Segoe UI", 20, "bold"), bg="white").pack(anchor="w", pady=(0, 20))
        
        self.overview_frame = tk.Frame(self.content_area, bg="white")
        self.overview_frame.pack(fill="both", expand=True)
        self.setup_overview_view()

    def setup_overview_view(self):
        stats = self.controller.get_dashboard_stats()
        
        container = tk.Frame(self.overview_frame, bg="white")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Stat Cards
        self.create_stat_card(container, "Total Earnings", f"₱{stats['total_earnings']:,.2f}", "#27ae60", 0, 0)
        self.create_stat_card(container, "Active Rentals", str(stats['active_rentals']), "#3498db", 0, 1)
        self.create_stat_card(container, "Total Users", str(stats['total_users']), "#f39c12", 0, 2)
        self.create_stat_card(container, "Total Vehicles", str(stats['total_vehicles']), "#8e44ad", 0, 3)

        tk.Button(self.overview_frame, text="Refresh Data", command=self.show_overview_view, bg="#34495e", fg="white", relief="flat", pady=10).pack(pady=20)

    def create_stat_card(self, parent, title, value, color, row, col):
        card = RoundedFrame(parent, width=250, height=150, corner_radius=20, bg_color=color)
        card.grid(row=row, column=col, padx=15, pady=15)
        
        tk.Label(card.inner_frame, text=title, bg=color, fg="white", font=("Segoe UI", 14)).pack(pady=(20, 10))
        tk.Label(card.inner_frame, text=value, bg=color, fg="white", font=("Segoe UI", 24, "bold")).pack()

    # --- Fleet Management View ---
    def show_fleet_view(self):
        self.clear_content()
        tk.Label(self.content_area, text="Fleet Management", font=("Segoe UI", 20, "bold"), bg="white").pack(anchor="w", pady=(0, 20))
        
        self.fleet_frame = tk.Frame(self.content_area, bg="white")
        self.fleet_frame.pack(fill="both", expand=True)
        self.setup_fleet_view()

    def setup_fleet_view(self):
        # Add Vehicle Button
        RoundedButton(self.fleet_frame, width=200, height=40, corner_radius=10, bg_color="#27ae60", fg_color="white", 
                      text="+ Add New Vehicle", command=self.show_add_vehicle_popup).pack(fill="x", padx=20, pady=10)

        self.fleet_scroll = ScrollableFrame(self.fleet_frame)
        self.fleet_scroll.pack(fill="both", expand=True, padx=10)
        self.load_fleet()

    def load_fleet(self):
        for widget in self.fleet_scroll.scrollable_frame.winfo_children():
            widget.destroy()
        
        vehicles = self.rental_controller.get_all_vehicles()
        
        columns = 3
        row = 0
        col = 0

        for v in vehicles:
            self.create_fleet_card(v, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

    def create_fleet_card(self, vehicle, row, col):
        card = RoundedFrame(self.fleet_scroll.scrollable_frame, width=280, height=240, corner_radius=15, bg_color="#f8f9fa")
        card.grid(row=row, column=col, padx=10, pady=10)

        # Image
        img_path = self.get_image_path(vehicle['model'])
        img = ImageHelper.load_resized_image(img_path, size=(150, 100))
        if img:
            lbl = tk.Label(card.inner_frame, image=img, bg="#f8f9fa")
            lbl.image = img
            lbl.pack(pady=5)

        tk.Label(card.inner_frame, text=f"{vehicle['brand']} {vehicle['model']}", font=("Segoe UI", 11, "bold"), bg="#f8f9fa").pack()
        tk.Label(card.inner_frame, text=f"Plate: {vehicle['license_plate']}", font=("Segoe UI", 9), bg="#f8f9fa", fg="#7f8c8d").pack()
        tk.Label(card.inner_frame, text=f"Rate: ₱{vehicle['daily_rate']}/day", font=("Segoe UI", 9, "bold"), fg="#27ae60", bg="#f8f9fa").pack()
        
        status_color = "green" if vehicle['status']=='Available' else "red"
        tk.Label(card.inner_frame, text=f"Status: {vehicle['status']}", font=("Segoe UI", 9, "bold"), 
                 fg=status_color, bg="#f8f9fa").pack(pady=5)

        # Edit button
        RoundedButton(card.inner_frame, width=100, height=30, corner_radius=8, bg_color="#3498db", 
                     fg_color="white", text="Edit", command=lambda v=vehicle: self.show_edit_vehicle_popup(v)).pack(pady=5)

    def show_add_vehicle_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Add New Vehicle")
        popup.geometry("400x500")
        popup.configure(bg="white")
        popup.grab_set()

        self._create_vehicle_form(popup, is_edit=False)

    def show_edit_vehicle_popup(self, vehicle):
        popup = tk.Toplevel(self)
        popup.title(f"Edit {vehicle['brand']} {vehicle['model']}")
        popup.geometry("400x500")
        popup.configure(bg="white")
        popup.grab_set()

        self._create_vehicle_form(popup, is_edit=True, vehicle=vehicle)

    def _create_vehicle_form(self, popup, is_edit, vehicle=None):
        tk.Label(popup, text="Vehicle Details", font=("Segoe UI", 14, "bold"), bg="white").pack(pady=10)
        
        form = tk.Frame(popup, bg="white")
        form.pack(padx=20, pady=10)

        entries = {}
        fields = ["Brand", "Model", "Year", "License Plate", "Type", "Daily Rate"]
        keys = ["brand", "model", "year", "license_plate", "type", "daily_rate"]

        for i, field in enumerate(fields):
            tk.Label(form, text=f"{field}:", bg="white").grid(row=i, column=0, sticky="e", pady=5)
            if field == "Type":
                entry = ttk.Combobox(form, values=["Car", "Truck", "SUV", "Van", "Motorcycle"])
            else:
                entry = tk.Entry(form)
            
            entry.grid(row=i, column=1, sticky="w", padx=10, pady=5)
            entries[keys[i]] = entry
            
            if is_edit and vehicle:
                if field == "Type":
                    entry.set(vehicle[keys[i]])
                else:
                    entry.insert(0, str(vehicle[keys[i]]))

        def save():
            data = {k: entries[k].get() for k in keys}
            if not all(data.values()):
                messagebox.showerror("Error", "All fields are required")
                return

            try:
                if is_edit:
                    self.rental_controller.update_vehicle(vehicle['vehicle_id'], data['brand'], data['model'], 
                                                        data['year'], data['license_plate'], data['type'], data['daily_rate'])
                    messagebox.showinfo("Success", "Vehicle updated successfully!")
                else:
                    self.rental_controller.add_vehicle(data['brand'], data['model'], data['year'], 
                                                     data['license_plate'], data['type'], data['daily_rate'])
                    messagebox.showinfo("Success", "Vehicle added successfully!")
                popup.destroy()
                self.load_fleet()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(popup, text="Save Vehicle", command=save, bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", pady=5).pack(fill="x", padx=20, pady=10)

        if is_edit:
            def delete():
                if messagebox.askyesno("Confirm", "Delete this vehicle?"):
                    try:
                        self.rental_controller.delete_vehicle(vehicle['vehicle_id'])
                        messagebox.showinfo("Success", "Vehicle deleted successfully!")
                        popup.destroy()
                        self.load_fleet()
                    except Exception as e:
                        messagebox.showerror("Error", str(e))
            
            tk.Button(popup, text="Delete Vehicle", command=delete, bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", pady=5).pack(fill="x", padx=20, pady=(0, 20))

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

    # --- Reservations View ---
    def show_reservations_view(self):
        self.clear_content()
        tk.Label(self.content_area, text="Reservations", font=("Segoe UI", 20, "bold"), bg="white").pack(anchor="w", pady=(0, 20))
        
        self.reservations_frame = tk.Frame(self.content_area, bg="white")
        self.reservations_frame.pack(fill="both", expand=True)
        self.setup_reservations_view()

    def setup_reservations_view(self):
        self.res_scroll = ScrollableFrame(self.reservations_frame)
        self.res_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        self.load_reservations()

    def load_reservations(self):
        for widget in self.res_scroll.scrollable_frame.winfo_children():
            widget.destroy()
        
        reservations = self.controller.get_all_reservations()
        
        row, col = 0, 0
        columns = 3
        
        for r in reservations:
            card = RoundedFrame(self.res_scroll.scrollable_frame, width=300, height=180, corner_radius=15, bg_color="#ecf0f1")
            card.grid(row=row, column=col, padx=10, pady=10)
            
            # Content
            tk.Label(card.inner_frame, text=f"Res ID: {r['reservation_id']}", bg="#ecf0f1", font=("Segoe UI", 10, "bold")).pack(anchor="w")
            tk.Label(card.inner_frame, text=f"User: {r['username']}", bg="#ecf0f1", font=("Segoe UI", 11)).pack(anchor="w")
            tk.Label(card.inner_frame, text=f"{r['brand']} {r['model']}", bg="#ecf0f1", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=5)
            tk.Label(card.inner_frame, text=f"{r['start_date']} to {r['end_date']}", bg="#ecf0f1", font=("Segoe UI", 10)).pack(anchor="w")
            tk.Label(card.inner_frame, text=f"Total: ₱{r['total_cost']:,.2f}", bg="#ecf0f1", font=("Segoe UI", 11, "bold"), fg="#27ae60").pack(anchor="w")
            
            # Status with color coding
            status_colors = {
                'Pending': '#f39c12',    # Orange
                'Active': '#27ae60',     # Green
                'Completed': '#7f8c8d',  # Gray
                'Cancelled': '#e74c3c'   # Red
            }
            status_color = status_colors.get(r['status'], '#7f8c8d')
            tk.Label(card.inner_frame, text=r['status'], bg="#ecf0f1", fg=status_color, font=("Segoe UI", 10, "bold")).pack(anchor="e")

            col += 1
            if col >= columns:
                col = 0
                row += 1

    # --- Analytics View ---
    def show_analytics_view(self):
        self.clear_content()
        tk.Label(self.content_area, text="Analytics", font=("Segoe UI", 20, "bold"), bg="white").pack(anchor="w", pady=(0, 20))
        
        self.analytics_frame = tk.Frame(self.content_area, bg="white")
        self.analytics_frame.pack(fill="both", expand=True)
        self.setup_analytics_view()

    def setup_analytics_view(self):
        tk.Label(self.analytics_frame, text="Earnings by Vehicle Type", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=20)
        
        self.chart_canvas = tk.Canvas(self.analytics_frame, bg="white", height=400)
        self.chart_canvas.pack(fill="x", padx=20)
        
        self.draw_chart()

    def draw_chart(self):
        self.chart_canvas.delete("all")
        data = self.controller.get_earnings_by_type()
        
        if not data:
            self.chart_canvas.create_text(400, 200, text="No data available", font=("Segoe UI", 14))
            return

        # Simple Bar Chart Logic
        max_val = float(max([d['earnings'] for d in data])) if data else 1.0
        c_width = 800
        c_height = 350
        bar_width = 50
        spacing = 40
        start_x = 50
        base_y = 350

        for i, item in enumerate(data):
            val = float(item['earnings'])
            bar_height = (val / max_val) * 300
            
            x0 = start_x + (i * (bar_width + spacing))
            y0 = base_y - bar_height
            x1 = x0 + bar_width
            y1 = base_y
            
            self.chart_canvas.create_rectangle(x0, y0, x1, y1, fill="#3498db", outline="")
            self.chart_canvas.create_text(x0 + bar_width/2, y1 + 15, text=item['type'])
            self.chart_canvas.create_text(x0 + bar_width/2, y0 - 10, text=f"₱{val:,.0f}")

    # --- User Management View ---
    def show_users_view(self):
        self.clear_content()
        tk.Label(self.content_area, text="User Management", font=("Segoe UI", 20, "bold"), bg="white").pack(anchor="w", pady=(0, 20))
        
        self.users_frame = tk.Frame(self.content_area, bg="white")
        self.users_frame.pack(fill="both", expand=True)
        self.setup_users_view()

    def setup_users_view(self):
        # Add User Form
        form_frame = tk.LabelFrame(self.users_frame, text="Add New User", bg="white")
        form_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(form_frame, text="Username:", bg="white").grid(row=0, column=0, padx=5, pady=5)
        self.u_username = tk.Entry(form_frame)
        self.u_username.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Password:", bg="white").grid(row=0, column=2, padx=5, pady=5)
        self.u_password = tk.Entry(form_frame, show="*")
        self.u_password.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="First Name:", bg="white").grid(row=0, column=4, padx=5, pady=5)
        self.u_fname = tk.Entry(form_frame)
        self.u_fname.grid(row=0, column=5, padx=5, pady=5)

        tk.Label(form_frame, text="Last Name:", bg="white").grid(row=1, column=0, padx=5, pady=5)
        self.u_lname = tk.Entry(form_frame)
        self.u_lname.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Role:", bg="white").grid(row=1, column=2, padx=5, pady=5)
        self.u_role = ttk.Combobox(form_frame, values=["Member", "Worker", "Receptionist", "Admin"])
        self.u_role.grid(row=1, column=3, padx=5, pady=5)

        RoundedButton(form_frame, width=100, height=30, corner_radius=10, bg_color="#27ae60", fg_color="white", text="Add User", command=self.add_user).grid(row=1, column=4, padx=10, pady=5)

        # User List
        self.user_scroll = ScrollableFrame(self.users_frame)
        self.user_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_users()

    def load_users(self):
        for widget in self.user_scroll.scrollable_frame.winfo_children():
            widget.destroy()
        
        users = self.controller.get_all_users()
        
        row, col = 0, 0
        columns = 3
        
        for u in users:
            card = RoundedFrame(self.user_scroll.scrollable_frame, width=280, height=160, corner_radius=15, bg_color="#ecf0f1")
            card.grid(row=row, column=col, padx=10, pady=10)
            
            tk.Label(card.inner_frame, text=f"ID: {u['user_id']}", bg="#ecf0f1", font=("Segoe UI", 9)).pack(anchor="w")
            tk.Label(card.inner_frame, text=u['username'], bg="#ecf0f1", font=("Segoe UI", 12, "bold")).pack(anchor="w")
            tk.Label(card.inner_frame, text=f"{u['first_name']} {u['last_name']}", bg="#ecf0f1", font=("Segoe UI", 11)).pack(anchor="w")
            tk.Label(card.inner_frame, text=f"Role: {u['role']}", bg="#ecf0f1", fg="#2980b9", font=("Segoe UI", 10)).pack(anchor="w", pady=5)
            
            RoundedButton(card.inner_frame, width=80, height=30, corner_radius=10, bg_color="#e74c3c", fg_color="white", 
                          text="Delete", command=lambda uid=u['user_id']: self.delete_user(uid)).pack(anchor="e", pady=5)

            col += 1
            if col >= columns:
                col = 0
                row += 1

    def add_user(self):
        try:
            if self.controller.add_user(
                self.u_username.get(), self.u_password.get(), 
                self.u_fname.get(), self.u_lname.get(), self.u_role.get()
            ):
                messagebox.showinfo("Success", "User added")
                self.load_users()
                # Clear
                for e in [self.u_username, self.u_password, self.u_fname, self.u_lname]:
                    e.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Failed to add user")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_user(self, user_id):
        if not messagebox.askyesno("Confirm", "Delete this user?"):
            return

        if self.controller.delete_user(user_id):
            messagebox.showinfo("Success", "User deleted")
            self.load_users()
