# database/db_manager.py
import sqlite3
import configparser
import os

def get_connection():
    return sqlite3.connect("database.db")

def inicializar_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recetas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            instrucciones TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL DEFAULT 0
        )
    ''')


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receta_ingrediente (
            receta_id INTEGER,
            ingrediente_id INTEGER,
            cantidad TEXT,
            FOREIGN KEY(receta_id) REFERENCES recetas(id),
            FOREIGN KEY(ingrediente_id) REFERENCES ingredientes(id)
        )
    ''')

    conn.commit()
    conn.close()

def obtener_recetas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.id, r.nombre, 
               IFNULL(SUM(i.precio * ri.cantidad), 0) AS costo_total
        FROM recetas r
        LEFT JOIN receta_ingrediente ri ON r.id = ri.receta_id
        LEFT JOIN ingredientes i ON ri.ingrediente_id = i.id
        GROUP BY r.id
        ORDER BY r.nombre ASC
    """)
    
    recetas = cursor.fetchall()
    conn.close()
    return recetas


def guardar_ingrediente_si_no_existe(nombre, precio=0.0):
    nombre = nombre.strip().lower().title()  # <-- estandarizamos
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM ingredientes WHERE LOWER(nombre) = ?", (nombre.lower(),))
    fila = cursor.fetchone()

    if fila:
        conn.close()
        return fila[0]

    cursor.execute("INSERT INTO ingredientes (nombre, precio) VALUES (?, ?)", (nombre, precio))
    ingrediente_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return ingrediente_id



def obtener_todos_ingredientes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM ingredientes ORDER BY nombre")
    ingredientes = [fila[0] for fila in cursor.fetchall()]
    conn.close()
    return ingredientes




def guardar_receta_completa(nombre, instrucciones, ingredientes):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO recetas (nombre, instrucciones) VALUES (?, ?)", (nombre, instrucciones))
    receta_id = cursor.lastrowid

    for nombre_ing, cantidad, precio_unitario in ingredientes:
        # Buscar o crear ingrediente
        cursor.execute("SELECT id FROM ingredientes WHERE nombre = ?", (nombre_ing,))
        result = cursor.fetchone()
        if result:
            ingrediente_id = result[0]
            # Actualizar precio
            cursor.execute("UPDATE ingredientes SET precio = ? WHERE id = ?", (precio_unitario, ingrediente_id))
        else:
            cursor.execute(
                "INSERT INTO ingredientes (nombre, precio) VALUES (?, ?)",
                (nombre_ing, precio_unitario)
            )
            ingrediente_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO receta_ingrediente (receta_id, ingrediente_id, cantidad) VALUES (?, ?, ?)",
            (receta_id, ingrediente_id, str(cantidad))
        )

    conn.commit()
    conn.close()

def actualizar_receta_completa(receta_id, nombre, instrucciones, ingredientes):
    conn = get_connection()
    cursor = conn.cursor()

    # Actualizar datos básicos de la receta
    cursor.execute(
        "UPDATE recetas SET nombre = ?, instrucciones = ? WHERE id = ?",
        (nombre, instrucciones, receta_id)
    )

    # Borrar ingredientes anteriores asociados
    cursor.execute("DELETE FROM receta_ingrediente WHERE receta_id = ?", (receta_id,))

    # Insertar ingredientes nuevos o actualizar precio si ya existen
    for nombre_ing, cantidad, precio_unitario in ingredientes:
        cursor.execute("SELECT id FROM ingredientes WHERE nombre = ?", (nombre_ing,))
        result = cursor.fetchone()
        if result:
            ingrediente_id = result[0]
            cursor.execute(
                "UPDATE ingredientes SET precio = ? WHERE id = ?",
                (precio_unitario, ingrediente_id)
            )
        else:
            cursor.execute(
                "INSERT INTO ingredientes (nombre, precio) VALUES (?, ?)",
                (nombre_ing, precio_unitario)
            )
            ingrediente_id = cursor.lastrowid

        # Insertar relación receta-ingrediente con cantidad
        cursor.execute(
            "INSERT INTO receta_ingrediente (receta_id, ingrediente_id, cantidad) VALUES (?, ?, ?)",
            (receta_id, ingrediente_id, str(cantidad))
        )

    conn.commit()
    conn.close()


def obtener_receta(receta_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nombre, instrucciones FROM recetas WHERE id = ?", (receta_id,))
    receta_row = cursor.fetchone()
    if not receta_row:
        conn.close()
        return None

    receta_id, nombre, instrucciones = receta_row

    cursor.execute("""
        SELECT i.nombre, ri.cantidad, i.precio
        FROM receta_ingrediente ri
        JOIN ingredientes i ON ri.ingrediente_id = i.id
        WHERE ri.receta_id = ?
    """, (receta_id,))

    ingredientes = cursor.fetchall()
    conn.close()

    return {
        'id': receta_id,
        'nombre': nombre,
        'instrucciones': instrucciones,
        'ingredientes': [(i[0], float(i[1]), float(i[2])) for i in ingredientes]
    }


def buscar_recetas_por_ingredientes(lista_ingredientes):
    conn = get_connection()
    cursor = conn.cursor()

    if not lista_ingredientes:
        return []

    patrones = [f"%{ing.lower()}%" for ing in lista_ingredientes]

    condiciones_like = " OR ".join(["LOWER(i.nombre) LIKE ?"] * len(patrones))

    query = f"""
    SELECT
        r.id,
        r.nombre,
        COUNT(DISTINCT i.id) AS ingredientes_coincidentes,
        (SELECT COUNT(*) FROM receta_ingrediente ri2 WHERE ri2.receta_id = r.id) AS total_ingredientes
    FROM recetas r
    JOIN receta_ingrediente ri ON r.id = ri.receta_id
    JOIN ingredientes i ON ri.ingrediente_id = i.id
    WHERE {condiciones_like}
    GROUP BY r.id
    HAVING ingredientes_coincidentes > 0
    ORDER BY (CAST(ingredientes_coincidentes AS FLOAT) / total_ingredientes) DESC
    """

    cursor.execute(query, patrones)
    filas = cursor.fetchall()
    conn.close()

    recetas = []
    for fila in filas:
        recetas.append({
            'id': fila[0],
            'nombre': fila[1],
            'ingredientes_coincidentes': fila[2],
            'total_ingredientes': fila[3],
            'porcentaje_coincidencia': fila[2] / fila[3] if fila[3] > 0 else 0
        })

    return recetas

def eliminar_receta_por_id(receta_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM receta_ingrediente WHERE receta_id = ?", (receta_id,))
    cursor.execute("DELETE FROM recetas WHERE id = ?", (receta_id,))

    conn.commit()
    conn.close()
