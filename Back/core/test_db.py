from database import engine


try:
    connection = engine.connect()
    print("Conexión exitosa a la base de datos mi rey")
    connection.close()
except Exception as e:
    print("❌ Error de conexión:")
    print(e)
