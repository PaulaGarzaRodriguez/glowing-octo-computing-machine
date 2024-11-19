import tkinter as tk
from tkinter import messagebox, Toplevel
from tkinter import ttk
from collections import defaultdict
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# Conexión a la base de datos
def conectar_bd():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="campusfp",
            database="ENCUESTAS"
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Error de conexión", f"Error: {err}")
        return None

# Función para crear encuestas
def crear_encuesta():
    edad = entries["Edad"].get()
    sexo_mujer = sexo_mujer_var.get()
    sexo_hombre = sexo_hombre_var.get()
    bebidas_semana = entries["Bebidas a la semana"].get()
    cervezas_semana = entries["Cervezas a la semana"].get()
    bebidas_fin_semana = entries["Bebidas fin de semana"].get()
    bebidas_destiladas_semana = entries["Bebidas destiladas a la semana"].get()
    vinos_semana = entries["Vinos a la semana"].get()
    perdidas_control = entries["¿Pierdes el control?"].get()
    diversion = diversion_combobox.get()  # Obtener del Combobox
    problemas_digestivos = problemas_digestivos_combobox.get()  # Obtener del Combobox
    tension_alta = tension_alta_combobox.get()  # Obtener del Combobox
    dolor_cabeza = dolorcabeza_combobox.get()

    # Validación de campos vacíos
    if not edad or not (sexo_mujer or sexo_hombre) or not bebidas_semana or not cervezas_semana or not bebidas_fin_semana or not bebidas_destiladas_semana or not vinos_semana or not perdidas_control or not diversion or not problemas_digestivos or not tension_alta or not dolor_cabeza:
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return
    
    # Validación de que el sexo esté seleccionado correctamente (solo uno)
    if not sexo_mujer and not sexo_hombre:
        messagebox.showerror("Error", "Debe seleccionar uno de los dos sexos (Mujer o Hombre).")
        return
    
    # Validación de que los valores numéricos no sean negativos
    if not edad.isdigit() or int(edad) < 0:
        messagebox.showerror("Error", "La edad debe ser un valor positivo.")
        return
    if not bebidas_semana.isdigit() or int(bebidas_semana) < 0:
        messagebox.showerror("Error", "Las bebidas a la semana deben ser un valor positivo.")
        return
    if not cervezas_semana.isdigit() or int(cervezas_semana) < 0:
        messagebox.showerror("Error", "Las cervezas a la semana deben ser un valor positivo.")
        return
    if not bebidas_fin_semana.isdigit() or int(bebidas_fin_semana) < 0:
        messagebox.showerror("Error", "Las bebidas fin de semana deben ser un valor positivo.")
        return
    if not bebidas_destiladas_semana.isdigit() or int(bebidas_destiladas_semana) < 0:
        messagebox.showerror("Error", "Las bebidas destiladas a la semana deben ser un valor positivo.")
        return
    if not vinos_semana.isdigit() or int(vinos_semana) < 0:
        messagebox.showerror("Error", "Los vinos a la semana deben ser un valor positivo.")
        return

    # Convertir "SI" y "NO"
    diversion = "SI" if diversion == "SI" else "NO"
    problemas_digestivos = "SI" if problemas_digestivos == "SI" else "NO"
    tension_alta = "SI" if tension_alta == "SI" else "NO"

    # Conexión a la base de datos
    conn = conectar_bd()
    if conn is None:
        return
    cursor = conn.cursor()

    # Elimina la columna 'id' de la consulta, porque es autoincremental
    query = """
        INSERT INTO ENCUESTA (
            edad, Sexo, BebidasSemana, CervezasSemana, BebidasFinSemana, 
            BebidasDestiladasSemana, VinosSemana, PerdidasControl, 
            DiversionDependenciaAlcohol, ProblemasDigestivos, TensionAlta, DolorCabeza
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        # Preparar el valor de sexo
        sexo = ""
        if sexo_mujer:
            sexo = "Mujer"
        elif sexo_hombre:
            sexo = "Hombre"
        
        # Ejecutar la consulta
        cursor.execute(query, (
            edad, sexo, bebidas_semana, cervezas_semana,
            bebidas_fin_semana, bebidas_destiladas_semana, vinos_semana,
            perdidas_control, diversion, problemas_digestivos,
            tension_alta, dolor_cabeza
        ))
        conn.commit()
        messagebox.showinfo("Éxito", "Encuesta creada correctamente.")
        limpiar_campos()
    except mysql.connector.Error as err:
        # Manejo de errores
        if err.errno == 1062:
            messagebox.showerror("Error al insertar", "Entrada duplicada en la clave primaria.")
        else:
            messagebox.showerror("Error al insertar", f"Error: {err}")
    finally:
        cursor.close()
        conn.close()




# Función para limpiar los campos de entrada
def limpiar_campos():
    for entry in entries.values():
        entry.delete(0, tk.END)
    sexo_mujer_var.set(False)
    sexo_hombre_var.set(False)
    # Limpiar los Combobox
    diversion_combobox.set("")
    problemas_digestivos_combobox.set("")
    tension_alta_combobox.set("")

# Función para mostrar todas las encuestas
def mostrar_encuestas():
    conn = conectar_bd()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ENCUESTA")
    encuestas = cursor.fetchall()
    treeview.delete(*treeview.get_children()) 
    for encuesta in encuestas:
        treeview.insert("", tk.END, values=encuesta)
    cursor.close()
    conn.close()

# Función para eliminar una encuesta
def eliminar_encuesta():
    selected_item = treeview.selection()
    if not selected_item:
        messagebox.showerror("Error", "Debe seleccionar una encuesta para eliminar.")
        return
    
    id_encuesta = treeview.item(selected_item)["values"][0]
    confirmacion = messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de que deseas eliminar la encuesta con ID {id_encuesta}?")
    if confirmacion:
        conn = conectar_bd()
        if conn is None:
            return
        cursor = conn.cursor()
        query = "DELETE FROM ENCUESTA WHERE idEncuesta = %s"
        try:
            cursor.execute(query, (id_encuesta,))
            conn.commit()
            if cursor.rowcount > 0:
                messagebox.showinfo("Éxito", "Encuesta eliminada correctamente.")
                mostrar_encuestas()  # Actualizar la tabla
            else:
                messagebox.showerror("Error", "No se encontró ninguna encuesta con ese ID.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error al eliminar", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

def modificar_encuesta():
    selected_item = treeview.selection()
    if not selected_item:
        messagebox.showerror("Error", "Debe seleccionar una encuesta para modificar.")
        return

    id_encuesta = treeview.item(selected_item)["values"][0]
    conn = conectar_bd()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ENCUESTA WHERE idEncuesta = %s", (id_encuesta,))
    encuesta = cursor.fetchone()
    cursor.close()
    conn.close()

    if encuesta is None:
        messagebox.showerror("Error", "Encuesta no encontrada.")
        return

    ventana_modificar = Toplevel(ventana)
    ventana_modificar.title("Modificar Encuesta")
    ventana_modificar.geometry("500x500")

    labels_modificar = [
        "Edad", "Sexo", "Bebidas a la semana", "Cervezas a la semana",
        "Bebidas fin de semana", "Bebidas destiladas a la semana",
        "Vinos a la semana", "¿Pierdes el control?", "Diversión y alcohol",
        "Problemas digestivos", "¿Tensión alta?", "Dolor de cabeza"
    ]
    
    entries_modificar = {}
    sexo_var = tk.StringVar(value="Mujer" if encuesta[2] == "Mujer" else "Hombre")

    for i, label in enumerate(labels_modificar):
        tk.Label(ventana_modificar, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
        if label == "Sexo":
            tk.Radiobutton(ventana_modificar, text="Mujer", variable=sexo_var, value="Mujer").grid(row=i, column=1, padx=10, pady=5, sticky="w")
            tk.Radiobutton(ventana_modificar, text="Hombre", variable=sexo_var, value="Hombre").grid(row=i, column=1, padx=10, pady=5, sticky="e")
        else:
            entry = tk.Entry(ventana_modificar)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries_modificar[label] = entry
            entries_modificar[label].insert(0, encuesta[i + 1] if i != 0 else encuesta[1])

    combobox_labels = ["¿Pierdes el control?", "Diversión y alcohol", "Problemas digestivos", "¿Tensión alta?", "Dolor de cabeza"]
    combobox_values = {
        "¿Pierdes el control?": ["", "SI", "NO"],
        "Diversión y alcohol": ["", "SI", "NO"],
        "Problemas digestivos": ["", "SI", "NO"],
        "¿Tensión alta?": ["", "SI", "NO"],
        "Dolor de cabeza": ["", "Alguna vez", "Muy a menudo", "Nunca", "A menudo", "No lo sé"]
    }
    comboboxes = {}
    
    for i, label in enumerate(combobox_labels, start=7):
        combobox = ttk.Combobox(ventana_modificar, values=combobox_values[label])
        combobox.set(encuesta[i] if label != "Dolor de cabeza" else encuesta[-1])
        combobox.grid(row=i, column=1, padx=10, pady=5)
        comboboxes[label] = combobox

    def guardar_modificacion():
        edad = entries_modificar["Edad"].get()
        sexo = sexo_var.get()
        bebidas_semana = entries_modificar["Bebidas a la semana"].get()
        cervezas_semana = entries_modificar["Cervezas a la semana"].get()
        bebidas_fin_semana = entries_modificar["Bebidas fin de semana"].get()
        bebidas_destiladas_semana = entries_modificar["Bebidas destiladas a la semana"].get()
        vinos_semana = entries_modificar["Vinos a la semana"].get()
        perdidas_control = comboboxes["¿Pierdes el control?"].get()
        diversion = comboboxes["Diversión y alcohol"].get()
        problemas_digestivos = comboboxes["Problemas digestivos"].get()
        tension_alta = comboboxes["¿Tensión alta?"].get()
        dolor_cabeza = comboboxes["Dolor de cabeza"].get()

        if any(not field for field in [edad, sexo, bebidas_semana, cervezas_semana, bebidas_fin_semana, bebidas_destiladas_semana, vinos_semana, perdidas_control, diversion, problemas_digestivos, tension_alta, dolor_cabeza]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        if any(not v.isdigit() or int(v) < 0 for v in [edad, bebidas_semana, cervezas_semana, bebidas_fin_semana, bebidas_destiladas_semana, vinos_semana]):
            messagebox.showerror("Error", "Algunos campos requieren valores numéricos positivos.")
            return
        
        perdidas_control = 1 if perdidas_control == "SI" else 0
        diversion = 1 if diversion == "SI" else 0
        problemas_digestivos = 1 if problemas_digestivos == "SI" else 0
        tension_alta = 1 if tension_alta == "SI" else 0

        conn = conectar_bd()
        if conn is None:
            return
        cursor = conn.cursor()
        query = """
            UPDATE ENCUESTA SET edad = %s, Sexo = %s, BebidasSemana = %s, CervezasSemana = %s,
            BebidasFinSemana = %s, BebidasDestiladasSemana = %s, VinosSemana = %s, PerdidasControl = %s, 
            DiversionDependenciaAlcohol = %s, ProblemasDigestivos = %s, TensionAlta = %s, DolorCabeza = %s
            WHERE idEncuesta = %s
        """
        try:
            cursor.execute(query, (edad, sexo, bebidas_semana, cervezas_semana, bebidas_fin_semana, bebidas_destiladas_semana, vinos_semana, perdidas_control, diversion, problemas_digestivos, tension_alta, dolor_cabeza, id_encuesta))
            conn.commit()
            messagebox.showinfo("Éxito", "Encuesta modificada correctamente.")
            ventana_modificar.destroy()
            mostrar_encuestas()
        except mysql.connector.Error as err:
            messagebox.showerror("Error al modificar", f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    btn_guardar = tk.Button(ventana_modificar, text="Guardar cambios", command=guardar_modificacion)
    btn_guardar.grid(row=len(labels_modificar) + 1, column=1, pady=20)




def buscar_encuestas():
    # Obtén los valores de los campos de entrada
    edad = entries["Edad"].get()
    sexo_mujer = sexo_mujer_var.get()
    sexo_hombre = sexo_hombre_var.get()
    bebidas_semana = entries["Bebidas a la semana"].get()
    cervezas_semana = entries["Cervezas a la semana"].get()
    bebidas_fin_semana = entries["Bebidas fin de semana"].get()
    bebidas_destiladas_semana = entries["Bebidas destiladas a la semana"].get()
    vinos_semana = entries["Vinos a la semana"].get()
    perdidas_control = entries["¿Pierdes el control?"].get()
    diversion = diversion_combobox.get()
    problemas_digestivos = problemas_digestivos_combobox.get()
    tension_alta = tension_alta_combobox.get()
    dolor_cabeza = dolorcabeza_combobox.get()

    # Conectar a la base de datos
    conn = conectar_bd()
    if conn is None:
        return
    
    cursor = conn.cursor()

    # Preparamos la consulta SQL para la búsqueda
    query = """
        SELECT * FROM ENCUESTA WHERE 1=1
    """
    
    # Lista de parámetros que se van a pasar
    params = []
    
    # Agregar filtros a la consulta según los valores de los campos
    if edad:
        query += " AND edad = %s"
        params.append(edad)
    
    if sexo_mujer:
        query += " AND Sexo LIKE %s"
        params.append("%Mujer%")
    
    if sexo_hombre:
        query += " AND Sexo LIKE %s"
        params.append("%Hombre%")
    
    if bebidas_semana:
        query += " AND BebidasSemana = %s"
        params.append(bebidas_semana)
    
    if cervezas_semana:
        query += " AND CervezasSemana = %s"
        params.append(cervezas_semana)
    
    if bebidas_fin_semana:
        query += " AND BebidasFinSemana = %s"
        params.append(bebidas_fin_semana)
    
    if bebidas_destiladas_semana:
        query += " AND BebidasDestiladasSemana = %s"
        params.append(bebidas_destiladas_semana)
    
    if vinos_semana:
        query += " AND VinosSemana = %s"
        params.append(vinos_semana)
    
    if perdidas_control:
        query += " AND PerdidasControl = %s"
        params.append(1 if perdidas_control == "SI" else "SI")
    
    if diversion:
        query += " AND DiversionDependenciaAlcohol = %s"
        params.append(1 if diversion == "SI" else 0)
    
    if problemas_digestivos:
        query += " AND ProblemasDigestivos = %s"
        params.append(1 if problemas_digestivos == "SI" else 0)
    
    if tension_alta:
        query += " AND TensionAlta = %s"
        params.append(1 if tension_alta == "SI" else 0)
    
    if dolor_cabeza:
        query += " AND DolorCabeza = %s"
        params.append(dolor_cabeza)

    # Ejecutamos la consulta con los parámetros
    cursor.execute(query, tuple(params))
    encuestas = cursor.fetchall()

    # Limpiar el Treeview y agregar las encuestas encontradas
    treeview.delete(*treeview.get_children())
    for encuesta in encuestas:
        treeview.insert("", tk.END, values=encuesta)
    
    # Limpiar los campos de entrada después de la búsqueda
    limpiar_campos()
    
    cursor.close()
    conn.close()


# Función para exportar las encuestas a Excel
def exportar_a_excel():
    conn = conectar_bd()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ENCUESTA")
    encuestas = cursor.fetchall()
    df = pd.DataFrame(encuestas, columns=["ID", "Edad", "Sexo", "BebidasSemana", "CervezasSemana", "BebidasFinSemana", 
    "BebidasDestiladasSemana", "VinosSemana", "PerdidasControl", "DiversionDependenciaAlcohol", "ProblemasDigestivos", 
    "TensionAlta", "DolorCabeza"])
    df.to_excel("encuestas.xlsx", index=False)
    messagebox.showinfo("Éxito", "Encuestas exportadas a Excel.")
    cursor.close()
    conn.close()


# Función para ordenar las encuestas
def ordenar_encuestas():
    columna = campo_ordenar_combobox.get()
    if not columna:
        messagebox.showerror("Error", "Debe seleccionar un campo para ordenar.")
        return

    conn = conectar_bd()
    if conn is None:
        return
    cursor = conn.cursor()

    # Crear una consulta para ordenar según la columna seleccionada
    query = f"SELECT * FROM ENCUESTA ORDER BY {columna} ASC"
    cursor.execute(query)
    encuestas = cursor.fetchall()

    # Limpiar el Treeview y agregar los datos ordenados
    treeview.delete(*treeview.get_children())
    for encuesta in encuestas:
        treeview.insert("", tk.END, values=encuesta)

    cursor.close()
    conn.close()

# Función para mostrar gráficos
def mostrar_ventana_grafico():
    # Crear una nueva ventana para mostrar gráficos
    ventana_grafico = tk.Toplevel(ventana)
    ventana_grafico.title("Seleccionar tipo de gráfico")
    ventana_grafico.geometry("800x400")

    def mostrar_grafico_sexo():
        conn = conectar_bd()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("SELECT Sexo FROM ENCUESTA")
        encuestas = cursor.fetchall()
        cursor.close()
        conn.close()

        if not encuestas:
            messagebox.showerror("Error", "No hay datos para mostrar.")
            return

        # Contar la cantidad de "Mujer" y "Hombre"
        sexo_hombres = sum(1 for encuesta in encuestas if encuesta[0] == "Hombre")
        sexo_mujeres = sum(1 for encuesta in encuestas if encuesta[0] == "Mujer")

        # Mostrar el gráfico circular
        plt.figure(figsize=(8, 8))
        plt.pie(
            [sexo_hombres, sexo_mujeres],
            labels=["Hombres", "Mujeres"],
            autopct='%1.1f%%',
            startangle=140,
            textprops={'fontsize': 12},
            explode=(0.1, 0)  # Añadir explosión a la sección
        )
        plt.title('Distribución por Sexo')
        plt.axis('equal')  # Asegura que el gráfico sea un círculo
        plt.show()

    # Función para mostrar gráfico circular o de barras para BebidasSemana
    def mostrar_grafico_bebidas(tipo_grafico):
        conn = conectar_bd()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("SELECT Edad, BebidasSemana FROM ENCUESTA")
        encuestas = cursor.fetchall()
        cursor.close()
        conn.close()

        if not encuestas:
            messagebox.showerror("Error", "No hay datos para mostrar.")
            return

        # Agrupar los datos por edad
        datos_agrupados = defaultdict(list)
        for encuesta in encuestas:
            edad = str(encuesta[0])  # Convertir edad a string
            bebidas = encuesta[1]
            if bebidas is not None:  # Validar que el valor no sea None
                datos_agrupados[edad].append(bebidas)

        # Promediar las bebidas por edad
        edades = list(datos_agrupados.keys())
        bebidas = [sum(bebidas_list) / len(bebidas_list) for bebidas_list in datos_agrupados.values()]

        if tipo_grafico == 'circular':
            # Gráfico circular
            plt.figure(figsize=(10, 10))
            plt.pie(
                bebidas,
                labels=edades,
                startangle=140,
                textprops={'fontsize': 10},
                pctdistance=0.85,
                explode=(0.05,) * len(bebidas)  # Añadir pequeño "explosión" a las porciones
            )
            plt.title('Consumo de bebidas por edad')
            plt.axis('equal')
            plt.show()
        elif tipo_grafico == 'barras':
            # Gráfico de barras
            plt.figure(figsize=(12, 6))
            plt.bar(edades, bebidas, color='blue')
            plt.xlabel('Edad')
            plt.ylabel('Promedio de bebidas a la semana')
            plt.title('Consumo de bebidas por edad')
            plt.xticks(rotation=90)  # Rotar etiquetas para mayor visibilidad
            plt.show()

    # Panel de selección para el tipo de gráfico de BebidasSemana
    frame_seleccion = tk.Frame(ventana_grafico)
    frame_seleccion.pack(side="right", padx=20)

    # Label para los gráficos de BebidasSemana
    label_grafico = tk.Label(frame_seleccion, text="Selecciona el tipo de gráfico para Bebidas a la semana:")
    label_grafico.pack(pady=10)

    # Función que maneja la selección del tipo de gráfico
    def elegir_grafico():
        tipo_grafico = tipo_grafico_var.get()
        mostrar_grafico_bebidas(tipo_grafico)

    # Variable para seleccionar el tipo de gráfico
    tipo_grafico_var = tk.StringVar(value="circular")  # Valor por defecto es circular

    # Opciones para el tipo de gráfico
    radio_circular = tk.Radiobutton(frame_seleccion, text="Gráfico Circular", variable=tipo_grafico_var, value="circular")
    radio_circular.pack(pady=5)
    radio_barras = tk.Radiobutton(frame_seleccion, text="Gráfico de Barras", variable=tipo_grafico_var, value="barras")
    radio_barras.pack(pady=5)

    # Botón para mostrar el gráfico elegido
    btn_mostrar_grafico = tk.Button(frame_seleccion, text="Mostrar Gráfico", command=elegir_grafico)
    btn_mostrar_grafico.pack(pady=20)

    # Botón para mostrar gráfico de sexo
    btn_mostrar_sexo = tk.Button(ventana_grafico, text="Mostrar Gráfico de Sexo", command=mostrar_grafico_sexo)
    btn_mostrar_sexo.pack(pady=10)

    
# Crear ventana principal
ventana = tk.Tk()
ventana.title("Encuestas")
ventana.geometry("1200x600")

# Frame para los campos de entrada
frame_entrada = tk.Frame(ventana)
frame_entrada.pack(pady=20)

# Crear etiquetas y campos de entrada
labels_col1 = [
    "Edad", "Sexo", "Bebidas a la semana", "Cervezas a la semana", 
    "Bebidas fin de semana", "Bebidas destiladas a la semana"
]
labels_col2 = [
    "Vinos a la semana", "¿Pierdes el control?", "Diversión y alcohol", 
    "Problemas digestivos", "¿Tensión alta?", "Dolor de cabeza"
]

entries = {}

# Columna 1
for i, label in enumerate(labels_col1):
    tk.Label(frame_entrada, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
    if label == "Sexo":
        sexo_mujer_var = tk.BooleanVar()
        sexo_hombre_var = tk.BooleanVar()
        cb_mujer = tk.Checkbutton(frame_entrada, text="Mujer", variable=sexo_mujer_var)
        cb_hombre = tk.Checkbutton(frame_entrada, text="Hombre", variable=sexo_hombre_var)
        cb_mujer.grid(row=i, column=1, padx=10, pady=5, sticky="w")
        cb_hombre.grid(row=i, column=1, padx=10, pady=5, sticky="e")
    else:
        entry = tk.Entry(frame_entrada)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[label] = entry

# Columna 2
for i, label in enumerate(labels_col2):
    tk.Label(frame_entrada, text=label).grid(row=i, column=2, padx=10, pady=5, sticky="e")
    if label == "¿Pierdes el control?":
        # Cambiar el combobox por un campo de entrada
        entry = tk.Entry(frame_entrada)
        entry.grid(row=i, column=3, padx=10, pady=5)
        entries[label] = entry  # Guardar el campo en el diccionario de entradas
    elif label == "Diversión y alcohol":
        diversion_combobox = ttk.Combobox(frame_entrada, values=["", "SI", "NO"])
        diversion_combobox.grid(row=i, column=3, padx=10, pady=5)
    elif label == "Problemas digestivos":
        problemas_digestivos_combobox = ttk.Combobox(frame_entrada, values=["", "SI", "NO"])
        problemas_digestivos_combobox.grid(row=i, column=3, padx=10, pady=5)
    elif label == "¿Tensión alta?":
        tension_alta_combobox = ttk.Combobox(frame_entrada, values=["", "SI", "NO"])
        tension_alta_combobox.grid(row=i, column=3, padx=10, pady=5)
    elif label == "Dolor de cabeza":
        dolorcabeza_combobox = ttk.Combobox(frame_entrada, values=["", "Alguna vez", "Muy a menudo", "Nunca", "A menudo", "No lo sé"])
        dolorcabeza_combobox.grid(row=i, column=3, padx=10, pady=5)
    else:
        entry = tk.Entry(frame_entrada)
        entry.grid(row=i, column=3, padx=10, pady=5)
        entries[label] = entry


# Botones de acción
button_frame = tk.Frame(ventana)
button_frame.pack(pady=20)

btn_mostrar = tk.Button(button_frame, text="Mostrar Encuestas", command=mostrar_encuestas, bg="lightblue", fg="black")
btn_mostrar.grid(row=0, column=0, padx=20, pady=5)

btn_crear = tk.Button(button_frame, text="Añadir Encuesta", command=crear_encuesta, bg="lightgreen", fg="black")
btn_crear.grid(row=0, column=1, padx=20, pady=5)

btn_eliminar = tk.Button(button_frame, text="Eliminar Encuesta", command=eliminar_encuesta, bg="lightcoral", fg="white")
btn_eliminar.grid(row=0, column=2, padx=20, pady=5)

btn_exportar = tk.Button(button_frame, text="Modificar Encuesta", command=modificar_encuesta, bg="gold", fg="black")
btn_exportar.grid(row=0, column=3, padx=20, pady=5)

# ComboBox para seleccionar el campo de ordenación
# Crear estilo para el Combobox
style = ttk.Style()
style.theme_use("default")
style.configure("Custom.TCombobox",
                fieldbackground="orchid",  # Fondo del área seleccionada
                background="orchid",      # Fondo del desplegable
                foreground="white")       # Color del texto

# Aplicar el estilo al Combobox
# Crear estilo para el Combobox
style = ttk.Style()
style.theme_use("default")
style.configure("Custom.TCombobox",
                fieldbackground="orchid",  # Fondo del área seleccionada
                background="orchid",      # Fondo del desplegable
                foreground="black")       # Color del texto

# Aplicar el estilo al Combobox
campo_ordenar_combobox = ttk.Combobox(button_frame, 
                                      values=["Edad", "Bebidas a la semana", "Cervezas a la semana", 
                                              "Bebidas fin de semana", "Bebidas destiladas a la semana", 
                                              "Vinos a la semana", "PerdidasControl", 
                                              "DiversionDependenciaAlcohol", "ProblemasDigestivos", 
                                              "TensionAlta", "DolorCabeza"], 
                                      state="readonly", 
                                      style="Custom.TCombobox")



campo_ordenar_combobox.set("Edad")  # Valor predeterminado
campo_ordenar_combobox.grid(row=0, column=4, padx=20, pady=5)

                                                           
campo_ordenar_combobox.set("Edad")  # Valor predeterminado
campo_ordenar_combobox.grid(row=0, column=4, padx=20, pady=5)

# Botón para ordenar las encuestas
btn_ordenar = tk.Button(button_frame, text="Ordenar Encuestas", command=ordenar_encuestas, bg="orchid", fg="white")
btn_ordenar.grid(row=0, column=5, padx=20, pady=5)

btn_buscar = tk.Button(button_frame, text="Buscar Encuestas", command=buscar_encuestas, bg="skyblue", fg="black")
btn_buscar.grid(row=0, column=6, padx=20, pady=5)

btn_exportar_excel = tk.Button(button_frame, text="Exportar a Excel", command=exportar_a_excel, bg="limegreen", fg="white")
btn_exportar_excel.grid(row=0, column=7, padx=20, pady=5)

btn_grafico = tk.Button(button_frame, text="Mostrar Gráfico", command=mostrar_ventana_grafico, bg="slateblue", fg="white")
btn_grafico.grid(row=0, column=8, padx=20, pady=5)



# Crear el Treeview para mostrar las encuestas
treeview = ttk.Treeview(ventana, columns=("ID", "Edad", "Sexo", "BebidasSemana", "CervezasSemana", "BebidasFinSemana", "BebidasDestiladasSemana", "VinosSemana", "PerdidasControl", "DiversionDependenciaAlcohol", "ProblemasDigestivos", "TensionAlta", "DolorCabeza"), show="headings")
treeview.pack(pady=20)

# Definir los encabezados y sus anchos
column_widths = {
    "ID": 50,
    "Edad": 80,
    "Sexo": 100,
    "BebidasSemana": 120,
    "CervezasSemana": 120,
    "BebidasFinSemana": 140,
    "BebidasDestiladasSemana": 180,
    "VinosSemana": 120,
    "PerdidasControl": 150,
    "DiversionDependenciaAlcohol": 180,
    "ProblemasDigestivos": 180,
    "TensionAlta": 120,
    "DolorCabeza": 120
}

# Configurar los encabezados
for col in treeview["columns"]:
    treeview.heading(col, text=col)
    treeview.column(col, width=column_widths[col], anchor="center")  # Fijamos el ancho de las columnas

ventana.mainloop()
