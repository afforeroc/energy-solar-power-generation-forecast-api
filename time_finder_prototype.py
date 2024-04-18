from timezonefinder import TimezoneFinder

def obtain_timezone(latitude, longitude):
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=longitude, lat=latitude)
    return timezone_str

# Ejemplo de uso
latitud = 4.624335  # Ejemplo de latitud (por ejemplo, Nueva York)
longitud = -74.063644  # Ejemplo de longitud (por ejemplo, Nueva York)
timezone = obtener_timezone(latitud, longitud)

if timezone:
    print(f"La latitud {latitud} y longitud {longitud} se encuentra en la zona horaria: {timezone}")
else:
    print(f"No se encontró la zona horaria para la latitud {latitud} y longitud {longitud}")
