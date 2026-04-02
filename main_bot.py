import asyncio
import os
import argparse
import csv
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

    resultados_totales = []

    if args.platform in ["all", "getonboard"]:
        print("\n--- Ejecutando Scraper de GetOnBoard ---")
        res = await run_getonboard(params)
        if res: resultados_totales.extend(res)
        
    if args.platform in ["all", "linkedin"]:
        print("\n--- Ejecutando Scraper de LinkedIn ---")
        res = await run_linkedin(params)
        if res: resultados_totales.extend(res)
        
    if args.platform in ["all", "computrabajo"]:
        print("\n--- Ejecutando Scraper de Computrabajo ---")
        res = await run_computrabajo(params)
        if res: resultados_totales.extend(res)
        
    if args.platform in ["all", "laborum"]:
        print("\n--- Ejecutando Scraper de Laborum ---")
        res = await run_laborum(params)
        if res: resultados_totales.extend(res)
        
    if args.platform in ["all", "trabajando"]:
        print("\n--- Ejecutando Scraper de Trabajando.com ---")
        res = await run_trabajando(params)
        if res: resultados_totales.extend(res)
        
    if args.platform in ["all", "bne"]:
        print("\n--- Ejecutando Scraper de BNE (Bolsa Nacional de Empleo) ---")
        res = await run_bne(params)
        if res: resultados_totales.extend(res)
        
    if args.platform in ["all", "glassdoor"]:
        print("\n--- Ejecutando Scraper de Glassdoor ---")
        res = await run_glassdoor(params)
        if res: resultados_totales.extend(res)
    
    print("\n==================================================")
    print("Guardando resultados en CSV...")
    
    if resultados_totales:
        file_exists = os.path.exists(report_file)
        with open(report_file, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Plataforma", "Titulo", "Empresa", "Link", "Estado"])
                
            for res in resultados_totales:
                writer.writerow([
                    res.get("plataforma", ""),
                    res.get("titulo", ""),
                    res.get("empresa", ""),
                    res.get("link", ""),
                    res.get("estado", "")
                ])
        print(f"-> {len(resultados_totales)} empleos nuevos guardados en total.")
    else:
        print("-> No se encontraron empleos nuevos u ofertas no vistas.")

    print(f"Ejecución finalizada. Reporte guardado en:")
    print(os.path.abspath(report_file))
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
