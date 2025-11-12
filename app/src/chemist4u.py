#!/usr/bin/env python3
"""
Chemist 4 U - Python CLI complete program (contextual loading messages, snappier animation)
Place this file at: Chemist4U/app/src/chemist4u.py
"""

import csv
import os
import sys
import time
import uuid

# -------------------------
# Project path configuration
# -------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

STORE_FILE = os.path.join(DATA_DIR, "store.csv")
CART_FILE = os.path.join(DATA_DIR, "cart.csv")
INSTR_FILE = os.path.join(DATA_DIR, "instructions.txt")

# -------------------------
# Models & Utilities
# -------------------------
class Medicine:
    def __init__(self, id_, name, intensity, disease, cost):
        try:
            self.id = int(id_)
        except Exception:
            self.id = 0
        self.name = name
        self.intensity = intensity
        self.disease = disease
        try:
            self.cost = float(cost)
        except Exception:
            self.cost = 0.0
        self.quantity = 1

    def to_row(self):
        return [str(self.id), self.name, self.intensity, self.disease, f"{self.cost:.2f}", str(self.quantity)]

    def print(self):
        print(f"ID: {self.id}")
        print(f"Name: {self.name}")
        print(f"Intensity: {self.intensity}")
        print(f"Disease: {self.disease}")
        print(f"Cost: ₹{self.cost:.2f}")
        print("-" * 40)


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def loading_animation(msg="Loading", frames=2, delay=0.20):
    """Short contextual loading animation.

    Args:
      msg: message to show next to the animation (string)
      frames: number of animation frames (small integer)
      delay: seconds per frame (float) -- smaller = snappier
    """
    for i in range(frames):
        clear_screen()
        dots = "." * (i + 1)
        print(f"{msg} {dots}")
        time.sleep(delay)
    clear_screen()


# -------------------------
# Ensure folders/files
# -------------------------
def ensure_folders_and_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.exists(STORE_FILE):
        sample = [
            ["id", "name", "intensity", "disease", "cost"],
            ["101", "Paracetamol", "500mg", "Fever", "20.00"],
            ["102", "Dolo", "650mg", "Fever", "30.00"],
            ["103", "Azithromycin", "250mg", "Infection", "85.00"],
            ["104", "Amoxicillin", "500mg", "Infection", "60.00"],
            ["105", "Cetirizine", "10mg", "Allergy", "30.00"],
            ["106", "Omeprazole", "20mg", "Acidity", "50.00"],
            ["107", "Multivitamin", "1tab", "General Health", "25.00"],
            ["108", "Ibuprofen", "400mg", "Pain Relief", "45.00"],
            ["109", "Cetraxal", "10mg", "Ear Infection", "120.00"],
        ]
        with open(STORE_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(sample)

    if not os.path.exists(CART_FILE):
        with open(CART_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "intensity", "disease", "cost", "quantity"])

    if not os.path.exists(INSTR_FILE):
        text = (
            "Welcome to Chemist 4 U (Python CLI Edition)\n"
            "--------------------------------------------\n"
            "1. Choose 'Place your order' to search medicines by disease.\n"
            "2. Add medicines by ID and specify quantity to your cart.\n"
            "3. View or delete items (or quantities) before billing.\n"
            "4. Payment mode: Cash on Delivery.\n"
            "5. Bill will be saved automatically in the /output folder.\n"
        )
        with open(INSTR_FILE, "w", encoding="utf-8") as f:
            f.write(text)


# -------------------------
# Store / Cart operations
# -------------------------
def load_store():
    meds = []
    if not os.path.exists(STORE_FILE):
        return meds
    with open(STORE_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("id"):
                continue
            meds.append(Medicine(row.get("id", "0"), row.get("name", ""), row.get("intensity", ""), row.get("disease", ""), row.get("cost", "0")))
    return meds


def read_cart():
    items = []
    if not os.path.exists(CART_FILE):
        return items
    with open(CART_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("id"):
                continue
            m = Medicine(row.get("id", "0"), row.get("name", ""), row.get("intensity", ""), row.get("disease", ""), row.get("cost", "0"))
            try:
                m.quantity = int(row.get("quantity", 1))
            except Exception:
                m.quantity = 1
            items.append(m)
    return items


def write_cart_from_items(items):
    with open(CART_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "intensity", "disease", "cost", "quantity"])
        for it in items:
            qty = getattr(it, "quantity", 1)
            writer.writerow([it.id, it.name, it.intensity, it.disease, f"{it.cost:.2f}", qty])


def clear_cart():
    with open(CART_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "intensity", "disease", "cost", "quantity"])


def append_to_cart(med, qty=1):
    if qty <= 0:
        return
    items = read_cart()
    for it in items:
        if it.id == med.id:
            it.quantity += qty
            break
    else:
        med.quantity = qty
        items.append(med)
    write_cart_from_items(items)


