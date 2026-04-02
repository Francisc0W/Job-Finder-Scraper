import asyncio
import os
import argparse
from datetime import datetime
from dotenv import load_dotenv

from scrapers.getonboard import run_getonboard
from scrapers.linkedin import run_linkedin
from scrapers.computrabajo import run_computrabajo
from scrapers.laborum import run_laborum
from scrapers.trabajando import run_trabajando
from scrapers.bne import run_bne
from scrapers.glassdoor import run_glassdoor

# Cargar variables de entorno (para credenciales si son necesarias)
load_dotenv()

async def main():
    print("==================================================")
    print(f"Iniciando Job Automation Bot - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==================================================\n")

    # Asegurar que exista el directorio de reportes
    os.makedirs("reportes_diarios", exist_ok=True)
    report_file = f"reportes_diarios/reporte_{datetime.now().strftime('%Y-%m-%d')}.csv"

    # Si no existe, crear el archivo con encabezados
    if not os.path.exists(report_file):
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("Plataforma,Titulo,Empresa,Link,Estado\n")

    # Cargar enlaces ya vistos para no repetir
    seen_links = set()
    for file in os.listdir("reportes_diarios"):
        if file.endswith(".csv"):
            try:
                with open(os.path.join("reportes_diarios", file), "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split(",")
                        for p in parts:
                            if p.startswith("http"):
                                seen_links.add(p)
            except Exception:
                pass

    parser = argparse.ArgumentParser(description="Bot de Postulación de Empleos")
    parser.add_argument("--platform", choices=["all", "getonboard", "linkedin", "computrabajo", "laborum", "trabajando", "bne", "glassdoor"], default="all", help="Plataforma a usar")
    parser.add_argument("--interactive", action="store_true", help="Abrir el navegador para iniciar sesión o ver visualmente")
    
    args = parser.parse_args()

    perfiles_buscar = ["Data Scientist", "Data Analyst", "Business Intelligence", "DevOps", "RevOps"]
    
    # Parámetros compartidos
    params = {
        "perfiles": perfiles_buscar,
        "ubicacion": "Santiago, Chile",
        "experiencia": "Junior",
        "interactive": args.interactive,
        "report_file": report_file,
        "seen_links": seen_links
    }

    if args.platform in ["all", "getonboard"]:
        print("\n--- Ejecutando Scraper de GetOnBoard ---")
        await run_getonboard(params)
        
    if args.platform in ["all", "linkedin"]:
        print("\n--- Ejecutando Scraper de LinkedIn ---")
        await run_linkedin(params)
        
    if args.platform in ["all", "computrabajo"]:
        print("\n--- Ejecutando Scraper de Computrabajo ---")
        await run_computrabajo(params)
        
    if args.platform in ["all", "laborum"]:
        print("\n--- Ejecutando Scraper de Laborum ---")
        await run_laborum(params)
        
    if args.platform in ["all", "trabajando"]:
        print("\n--- Ejecutando Scraper de Trabajando.com ---")
        await run_trabajando(params)
        
    if args.platform in ["all", "bne"]:
        print("\n--- Ejecutando Scraper de BNE (Bolsa Nacional de Empleo) ---")
        await run_bne(params)
        
    if args.platform in ["all", "glassdoor"]:
        print("\n--- Ejecutando Scraper de Glassdoor ---")
        await run_glassdoor(params)
    
    print("\n==================================================")
    print("Ejecución finalizada. Reporte guardado en:")
    print(os.path.abspath(report_file))
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
