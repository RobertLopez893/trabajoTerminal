import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

# Credenciales para el servidor AWS (Base de datos remota)
# IMPORTANTE: Debes abrir el puerto 5433 en el Security Group de AWS para que funcione.
DB_HOST = "18.217.21.239"
DB_PORT = "5433"
DB_USER = "postgres"
DB_PASSWORD = "password"


class MiniGestorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌙 ANIMOON - Mini Gestor de Base de Datos")
        self.root.geometry("800x500")
        self.root.configure(padx=10, pady=10)

        # Variables
        self.db_var = tk.StringVar(value="animoon_operacional")
        
        self.create_widgets()

    def create_widgets(self):
        # Frame Superior (Controles)
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(control_frame, text="Base de Datos:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        db_combo = ttk.Combobox(control_frame, textvariable=self.db_var, values=["animoon_operacional", "animoon_auditoria"], state="readonly", width=25)
        db_combo.pack(side=tk.LEFT, padx=5)
        
        tk.Label(control_frame, text="Tabla:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(15, 5))
        
        self.table_combo = ttk.Combobox(control_frame, state="readonly", width=25)
        self.table_combo.pack(side=tk.LEFT, padx=5)
        
        btn_load_tables = tk.Button(control_frame, text="🔄 Conectar", command=self.load_tables, bg="#4CAF50", fg="white", font=("Arial", 9, "bold"))
        btn_load_tables.pack(side=tk.LEFT, padx=10)

        btn_view_data = tk.Button(control_frame, text="👁️ Ver Datos", command=self.view_data, bg="#2196F3", fg="white", font=("Arial", 9, "bold"))
        btn_view_data.pack(side=tk.LEFT, padx=5)

        # Frame Inferior (Tabla)
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

        self.tree = ttk.Treeview(table_frame, yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        scroll_y.config(command=self.tree.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.config(command=self.tree.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def get_connection(self):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                dbname=self.db_var.get()
            )
            return conn
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos:\n{str(e)}")
            return None

    def load_tables(self):
        conn = self.get_connection()
        if not conn: return
        
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cur.fetchall()]
            self.table_combo['values'] = tables
            if tables:
                self.table_combo.current(0)
            messagebox.showinfo("Éxito", f"Se encontraron {len(tables)} tablas en {self.db_var.get()}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def view_data(self):
        tabla = self.table_combo.get()
        if not tabla:
            messagebox.showwarning("Aviso", "Primero conecta y selecciona una tabla.")
            return

        conn = self.get_connection()
        if not conn: return
        
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {tabla} LIMIT 100")
            rows = cur.fetchall()
            
            # Obtener nombres de columnas
            colnames = [desc[0] for desc in cur.description]
            
            # Limpiar árbol actual
            self.tree.delete(*self.tree.get_children())
            
            # Configurar columnas
            self.tree["columns"] = colnames
            self.tree["show"] = "headings"
            
            for col in colnames:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120, anchor=tk.W)
                
            # Insertar datos
            for row in rows:
                self.tree.insert("", "end", values=row)
                
        except Exception as e:
            messagebox.showerror("Error SQL", str(e))
        finally:
            conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    # Estilo moderno básico
    style = ttk.Style()
    style.theme_use('clam')
    app = MiniGestorApp(root)
    root.mainloop()