# -------------------------
# Display utilities
# -------------------------
def display_store():
    loading_animation("Loading store...")
    meds = load_store()
    clear_screen()
    print("=" * 60)
    print("\t\tCHEMIST 4 U - MEDICINE LIST")
    print("=" * 60)
    if not meds:
        print("No medicines in store.")
    else:
        for m in meds:
            m.print()
    input("Press Enter to return to menu...")


def display_cart(return_choice=False):
    """
    Show cart contents.
    If return_choice=True, prompt:
      (B)ill now, (M)ain menu, (D)elete item then return choice meaning:
        returns 'b' to bill, 'm' to return to main menu, 'd' to open delete flow (then return to caller)
    If return_choice=False, just display and wait for Enter.
    """
    loading_animation("Loading cart...")
    items = read_cart()
    clear_screen()
    print("=" * 60)
    print("\t\tYOUR CURRENT CART")
    print("=" * 60)
    if not items:
        print("Cart is empty.")
        if return_choice:
            input("\nPress Enter to return to main menu...")
            return "m"
        input("Press Enter to continue...")
        return None
    else:
        total = 0.0
        print(f"{'Item':30} {'Qty':>3}  {'Rate':>8}  {'Subtotal':>10}")
        print("-" * 60)
        for it in items:
            subtotal = it.cost * it.quantity
            print(f"{it.name:30} {it.quantity:3}  ₹{it.cost:8.2f}  ₹{subtotal:10.2f}")
            total += subtotal
        print("-" * 60)
        print(f"Total = ₹{total:.2f}")

    if not return_choice:
        input("Press Enter to continue...")
        return None

    while True:
        print("\nOptions: [B]ill now   [D]elete item from cart   [M]ain menu")
        ch = input("Choose B / D / M: ").strip().lower()
        if ch in ("b", "d", "m"):
            return ch
        print("Invalid choice. Enter B, D or M.")


def delete_from_cart():
    loading_animation("Opening cart for deletion...")
    items = read_cart()
    if not items:
        print("Cart is empty. Nothing to delete.")
        time.sleep(1)
        return

    while True:
        display_cart(return_choice=False)
        try:
            id_to_del = int(input("Enter ID of medicine to delete (0 to cancel): ").strip())
        except Exception:
            print("Invalid input.")
            time.sleep(1)
            continue
        if id_to_del == 0:
            return
        found = next((it for it in items if it.id == id_to_del), None)
        if not found:
            print("Medicine ID not found in cart.")
            time.sleep(1)
            continue

        print(f"Current quantity of {found.name}: {found.quantity}")
        try:
            qty_del = int(input(f"Enter how many to delete (1–{found.quantity}): ").strip())
        except Exception:
            print("Invalid number.")
            time.sleep(1)
            continue

        if qty_del >= found.quantity:
            items.remove(found)
            print(f"Removed all {found.name} from cart.")
        else:
            found.quantity -= qty_del
            print(f"Removed {qty_del} of {found.name}. Remaining: {found.quantity}")

        write_cart_from_items(items)
        time.sleep(1)

        if not items:
            print("Cart is now empty.")
            time.sleep(1)
            return

        more = input("Delete another item? (y/n): ").strip().lower()
        if more != "y":
            return


# -------------------------
# Order & Billing
# -------------------------
def find_by_disease(disease):
    meds = load_store()
    return [m for m in meds if (m.disease or "").strip().lower() == disease.strip().lower()]


def generate_tracking_id():
    return uuid.uuid4().hex[:10].upper()


def save_bill(name, address, phone, items, total, tracking_id):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"bill_{tracking_id}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("CHEMIST 4 U\n")
        f.write("=" * 60 + "\n")
        f.write(f"Customer: {name}\n")
        f.write(f"Address:  {address}\n")
        f.write(f"Phone:    {phone}\n")
        f.write("-" * 60 + "\n")
        f.write(f"{'Item':30} {'Qty':>3}  {'Rate':>8}  {'Subtotal':>10}\n")
        f.write("-" * 60 + "\n")
        for it in items:
            subtotal = it.cost * it.quantity
            f.write(f"{it.name:30} {it.quantity:3}  ₹{it.cost:8.2f}  ₹{subtotal:10.2f}\n")
        f.write("-" * 60 + "\n")
        f.write(f"Total: ₹{total:.2f}\n")
        f.write(f"Payment Mode: Cash on Delivery\n")
        f.write(f"Tracking ID: {tracking_id}\n")
        f.write("=" * 60 + "\n")
        f.write("Thank you for shopping with Chemist 4 U!\n")
    return filepath


