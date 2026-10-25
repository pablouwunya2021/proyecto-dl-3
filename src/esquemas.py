"""Definición estructurada de los esquemas propios (MySQL 8.4).

Cada esquema se describe con tablas, columnas (con tipo, COMMENT y rol
semántico) y datos de ejemplo. A partir de esta estructura se generan:

- el DDL `CREATE TABLE ...` (campo `esquema` del contrato),
- los `INSERT` de datos de prueba (para validar el SQL en MySQL),
- los pares pregunta–SQL sintéticos (ver src/generar_datos.py).

Los roles de columna guían qué preguntas se pueden formular:
  id        -> clave / identificador
  texto     -> nombre o descripción (VARCHAR)
  categoria -> valor categórico con pocos distintos (para GROUP BY, WHERE =)
  numero    -> medida numérica (SUM, AVG, MAX, MIN, >, <)
  fecha     -> fecha (funciones de fecha, rangos)
  booleano  -> 0/1

Hay esquemas de ENTRENAMIENTO y de VALIDACION. La partición es por esquema:
los esquemas de validación NO se usan para generar datos de entrenamiento.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Columna:
    nombre: str
    tipo: str
    rol: str                      # id|texto|categoria|numero|fecha|booleano
    comentario: str = ""
    pk: bool = False
    fk: Optional[str] = None      # "tabla.columna"
    valores: Optional[List[str]] = None  # dominio para categóricas


@dataclass
class Tabla:
    nombre: str
    comentario: str
    columnas: List[Columna]
    filas: List[tuple] = field(default_factory=list)


@dataclass
class Esquema:
    nombre: str
    descripcion: str
    tablas: List[Tabla]


def _col(n, t, rol, c="", pk=False, fk=None, valores=None):
    return Columna(n, t, rol, c, pk, fk, valores)


# ==========================================================================
# ESQUEMAS DE ENTRENAMIENTO (10)
# ==========================================================================
ESQUEMAS_ENTRENAMIENTO: List[Esquema] = []
ESQUEMAS_VALIDACION: List[Esquema] = []


def _reg_train(e):
    ESQUEMAS_ENTRENAMIENTO.append(e)
    return e


def _reg_val(e):
    ESQUEMAS_VALIDACION.append(e)
    return e


# --- 1. Tienda / e-commerce (español) -------------------------------------
_reg_train(Esquema(
    "tienda", "Comercio en línea: clientes, productos y pedidos.",
    [
        Tabla("clientes", "Clientes registrados en la tienda", [
            _col("id_cliente", "INT", "id", "Identificador del cliente", pk=True),
            _col("nombre", "VARCHAR(100)", "texto", "Nombre completo"),
            _col("ciudad", "VARCHAR(50)", "categoria", "Ciudad de residencia",
                 valores=["Guatemala", "Quetzaltenango", "Escuintla", "Antigua"]),
            _col("fecha_registro", "DATE", "fecha", "Fecha de alta"),
        ], filas=[
            (1, "Ana López", "Guatemala", "2023-01-15"),
            (2, "Luis Pérez", "Quetzaltenango", "2023-03-22"),
            (3, "María Gómez", "Guatemala", "2024-02-10"),
            (4, "Carlos Ruiz", "Escuintla", "2024-06-01"),
        ]),
        Tabla("productos", "Catálogo de productos", [
            _col("id_producto", "INT", "id", "Identificador del producto", pk=True),
            _col("nombre", "VARCHAR(100)", "texto", "Nombre del producto"),
            _col("categoria", "VARCHAR(50)", "categoria", "Categoría",
                 valores=["Electrónica", "Hogar", "Ropa", "Juguetes"]),
            _col("precio", "DECIMAL(10,2)", "numero", "Precio unitario en quetzales"),
        ], filas=[
            (1, "Audífonos", "Electrónica", "250.00"),
            (2, "Lámpara", "Hogar", "120.50"),
            (3, "Camisa", "Ropa", "85.00"),
            (4, "Rompecabezas", "Juguetes", "60.00"),
            (5, "Teclado", "Electrónica", "180.00"),
        ]),
        Tabla("pedidos", "Pedidos realizados por los clientes", [
            _col("id_pedido", "INT", "id", "Identificador del pedido", pk=True),
            _col("id_cliente", "INT", "id", "Cliente que hizo el pedido",
                 fk="clientes.id_cliente"),
            _col("id_producto", "INT", "id", "Producto pedido",
                 fk="productos.id_producto"),
            _col("cantidad", "INT", "numero", "Unidades pedidas"),
            _col("fecha", "DATE", "fecha", "Fecha del pedido"),
        ], filas=[
            (1, 1, 1, 2, "2024-07-01"),
            (2, 1, 3, 1, "2024-07-03"),
            (3, 2, 2, 3, "2024-07-05"),
            (4, 3, 5, 1, "2024-08-10"),
            (5, 3, 1, 1, "2024-08-11"),
            (6, 4, 4, 2, "2024-09-01"),
        ]),
    ],
))

# --- 2. Recursos humanos (inglés, abreviado) ------------------------------
_reg_train(Esquema(
    "hr", "Human resources: employees and departments.",
    [
        Tabla("dept", "Company departments", [
            _col("dept_id", "INT", "id", "Department id", pk=True),
            _col("dname", "VARCHAR(60)", "texto", "Department name"),
            _col("loc", "VARCHAR(40)", "categoria", "Location",
                 valores=["HQ", "Branch-A", "Branch-B"]),
        ], filas=[
            (10, "Engineering", "HQ"),
            (20, "Sales", "Branch-A"),
            (30, "Support", "Branch-B"),
        ]),
        Tabla("emp", "Employees", [
            _col("emp_id", "INT", "id", "Employee id", pk=True),
            _col("ename", "VARCHAR(60)", "texto", "Employee name"),
            _col("dept_id", "INT", "id", "Department", fk="dept.dept_id"),
            _col("salary", "DECIMAL(10,2)", "numero", "Monthly salary"),
            _col("hire_date", "DATE", "fecha", "Hire date"),
            _col("active", "TINYINT(1)", "booleano", "1 if currently active"),
        ], filas=[
            (1, "Alice", 10, "9000.00", "2021-02-01", 1),
            (2, "Bob", 10, "7500.00", "2022-05-15", 1),
            (3, "Carol", 20, "6000.00", "2020-09-10", 1),
            (4, "Dan", 20, "5500.00", "2023-01-20", 0),
            (5, "Eve", 30, "4800.00", "2023-07-01", 1),
        ]),
    ],
))

# --- 3. Biblioteca (español) ----------------------------------------------
_reg_train(Esquema(
    "biblioteca", "Biblioteca: libros, autores y préstamos.",
    [
        Tabla("autores", "Autores de los libros", [
            _col("id_autor", "INT", "id", "Id del autor", pk=True),
            _col("nombre", "VARCHAR(100)", "texto", "Nombre del autor"),
            _col("pais", "VARCHAR(40)", "categoria", "País de origen",
                 valores=["Guatemala", "México", "Colombia", "España"]),
        ], filas=[
            (1, "Miguel Ángel Asturias", "Guatemala"),
            (2, "Gabriel García Márquez", "Colombia"),
            (3, "Octavio Paz", "México"),
        ]),
        Tabla("libros", "Libros del catálogo", [
            _col("id_libro", "INT", "id", "Id del libro", pk=True),
            _col("titulo", "VARCHAR(150)", "texto", "Título"),
            _col("id_autor", "INT", "id", "Autor", fk="autores.id_autor"),
            _col("anio", "INT", "numero", "Año de publicación"),
            _col("genero", "VARCHAR(40)", "categoria", "Género",
                 valores=["Novela", "Poesía", "Ensayo"]),
        ], filas=[
            (1, "El Señor Presidente", 1, 1946, "Novela"),
            (2, "Hombres de maíz", 1, 1949, "Novela"),
            (3, "Cien años de soledad", 2, 1967, "Novela"),
            (4, "El laberinto de la soledad", 3, 1950, "Ensayo"),
        ]),
        Tabla("prestamos", "Préstamos de libros", [
            _col("id_prestamo", "INT", "id", "Id del préstamo", pk=True),
            _col("id_libro", "INT", "id", "Libro prestado", fk="libros.id_libro"),
            _col("fecha_prestamo", "DATE", "fecha", "Fecha del préstamo"),
            _col("dias", "INT", "numero", "Días de préstamo"),
        ], filas=[
            (1, 1, "2024-03-01", 7),
            (2, 3, "2024-03-05", 14),
            (3, 1, "2024-04-10", 7),
            (4, 4, "2024-05-01", 21),
        ]),
    ],
))

# --- 4. Escuela / notas (español) -----------------------------------------
_reg_train(Esquema(
    "escuela", "Centro educativo: estudiantes, cursos y notas.",
    [
        Tabla("estudiantes", "Estudiantes inscritos", [
            _col("id_est", "INT", "id", "Id del estudiante", pk=True),
            _col("nombre", "VARCHAR(100)", "texto", "Nombre"),
            _col("grado", "VARCHAR(20)", "categoria", "Grado",
                 valores=["1ro", "2do", "3ro"]),
        ], filas=[
            (1, "Pedro", "1ro"), (2, "Lucía", "1ro"),
            (3, "Jorge", "2do"), (4, "Sofía", "3ro"),
        ]),
        Tabla("cursos", "Cursos impartidos", [
            _col("id_curso", "INT", "id", "Id del curso", pk=True),
            _col("nombre", "VARCHAR(80)", "texto", "Nombre del curso"),
            _col("creditos", "INT", "numero", "Créditos del curso"),
        ], filas=[
            (1, "Matemática", 4), (2, "Historia", 3), (3, "Ciencias", 4),
        ]),
        Tabla("notas", "Notas de los estudiantes por curso", [
            _col("id_nota", "INT", "id", "Id de la nota", pk=True),
            _col("id_est", "INT", "id", "Estudiante", fk="estudiantes.id_est"),
            _col("id_curso", "INT", "id", "Curso", fk="cursos.id_curso"),
            _col("nota", "DECIMAL(5,2)", "numero", "Nota de 0 a 100"),
        ], filas=[
            (1, 1, 1, "85.00"), (2, 1, 2, "70.00"), (3, 2, 1, "90.00"),
            (4, 3, 3, "60.00"), (5, 4, 1, "95.00"), (6, 4, 3, "88.00"),
        ]),
    ],
))

# --- 5. Hospital / clínica (inglés abreviado) -----------------------------
_reg_train(Esquema(
    "clinic", "Clinic: patients, doctors and visits.",
    [
        Tabla("doctor", "Doctors", [
            _col("doc_id", "INT", "id", "Doctor id", pk=True),
            _col("dname", "VARCHAR(80)", "texto", "Doctor name"),
            _col("spec", "VARCHAR(50)", "categoria", "Specialty",
                 valores=["Cardiology", "Pediatrics", "General"]),
        ], filas=[
            (1, "Dr. House", "General"), (2, "Dr. Grey", "Cardiology"),
            (3, "Dr. Wilson", "Pediatrics"),
        ]),
        Tabla("patient", "Patients", [
            _col("pat_id", "INT", "id", "Patient id", pk=True),
            _col("pname", "VARCHAR(80)", "texto", "Patient name"),
            _col("age", "INT", "numero", "Age in years"),
            _col("city", "VARCHAR(40)", "categoria", "City",
                 valores=["Guatemala", "Mixco", "Villa Nueva"]),
        ], filas=[
            (1, "John", 45, "Guatemala"), (2, "Mary", 30, "Mixco"),
            (3, "Peter", 8, "Villa Nueva"), (4, "Sara", 60, "Guatemala"),
        ]),
        Tabla("visit", "Clinic visits", [
            _col("vid", "INT", "id", "Visit id", pk=True),
            _col("pat_id", "INT", "id", "Patient", fk="patient.pat_id"),
            _col("doc_id", "INT", "id", "Doctor", fk="doctor.doc_id"),
            _col("vdate", "DATE", "fecha", "Visit date"),
            _col("cost", "DECIMAL(10,2)", "numero", "Visit cost"),
        ], filas=[
            (1, 1, 1, "2024-01-10", "150.00"),
            (2, 2, 2, "2024-02-15", "300.00"),
            (3, 3, 3, "2024-03-20", "100.00"),
            (4, 1, 2, "2024-04-01", "320.00"),
            (5, 4, 1, "2024-05-05", "180.00"),
        ]),
    ],
))

# --- 6. Restaurante (español) ---------------------------------------------
_reg_train(Esquema(
    "restaurante", "Restaurante: platos, meseros y ventas.",
    [
        Tabla("platos", "Platos del menú", [
            _col("id_plato", "INT", "id", "Id del plato", pk=True),
            _col("nombre", "VARCHAR(80)", "texto", "Nombre del plato"),
            _col("tipo", "VARCHAR(30)", "categoria", "Tipo de plato",
                 valores=["Entrada", "Fuerte", "Postre", "Bebida"]),
            _col("precio", "DECIMAL(8,2)", "numero", "Precio"),
        ], filas=[
            (1, "Sopa", "Entrada", "25.00"), (2, "Pepián", "Fuerte", "55.00"),
            (3, "Flan", "Postre", "20.00"), (4, "Jugo", "Bebida", "15.00"),
        ]),
        Tabla("meseros", "Meseros del restaurante", [
            _col("id_mesero", "INT", "id", "Id del mesero", pk=True),
            _col("nombre", "VARCHAR(60)", "texto", "Nombre"),
            _col("turno", "VARCHAR(20)", "categoria", "Turno",
                 valores=["Mañana", "Tarde", "Noche"]),
        ], filas=[
            (1, "Rosa", "Mañana"), (2, "Juan", "Tarde"), (3, "Mario", "Noche"),
        ]),
        Tabla("ventas", "Ventas de platos", [
            _col("id_venta", "INT", "id", "Id de la venta", pk=True),
            _col("id_plato", "INT", "id", "Plato vendido", fk="platos.id_plato"),
            _col("id_mesero", "INT", "id", "Mesero", fk="meseros.id_mesero"),
            _col("cantidad", "INT", "numero", "Cantidad vendida"),
            _col("fecha", "DATE", "fecha", "Fecha de la venta"),
        ], filas=[
            (1, 2, 1, 3, "2024-06-01"), (2, 1, 1, 2, "2024-06-01"),
            (3, 3, 2, 5, "2024-06-02"), (4, 2, 3, 1, "2024-06-03"),
            (5, 4, 2, 4, "2024-06-03"),
        ]),
    ],
))

# --- 7. Gimnasio (español) ------------------------------------------------
_reg_train(Esquema(
    "gimnasio", "Gimnasio: socios, membresías y asistencias.",
    [
        Tabla("socios", "Socios del gimnasio", [
            _col("id_socio", "INT", "id", "Id del socio", pk=True),
            _col("nombre", "VARCHAR(80)", "texto", "Nombre"),
            _col("plan", "VARCHAR(20)", "categoria", "Plan de membresía",
                 valores=["Básico", "Plus", "Premium"]),
            _col("cuota", "DECIMAL(8,2)", "numero", "Cuota mensual"),
            _col("fecha_alta", "DATE", "fecha", "Fecha de alta"),
        ], filas=[
            (1, "Diego", "Básico", "150.00", "2024-01-05"),
            (2, "Elena", "Premium", "450.00", "2024-02-10"),
            (3, "Fabio", "Plus", "300.00", "2024-02-20"),
            (4, "Gaby", "Básico", "150.00", "2024-03-15"),
        ]),
        Tabla("asistencias", "Registro de asistencias", [
            _col("id_asis", "INT", "id", "Id de asistencia", pk=True),
            _col("id_socio", "INT", "id", "Socio", fk="socios.id_socio"),
            _col("fecha", "DATE", "fecha", "Fecha de asistencia"),
            _col("minutos", "INT", "numero", "Minutos de entrenamiento"),
        ], filas=[
            (1, 1, "2024-03-01", 60), (2, 1, "2024-03-03", 45),
            (3, 2, "2024-03-01", 90), (4, 3, "2024-03-02", 30),
            (5, 2, "2024-03-05", 75),
        ]),
    ],
))

# --- 8. Flota de vehículos (inglés abreviado) -----------------------------
_reg_train(Esquema(
    "fleet", "Vehicle fleet: cars and trips.",
    [
        Tabla("car", "Fleet vehicles", [
            _col("car_id", "INT", "id", "Car id", pk=True),
            _col("plate", "VARCHAR(12)", "texto", "License plate"),
            _col("brand", "VARCHAR(30)", "categoria", "Brand",
                 valores=["Toyota", "Nissan", "Ford"]),
            _col("year", "INT", "numero", "Model year"),
        ], filas=[
            (1, "P-001ABC", "Toyota", 2020), (2, "P-002DEF", "Nissan", 2019),
            (3, "P-003GHI", "Ford", 2021),
        ]),
        Tabla("trip", "Trips made", [
            _col("trip_id", "INT", "id", "Trip id", pk=True),
            _col("car_id", "INT", "id", "Car", fk="car.car_id"),
            _col("km", "DECIMAL(8,2)", "numero", "Distance in km"),
            _col("tdate", "DATE", "fecha", "Trip date"),
        ], filas=[
            (1, 1, "120.50", "2024-07-01"), (2, 1, "80.00", "2024-07-02"),
            (3, 2, "200.00", "2024-07-01"), (4, 3, "50.25", "2024-07-03"),
            (5, 2, "150.00", "2024-07-05"),
        ]),
    ],
))

# --- 9. Hotel (español) ---------------------------------------------------
_reg_train(Esquema(
    "hotel", "Hotel: habitaciones y reservas.",
    [
        Tabla("habitaciones", "Habitaciones del hotel", [
            _col("id_hab", "INT", "id", "Id de la habitación", pk=True),
            _col("tipo", "VARCHAR(20)", "categoria", "Tipo de habitación",
                 valores=["Individual", "Doble", "Suite"]),
            _col("precio_noche", "DECIMAL(8,2)", "numero", "Precio por noche"),
        ], filas=[
            (1, "Individual", "250.00"), (2, "Doble", "400.00"),
            (3, "Suite", "800.00"), (4, "Doble", "400.00"),
        ]),
        Tabla("reservas", "Reservas de habitaciones", [
            _col("id_reserva", "INT", "id", "Id de la reserva", pk=True),
            _col("id_hab", "INT", "id", "Habitación", fk="habitaciones.id_hab"),
            _col("huesped", "VARCHAR(80)", "texto", "Nombre del huésped"),
            _col("noches", "INT", "numero", "Número de noches"),
            _col("fecha_entrada", "DATE", "fecha", "Fecha de entrada"),
        ], filas=[
            (1, 3, "Ana", 2, "2024-08-01"), (2, 1, "Luis", 5, "2024-08-03"),
            (3, 2, "Marta", 1, "2024-08-10"), (4, 3, "Pablo", 3, "2024-09-01"),
        ]),
    ],
))

# --- 10. Red social (español) ---------------------------------------------
_reg_train(Esquema(
    "red_social", "Red social: usuarios y publicaciones.",
    [
        Tabla("usuarios", "Usuarios de la red", [
            _col("id_usuario", "INT", "id", "Id del usuario", pk=True),
            _col("usuario", "VARCHAR(40)", "texto", "Nombre de usuario"),
            _col("pais", "VARCHAR(40)", "categoria", "País",
                 valores=["Guatemala", "El Salvador", "Honduras"]),
            _col("fecha_registro", "DATE", "fecha", "Fecha de registro"),
        ], filas=[
            (1, "ana23", "Guatemala", "2023-05-01"),
            (2, "luisgt", "Guatemala", "2023-06-15"),
            (3, "sv_maria", "El Salvador", "2024-01-10"),
        ]),
        Tabla("publicaciones", "Publicaciones de los usuarios", [
            _col("id_pub", "INT", "id", "Id de la publicación", pk=True),
            _col("id_usuario", "INT", "id", "Autor", fk="usuarios.id_usuario"),
            _col("likes", "INT", "numero", "Cantidad de me gusta"),
            _col("fecha", "DATE", "fecha", "Fecha de publicación"),
        ], filas=[
            (1, 1, 10, "2024-02-01"), (2, 1, 25, "2024-02-05"),
            (3, 2, 5, "2024-02-03"), (4, 3, 40, "2024-03-01"),
            (5, 2, 15, "2024-03-10"),
        ]),
    ],
))


# ==========================================================================
# ESQUEMAS DE VALIDACION (2) — NO aparecen en entrenamiento
# ==========================================================================
_reg_val(Esquema(
    "aerolinea", "Aerolínea: vuelos, aviones y pasajeros.",
    [
        Tabla("aviones", "Aviones de la flota", [
            _col("id_avion", "INT", "id", "Id del avión", pk=True),
            _col("modelo", "VARCHAR(40)", "texto", "Modelo del avión"),
            _col("capacidad", "INT", "numero", "Número de asientos"),
            _col("aerolinea", "VARCHAR(40)", "categoria", "Aerolínea",
                 valores=["Avianca", "Copa", "United"]),
        ], filas=[
            (1, "A320", 180, "Avianca"), (2, "B737", 160, "Copa"),
            (3, "E190", 100, "Avianca"),
        ]),
        Tabla("vuelos", "Vuelos programados", [
            _col("id_vuelo", "INT", "id", "Id del vuelo", pk=True),
            _col("id_avion", "INT", "id", "Avión", fk="aviones.id_avion"),
            _col("origen", "VARCHAR(40)", "categoria", "Ciudad de origen",
                 valores=["Guatemala", "Panamá", "Miami"]),
            _col("destino", "VARCHAR(40)", "categoria", "Ciudad de destino",
                 valores=["Guatemala", "Panamá", "Miami"]),
            _col("fecha", "DATE", "fecha", "Fecha del vuelo"),
            _col("precio", "DECIMAL(10,2)", "numero", "Precio del boleto"),
        ], filas=[
            (1, 1, "Guatemala", "Panamá", "2024-09-01", "1200.00"),
            (2, 2, "Panamá", "Miami", "2024-09-02", "2500.00"),
            (3, 1, "Guatemala", "Miami", "2024-09-05", "3000.00"),
            (4, 3, "Guatemala", "Panamá", "2024-09-10", "1100.00"),
        ]),
        Tabla("pasajeros", "Pasajeros por vuelo", [
            _col("id_pasajero", "INT", "id", "Id del pasajero", pk=True),
            _col("id_vuelo", "INT", "id", "Vuelo", fk="vuelos.id_vuelo"),
            _col("nombre", "VARCHAR(80)", "texto", "Nombre del pasajero"),
            _col("edad", "INT", "numero", "Edad del pasajero"),
        ], filas=[
            (1, 1, "Ana", 34), (2, 1, "Luis", 28), (3, 2, "María", 45),
            (4, 3, "Carlos", 50), (5, 3, "Sofía", 19), (6, 4, "Pedro", 60),
        ]),
    ],
))

_reg_val(Esquema(
    "banco", "Banco: cuentas, clientes y transacciones.",
    [
        Tabla("clientes_banco", "Clientes del banco", [
            _col("id_cliente", "INT", "id", "Id del cliente", pk=True),
            _col("nombre", "VARCHAR(100)", "texto", "Nombre del cliente"),
            _col("ciudad", "VARCHAR(50)", "categoria", "Ciudad",
                 valores=["Guatemala", "Xela", "Cobán"]),
        ], filas=[
            (1, "Rodrigo", "Guatemala"), (2, "Valeria", "Xela"),
            (3, "Tomás", "Cobán"),
        ]),
        Tabla("cuentas", "Cuentas bancarias", [
            _col("id_cuenta", "INT", "id", "Id de la cuenta", pk=True),
            _col("id_cliente", "INT", "id", "Dueño", fk="clientes_banco.id_cliente"),
            _col("tipo", "VARCHAR(20)", "categoria", "Tipo de cuenta",
                 valores=["Ahorro", "Monetaria"]),
            _col("saldo", "DECIMAL(12,2)", "numero", "Saldo actual"),
        ], filas=[
            (1, 1, "Ahorro", "15000.00"), (2, 1, "Monetaria", "5000.00"),
            (3, 2, "Ahorro", "22000.00"), (4, 3, "Monetaria", "800.00"),
        ]),
        Tabla("transacciones", "Transacciones de las cuentas", [
            _col("id_tx", "INT", "id", "Id de la transacción", pk=True),
            _col("id_cuenta", "INT", "id", "Cuenta", fk="cuentas.id_cuenta"),
            _col("monto", "DECIMAL(12,2)", "numero", "Monto de la transacción"),
            _col("tipo", "VARCHAR(20)", "categoria", "Tipo",
                 valores=["Depósito", "Retiro"]),
            _col("fecha", "DATE", "fecha", "Fecha de la transacción"),
        ], filas=[
            (1, 1, "2000.00", "Depósito", "2024-07-01"),
            (2, 1, "500.00", "Retiro", "2024-07-10"),
            (3, 3, "10000.00", "Depósito", "2024-07-05"),
            (4, 4, "300.00", "Retiro", "2024-07-15"),
            (5, 2, "1500.00", "Depósito", "2024-08-01"),
        ]),
    ],
))


# ==========================================================================
# Generación de DDL e INSERTs
# ==========================================================================
def ddl_tabla(t: Tabla) -> str:
    lineas = []
    for c in t.columnas:
        pieza = f"  `{c.nombre}` {c.tipo}"
        if c.pk:
            pieza += " NOT NULL"
        if c.comentario:
            pieza += f" COMMENT '{c.comentario}'"
        lineas.append(pieza)
    pks = [c.nombre for c in t.columnas if c.pk]
    if pks:
        lineas.append("  PRIMARY KEY (" + ", ".join(f"`{p}`" for p in pks) + ")")
    for c in t.columnas:
        if c.fk:
            tab_ref, col_ref = c.fk.split(".")
            lineas.append(
                f"  FOREIGN KEY (`{c.nombre}`) REFERENCES `{tab_ref}` (`{col_ref}`)"
            )
    cuerpo = ",\n".join(lineas)
    comentario = f" COMMENT='{t.comentario}'" if t.comentario else ""
    return (
        f"CREATE TABLE `{t.nombre}` (\n{cuerpo}\n) "
        f"ENGINE=InnoDB DEFAULT CHARSET=utf8mb4{comentario};"
    )


def ddl_esquema(e: Esquema) -> str:
    """DDL completo del esquema, estilo SHOW CREATE TABLE."""
    return "\n\n".join(ddl_tabla(t) for t in e.tablas)


def inserts_esquema(e: Esquema) -> str:
    """Sentencias INSERT con los datos de ejemplo (para validar en MySQL)."""
    partes = []
    for t in e.tablas:
        if not t.filas:
            continue
        cols = ", ".join(f"`{c.nombre}`" for c in t.columnas)
        valores = []
        for fila in t.filas:
            vv = []
            for c, v in zip(t.columnas, fila):
                if v is None:
                    vv.append("NULL")
                elif c.tipo.startswith(("INT", "TINYINT", "BIGINT", "DECIMAL")):
                    vv.append(str(v))
                else:
                    vv.append("'" + str(v).replace("'", "''") + "'")
            valores.append("(" + ", ".join(vv) + ")")
        partes.append(
            f"INSERT INTO `{t.nombre}` ({cols}) VALUES\n"
            + ",\n".join(valores) + ";"
        )
    return "\n\n".join(partes)


TODOS = {e.nombre: e for e in ESQUEMAS_ENTRENAMIENTO + ESQUEMAS_VALIDACION}
