from datetime import datetime
import random
import string

def numero_documento():
    # Fecha y hora en formato compacto
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Generar 6 letras aleatorias del abecedario (mayúsculas)
    letras = ''.join(random.choice(string.ascii_uppercase) for _ in range(6))

    # Unir todo en un solo string
    return f"{timestamp}{letras}"

if __name__=="__main__":
    i = numero_documento()
    print(i)