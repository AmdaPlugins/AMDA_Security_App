import sys
from pathlib import Path

# Añadir carpeta shared al path
shared_path = Path(__file__).resolve().parent.parent / "shared"
sys.path.append(str(shared_path))

# Verificación de módulos
def verificar_modulos():
    errores = []

    try:
        import loader
        print("✅ loader.py importado correctamente.")
    except Exception as e:
        errores.append(f"❌ Error al importar loader.py: {e}")

    try:
        import registry
        print("✅ registry.py importado correctamente.")
    except Exception as e:
        errores.append(f"❌ Error al importar registry.py: {e}")

    try:
        import phrase
        print("✅ phrase.py importado correctamente.")
    except Exception as e:
        errores.append(f"❌ Error al importar phrase.py: {e}")

    if errores:
        print("\n🔍 Resumen de errores:")
        for err in errores:
            print(err)
    else:
        print("\n🟢 Todos los módulos compartidos están disponibles.")

if __name__ == "__main__":
    verificar_modulos()
