import os
import sqlite3
import csv
import tkinter as tk
from tkinter import filedialog

class SQLTableEditor:
    def __init__(self, base_dir="projects"):
        self.base_dir = base_dir
        self.project_name = None
        self.db_path = None
        self.conn = None

    def run(self):
        self.choose_project()
        if input("\n📥 Do you want to import a CSV as a table? (yes/no): ").strip().lower() == "yes":
            self.import_csv_to_sqlite()
        while True:
            self.show_tables()
            choice = input("\nWhat would you like to do? (edit/add/delete/exit): ").strip().lower()
            if choice == "edit":
                self.edit_table()
            elif choice == "add":
                self.add_table_row()
            elif choice == "delete":
                self.delete_table_row()
            elif choice == "exit":
                break
            else:
                print("❌ Invalid choice.")

    def choose_project(self):
        print("\n📂 Available Projects:")
        projects = [d for d in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, d))]
        for p in projects:
            print(f"- {p}")
        while True:
            name = input("\nSelect a project: ").strip()
            if name in projects:
                self.project_name = name
                break
            print("❌ Project not found.")
        self.db_path = os.path.join(self.base_dir, self.project_name, f"{self.project_name}.sqlite")
        self.conn = sqlite3.connect(self.db_path)

    def show_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        print("\n📊 Tables in this project:")
        for t in tables:
            print(f"- {t}")

    def edit_table(self):
        table = input("Enter the table name to edit: ").strip()
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]

        cursor.execute(f"SELECT rowid, * FROM {table}")
        rows = cursor.fetchall()
        print(f"\n📄 Rows in {table}:")
        for row in rows:
            print(row)

        rowid = input("\nEnter rowid to edit (or blank to cancel): ").strip()
        if not rowid:
            return

        updates = []
        for col in columns:
            val = input(f"New value for {col} (leave blank to keep): ").strip()
            if val:
                updates.append((col, val))

        if updates:
            set_clause = ", ".join([f"{col} = ?" for col, _ in updates])
            values = [val for _, val in updates]
            values.append(rowid)
            cursor.execute(f"UPDATE {table} SET {set_clause} WHERE rowid = ?", values)
            self.conn.commit()
            print("✅ Row updated.")

    def add_table_row(self):
        table = input("Enter the table name to add to: ").strip()
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        values = []
        for col in columns:
            val = input(f"  {col}: ").strip()
            values.append(val)
        cursor.execute(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['?']*len(columns))})", values)
        self.conn.commit()
        print("✅ Row added.")

    def delete_table_row(self):
        table = input("Enter the table name to delete from: ").strip()
        rowid = input("Enter the rowid to delete: ").strip()
        cursor = self.conn.cursor()
        cursor.execute(f"DELETE FROM {table} WHERE rowid = ?", (rowid,))
        self.conn.commit()
        print("🗑️ Row deleted.")

    def import_csv_to_sqlite(self):
        print("\n📁 Import CSV File")
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])
        if not filepath:
            print("⚠️ No file selected.")
            return

        table_name = input("📝 Enter name for the new table: ").strip()
        if not table_name.isidentifier():
            print("❌ Invalid table name.")
            return

        with open(filepath, newline='', encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            columns = ', '.join([f'"{h}" TEXT' for h in headers])
            cursor = self.conn.cursor()
            cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns})')
            for row in reader:
                cursor.execute(f'INSERT INTO "{table_name}" VALUES ({", ".join(["?"]*len(row))})', row)
            self.conn.commit()
            print(f"✅ Imported CSV into table '{table_name}'")

if __name__ == "__main__":
    editor = SQLTableEditor()
    editor.run()

