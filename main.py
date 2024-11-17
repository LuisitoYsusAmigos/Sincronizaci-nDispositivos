from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# Configura la conexión a la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'qr'
}

# Crea una función para obtener la conexión a la base de datos
def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection
@app.route("/asignar_dispositivo", methods=['POST'])
def asignar_dispositivo():
    data = request.get_json()
    
    if not data or 'id_usuario' not in data or 'id_dispositivo' not in data:
        return jsonify({"error": "Datos incompletos"}), 400

    id_usuario = data['id_usuario']
    id_dispositivo = data['id_dispositivo']
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Verifica el estado del dispositivo y si ya tiene un propietario
    select_query = "SELECT estado, id_usuario FROM dispositivo WHERE id = %s"
    cursor.execute(select_query, (id_dispositivo,))
    dispositivo = cursor.fetchone()
    
    if dispositivo:
        if dispositivo['id_usuario'] is not None:
            # El dispositivo ya tiene un propietario asignado
            respuesta = "El dispositivo ya tiene un propietario"
        elif dispositivo['estado']:  # Si el estado es True y no tiene propietario
            # Asigna el id_usuario al dispositivo
            update_query = "UPDATE dispositivo SET id_usuario = %s WHERE id = %s"
            cursor.execute(update_query, (id_usuario, id_dispositivo))
            connection.commit()
            respuesta = "Dispositivo asignado exitosamente"
        else:
            # Estado es False, el dispositivo está apagado o necesita reinicio
            respuesta = "Encienda o reinicie su dispositivo"
    else:
        respuesta = "Dispositivo no encontrado"
    
    cursor.close()
    connection.close()
    
    return jsonify({"respuesta": respuesta})



@app.route("/encendidoPlaca", methods=['POST'])
def encender_placa():
    data = request.get_json()
    
    if not data or 'id_dispositivo' not in data:
        return jsonify({"error": "Datos incompletos"}), 400

    id_dispositivo = data['id_dispositivo']
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Verifica si el dispositivo existe
    select_query = "SELECT * FROM dispositivo WHERE id = %s"
    cursor.execute(select_query, (id_dispositivo,))
    dispositivo = cursor.fetchone()
    
    if dispositivo:
        # Si el dispositivo existe, llama al procedimiento almacenado
        try:
            call_query = "CALL activarEstadoTemporal(%s)"
            cursor.execute(call_query, (id_dispositivo,))
            connection.commit()
            respuesta = "Estado activado temporalmente para el dispositivo"
        except mysql.connector.Error as err:
            respuesta = f"Error al ejecutar el procedimiento: {err}"
    else:
        # Si el dispositivo no existe
        respuesta = "No existe ese dispositivo"
    
    cursor.close()
    connection.close()
    
    return jsonify({"respuesta": respuesta})

if __name__ == "__main__":
    app.run(debug=True)
