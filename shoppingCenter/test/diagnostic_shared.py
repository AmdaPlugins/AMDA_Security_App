﻿import sys
from pathlib import Path

# AÃ±adir carpeta shared al path
shared_path = Path(__file__).resolve().parent.parent / "shared"
sys.path.append(str(shared_path))

# VerificaciÃ³n de mÃ³dulos
def verificar_modulos():
    errores = []

    try:
        from Shared import loader 
        print("âœ… loader.py importado correctamente.")
    except Exception as e:
        errores.append(f"âŒ Error al importar loader.py: {e}")

    try:
        from Shared import registry 
        print("âœ… registry.py importado correctamente.")
    except Exception as e:
        errores.append(f"âŒ Error al importar registry.py: {e}")

    try:
        from Shared import phrase 
        print("âœ… phrase.py importado correctamente.")
    except Exception as e:
        errores.append(f"âŒ Error al importar phrase.py: {e}")

    if errores:
        print("\nðŸ” Resumen de errores:")
        for err in errores:
            print(err)
    else:
        print("\nðŸŸ¢ Todos los mÃ³dulos compartidos estÃ¡n disponibles.")

if __name__ == "__main__":
    verificar_modulos()
