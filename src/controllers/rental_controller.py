from src.database.db_manager import DBManager
from datetime import datetime

class RentalController:
    def __init__(self):
        self.db = DBManager()

    def get_available_vehicles(self, vehicle_type=None):
        query = "SELECT * FROM Vehicles WHERE status = 'Available'"
        params = []
        if vehicle_type and vehicle_type != "All":
            query += " AND type = %s"
            params.append(vehicle_type)
        return self.db.fetch_all(query, tuple(params))

    def create_reservation(self, user_id, vehicle_id, start_date, end_date, insurance, equipment_ids):
        # Calculate days
        delta = (end_date - start_date).days
        if delta < 1: delta = 1
        
        # Get vehicle rate
        v_query = "SELECT daily_rate FROM Vehicles WHERE vehicle_id = %s"
        vehicle = self.db.fetch_one(v_query, (vehicle_id,))
        base_cost = float(vehicle['daily_rate']) * delta

        # Add equipment cost
        eq_cost = 0
        if equipment_ids:
            format_strings = ','.join(['%s'] * len(equipment_ids))
            e_query = f"SELECT daily_rate FROM Equipment WHERE equipment_id IN ({format_strings})"
            equipments = self.db.fetch_all(e_query, tuple(equipment_ids))
            for eq in equipments:
                eq_cost += float(eq['daily_rate']) * delta

        total_cost = base_cost + eq_cost
        if insurance:
            total_cost += (500 * delta) # Flat 500 per day for insurance

        # Insert Reservation with Pending status - awaiting Staff approval
        ins_query = """
            INSERT INTO Reservations (user_id, vehicle_id, start_date, end_date, insurance_added, total_cost, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
        """
        self.db.execute_query(ins_query, (user_id, vehicle_id, start_date, end_date, insurance, total_cost))
        
        # Do NOT change vehicle status yet - it remains 'Available' until approved
        
        return True

    def get_user_reservations(self, user_id):
        query = """
            SELECT r.*, v.brand, v.model, v.license_plate 
            FROM Reservations r 
            JOIN Vehicles v ON r.vehicle_id = v.vehicle_id 
            WHERE r.user_id = %s
            ORDER BY r.created_at DESC
        """
        return self.db.fetch_all(query, (user_id,))

    def get_pending_reservations(self):
        """Get all reservations with Pending status for Staff approval"""
        query = """
            SELECT r.*, v.brand, v.model, v.license_plate, u.username, u.full_name 
            FROM Reservations r 
            JOIN Vehicles v ON r.vehicle_id = v.vehicle_id 
            JOIN Users u ON r.user_id = u.user_id
            WHERE r.status = 'Pending'
            ORDER BY r.created_at ASC
        """
        return self.db.fetch_all(query)

    def get_all_active_rentals(self):
        query = """
            SELECT r.*, v.brand, v.model, u.username 
            FROM Reservations r 
            JOIN Vehicles v ON r.vehicle_id = v.vehicle_id 
            JOIN Users u ON r.user_id = u.user_id
            WHERE r.status = 'Active'
        """
        return self.db.fetch_all(query)
    
    def approve_reservation(self, reservation_id):
        """Approve a pending reservation - changes status to Active and marks vehicle as Rented"""
        # Get reservation details
        res = self.db.fetch_one("SELECT vehicle_id, status FROM Reservations WHERE reservation_id = %s", (reservation_id,))
        if not res:
            raise Exception("Reservation not found")
        if res['status'] != 'Pending':
            raise Exception("Can only approve Pending reservations")
        
        # Update Reservation status to Active
        self.db.execute_query("UPDATE Reservations SET status = 'Active' WHERE reservation_id = %s", (reservation_id,))
        
        # Update Vehicle status to Rented
        self.db.execute_query("UPDATE Vehicles SET status = 'Rented' WHERE vehicle_id = %s", (res['vehicle_id'],))
        
        return True
    
    def reject_reservation(self, reservation_id):
        """Reject a pending reservation - changes status to Cancelled"""
        # Get reservation details
        res = self.db.fetch_one("SELECT status FROM Reservations WHERE reservation_id = %s", (reservation_id,))
        if not res:
            raise Exception("Reservation not found")
        if res['status'] != 'Pending':
            raise Exception("Can only reject Pending reservations")
        
        # Update Reservation status to Cancelled
        self.db.execute_query("UPDATE Reservations SET status = 'Cancelled' WHERE reservation_id = %s", (reservation_id,))
        
        # Vehicle remains Available since it was never marked as Rented
        return True

    def return_vehicle(self, reservation_id, vehicle_id, condition_notes):
        # Update Reservation
        upd_res = "UPDATE Reservations SET status = 'Completed' WHERE reservation_id = %s"
        self.db.execute_query(upd_res, (reservation_id,))

        # Update Vehicle
        upd_veh = "UPDATE Vehicles SET status = 'Available' WHERE vehicle_id = %s"
        self.db.execute_query(upd_veh, (vehicle_id,))

        # Log Return
        log_query = """
            INSERT INTO Vehicle_Logs (vehicle_id, event_type, description)
            VALUES (%s, 'Return', %s)
        """
        self.db.execute_query(log_query, (vehicle_id, condition_notes))
        return True

    def get_all_vehicles(self):
        return self.db.fetch_all("SELECT * FROM Vehicles")

    def add_vehicle(self, brand, model, year, license_plate, v_type, rate):
        query = """
            INSERT INTO Vehicles (brand, model, year, license_plate, type, daily_rate, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'Available')
        """
        self.db.execute_query(query, (brand, model, year, license_plate, v_type, rate))
        return True

    def delete_vehicle(self, vehicle_id):
        query = "DELETE FROM Vehicles WHERE vehicle_id = %s"
        self.db.execute_query(query, (vehicle_id,))
        return True

    def get_equipment(self):
        return self.db.fetch_all("SELECT * FROM Equipment")

    def cancel_reservation(self, reservation_id):
        """Cancel a reservation - Members can only cancel Pending reservations"""
        # Get reservation details
        res = self.db.fetch_one("SELECT vehicle_id, status FROM Reservations WHERE reservation_id = %s", (reservation_id,))
        if not res:
            raise Exception("Reservation not found")
        if res['status'] != 'Pending':
            raise Exception("Can only cancel Pending reservations")
            
        # Update Reservation status to Cancelled
        self.db.execute_query("UPDATE Reservations SET status = 'Cancelled' WHERE reservation_id = %s", (reservation_id,))
        
        # Vehicle remains Available (it was never marked as Rented for pending reservations)
        return True

    def update_vehicle(self, vehicle_id, brand, model, year, license_plate, v_type, rate):
        query = """
            UPDATE Vehicles 
            SET brand=%s, model=%s, year=%s, license_plate=%s, type=%s, daily_rate=%s
            WHERE vehicle_id=%s
        """
        self.db.execute_query(query, (brand, model, year, license_plate, v_type, rate, vehicle_id))
        return True
        return True
