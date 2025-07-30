import os
import sqlite3
import csv
import re
import tkinter as tk
from tkinter import filedialog

class SQLTableEditor:
    def __init__(self, base_dir="projects"):
        self.base_dir = base_dir
        self.project_name = None
        self.db_path = None
        self.conn = None
    
    def validate_table_name(self, table_name):
        """Validate table name to prevent SQL injection"""
        if not table_name or not isinstance(table_name, str):
            return False
        # Allow only alphanumeric characters, underscores, and hyphens
        if not re.match(r'^[a-zA-Z0-9_-]+$', table_name):
            return False
        # Prevent SQL keywords
        sql_keywords = {'select', 'insert', 'update', 'delete', 'drop', 'create', 'alter', 'union', 'where'}
        if table_name.lower() in sql_keywords:
            return False
        return True

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
        
        # Validate table name
        if not self.validate_table_name(table):
            print("❌ Invalid table name.")
            return
            
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(" + table + ")")
        columns = [row[1] for row in cursor.fetchall()]

        cursor.execute("SELECT rowid, * FROM " + table)
        rows = cursor.fetchall()
        print(f"\n📄 Rows in {table}:")
        for row in rows:
            print(row)

        rowid = input("\nEnter rowid to edit (or blank to cancel): ").strip()
        if not rowid:
            return

        # Validate rowid is numeric
        try:
            int(rowid)
        except ValueError:
            print("❌ Invalid rowid - must be a number.")
            return

        updates = []
        for col in columns:
            # Validate column name
            if not re.match(r'^[a-zA-Z0-9_]+$', col):
                print(f"❌ Skipping invalid column name: {col}")
                continue
                
            val = input(f"New value for {col} (leave blank to keep): ").strip()
            if val:
                updates.append((col, val))

        if updates:
            set_clause = ", ".join([f"{col} = ?" for col, _ in updates])
            values = [val for _, val in updates]
            values.append(rowid)
            cursor.execute("UPDATE " + table + " SET " + set_clause + " WHERE rowid = ?", values)
            self.conn.commit()
            print("✅ Row updated.")

    def add_table_row(self):
        table = input("Enter the table name to add to: ").strip()
        
        # Validate table name
        if not self.validate_table_name(table):
            print("❌ Invalid table name.")
            return
            
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(" + table + ")")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Validate column names
        safe_columns = []
        for col in columns:
            if re.match(r'^[a-zA-Z0-9_]+$', col):
                safe_columns.append(col)
            else:
                print(f"❌ Skipping invalid column name: {col}")
        
        if not safe_columns:
            print("❌ No valid columns found.")
            return
            
        values = []
        for col in safe_columns:
            val = input(f"  {col}: ").strip()
            values.append(val)
            
        columns_str = ', '.join(safe_columns)
        placeholders = ', '.join(['?'] * len(safe_columns))
        
        cursor.execute(f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})", values)
        self.conn.commit()
        print("✅ Row added.")

    def delete_table_row(self):
        table = input("Enter the table name to delete from: ").strip()
        
        # Validate table name
        if not self.validate_table_name(table):
            print("❌ Invalid table name.")
            return
            
        rowid = input("Enter the rowid to delete: ").strip()
        
        # Validate rowid is numeric
        try:
            int(rowid)
        except ValueError:
            print("❌ Invalid rowid - must be a number.")
            return
            
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM " + table + " WHERE rowid = ?", (rowid,))
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
        if not self.validate_table_name(table_name):
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

