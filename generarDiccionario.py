import random

nombres = ["Carlos", "Ana", "Luis", "María", "Jorge", "Elena", "Pedro", "Laura", "Sergio", "Marta", "Fernando", "Paula",
           "Rubén", "Sara", "Andrés", "Lucía", "Iván", "Clara", "Manuel", "Rosa", "Alberto", "Patricia", "David",
           "Beatriz", "José", "Noelia", "Adrián", "Carmen", "Miguel", "Eva", "Raúl", "Cristina", "Óscar", "Julia",
           "Víctor", "Nuria", "Pablo", "Andrea", "Jesús", "Lorena", "Hugo", "Isabel", "Álvaro", "Silvia", "Francisco",
           "Gloria", "Diego", "Verónica", "Javier", "Natalia"]

apellidos = ["García", "López", "Martínez", "Rodríguez", "Fernández", "González", "Pérez", "Sánchez", "Ramírez",
             "Torres", "Díaz", "Vargas", "Castro", "Ortiz", "Rubio", "Santos", "Mendoza", "Reyes", "Navarro", "Herrera"]

grado_options = ["Informatica", "Comercio", "Deporte", "Mecanizado"]
fin_options = ["Relacion estable", "Nada serio", "Duda"]
hijos_options = ["Si quiere", "No quiere", "Duda"]

personas = {}

for i in range(1, 51):
    nombre_completo = f"{random.choice(nombres)} {random.choice(apellidos)}"
    edad = random.randint(18, 33)
    sexo = random.choice(["Hombre", "Mujer"])
    grado = random.choice(grado_options)
    fin = random.choice(fin_options)
    hijos = random.choice(hijos_options)

    personas[f"Persona_{i}"] = {
        "NombreCompleto": nombre_completo,
        "Edad": edad,
        "Sexo": sexo,
        "Grado": grado,
        "Fin": fin,
        "Hijos": hijos
    }
print(personas)