def bill_process():
    loading_animation("Preparing bill...")
    items = read_cart()
    if not items:
        print("Cart is empty! Add items before billing.")
        time.sleep(1)
        return
    clear_screen()
    print("=" * 60)
    print("\t\tBILLING INFORMATION")
    print("=" * 60)
    name = input("Name: ").strip()
    address = input("Address: ").strip()
    phone = input("Phone: ").strip()
    total = sum(it.cost * it.quantity for it in items)
    tracking_id = generate_tracking_id()
    path = save_bill(name, address, phone, items, total, tracking_id)
    clear_screen()
    print("=" * 60)
    print("\t\tCHEMIST 4 U - BILL SUMMARY")
    print("=" * 60)
    for it in items:
        subtotal = it.cost * it.quantity
        print(f"{it.name} ({it.intensity}) x {it.quantity} → ₹{subtotal:.2f}")
    print("-" * 60)
    print(f"TOTAL COST: ₹{total:.2f}")
    print(f"Tracking ID: {tracking_id}")
    print(f"Bill saved at: {path}")
    print("\nPayment Mode: CASH ON DELIVERY")
    print("Thank you for shopping with Chemist 4 U!")
    clear_cart()
    input("\nPress Enter to return to menu...")


def place_order():
    loading_animation("Opening order screen...")
    while True:
        clear_screen()
        print("\t\tPLACE YOUR ORDER")
        print("-" * 60)
        disease = input("Enter disease to search (or 'back' to return): ").strip()
        if disease.lower() == "back":
            return
        results = find_by_disease(disease)
        if not results:
            print("No medicines found for that disease (case-insensitive exact match).")
            meds = load_store()
            approx = [m for m in meds if disease.strip().lower() in (m.disease or "").strip().lower()]
            if approx:
                print("\nApproximate matches based on substring in disease:")
                for m in approx:
                    m.print()
            input("Press Enter to continue...")
            continue

        print(f"\nFound {len(results)} medicine(s):")
        for m in results:
            m.print()

        try:
            id_choice = int(input("Enter ID to add to cart (0 to cancel): ").strip())
        except Exception:
            print("Invalid input.")
            time.sleep(1)
            continue
        if id_choice == 0:
            continue

        chosen = next((m for m in results if m.id == id_choice), None)
        if not chosen:
            all_meds = load_store()
            chosen = next((m for m in all_meds if m.id == id_choice), None)

        if chosen:
            try:
                qty = int(input("Enter quantity to add: ").strip())
                if qty <= 0:
                    print("Quantity must be >= 1.")
                    time.sleep(1)
                    continue
            except Exception:
                print("Invalid quantity.")
                time.sleep(1)
                continue
            append_to_cart(chosen, qty=qty)
            print(f"Added {qty} x {chosen.name} to cart!")
        else:
            print("Invalid ID. ")

        # After adding, allow user to choose next step:
        while True:
            print("\nWhat would you like to do next?")
            print("[B] Proceed to BILLING")
            print("[C] Go to CART (view/manage)")
            print("[M] Return to MAIN MENU")
            next_choice = input("Choose B / C / M: ").strip().lower()
            if next_choice == "b":
                if read_cart():
                    bill_process()
                else:
                    print("Cart is empty; cannot bill.")
                return
            elif next_choice == "c":
                cart_action = display_cart(return_choice=True)
                if cart_action == "d":
                    delete_from_cart()
                    post = input("After cart changes: [B]ill now or [M]ain menu? (B/M): ").strip().lower()
                    if post == "b" and read_cart():
                        bill_process()
                        return
                    else:
                        return
                elif cart_action == "b":
                    if read_cart():
                        bill_process()
                    else:
                        print("Cart empty; nothing to bill.")
                    return
                else:
                    return
            elif next_choice == "m":
                return
            else:
                print("Invalid choice. Enter B, C or M.")


# -------------------------
# Menu & main
# -------------------------
def instructions():
    loading_animation("Loading instructions...")
    clear_screen()
    try:
        with open(INSTR_FILE, encoding="utf-8") as f:
            print(f.read())
    except Exception:
        print("No instructions file found.")
    input("\nPress Enter to return to menu...")


def main_menu():
    ensure_folders_and_files()
    while True:
        clear_screen()
        print("CHEMIST 4 U".center(60, " "))
        print("=" * 60)
        print("1. Instructions")
        print("2. Place your order")
        print("3. View medicines")
        print("4. View cart")
        print("5. Exit")
        print("=" * 60)
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            instructions()
        elif choice == "2":
            loading_animation("Opening order...")
            place_order()
        elif choice == "3":
            loading_animation("Loading store...")
            display_store()
        elif choice == "4":
            loading_animation("Opening cart...")
            action = display_cart(return_choice=True)
            if action == "d":
                delete_from_cart()
                if read_cart():
                    if input("Bill now? (y/n): ").strip().lower() == "y":
                        bill_process()
            elif action == "b":
                if read_cart():
                    bill_process()
                else:
                    print("Cart is empty.")
                    time.sleep(1)
            else:
                pass
        elif choice == "5":
            loading_animation("Exiting...")
            clear_screen()
            print("CHEMIST 4 U".center(60))
            print("Your Health. Our Expertise.")
            print("Thank you for visiting!")
            time.sleep(1)
            sys.exit(0)
        else:
            print("Invalid choice.")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nExiting... Goodbye!")
