import os
import asyncio
from playwright.async_api import async_playwright

async def run_getonboard(params):
    perfiles = params.get("perfiles", [])
    interactive = params.get("interactive", False)
    report_file = params.get("report_file")
    seen_links = params.get("seen_links", set())
    
    print("Iniciando busqueda en GetOnBoard...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not interactive)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        resultados = []

        try:
            # Login manual opcional (para cookies en futuras automatizaciones)
            # await page.goto("https://www.getonbrd.com/login")
            # En GetOnBoard es facil buscar sin login, pero para postular se necesita login
            
            for perfil in perfiles:
                query = perfil.replace(" ", "+")
                url = f"https://www.getonbrd.com/jobs-{query.lower()}?country=chile"
                print(f"Buscando: {url}")
                await page.goto(url)
                
                await page.wait_for_timeout(3000) # Esperar a que cargue
                
                # Buscar contenedores de jobs (ESTO PUEDE CAMBIAR SEGÚN LA WEB)
                jobs = await page.query_selector_all("a.gb-results-list__item")
                
                for job in jobs[:5]: # Probar primeros 5 por perfil
                    try:
                        titulo_elem = await job.query_selector("h4")
                        empresa_elem = await job.query_selector(".size-0")
                        
                        titulo = await titulo_elem.inner_text() if titulo_elem else "N/A"
                        empresa = await empresa_elem.inner_text() if empresa_elem else "N/A"
                        link = await job.get_attribute("href")
                        
                        if not link.startswith("http"):
                            link = "https://www.getonbrd.com" + link
                            
                        # Limpiar saltos de linea
                        titulo = titulo.replace('\n', ' ').strip()
                        empresa = empresa.replace('\n', ' ').strip()
                        
                        # Filtro estricto para Junior / Trainee
                        titulo_chk = titulo.lower()
                        # Filtro estricto Junior (Excluye niveles Mid/Senior)
                        import re
                        excluir = [r"\bsenior\b", r"\bssr\b", r"semi-senior", r"semi senior", r"\bsr\.?\b", r"\blead\b", r"\bjefe\b", r"\bmanager\b", r"principal", r"arquitecto", r"experto", r"specialist", r"especialista", r"coordinador", r"supervisor", r"líder", r"lider", r"director", r"\bhead\b", r"\bvp\b", r"gerente", r"middle", r"mid-level", r"mid level", r"\bmid\b", r"experiencia", r"experienced"]
                        if any(re.search(p, titulo_chk) for p in excluir):
                            continue

                        if link in seen_links:
                            continue
                            
                        seen_links.add(link)
                        
                        resultados.append({
                            "plataforma": "GetOnBoard",
                            "titulo": titulo,
                            "empresa": empresa,
                            "link": link,
                            "estado": "Encontrado - Requiere accion manual / Easy Apply pendiente"
                        })
                    except Exception as e:
                        print(f"Error procesando un trabajo: {e}")
                
        except Exception as e:
            print(f"Error general en GetOnBoard: {e}")
        finally:
            await browser.close()
            
        # Guardar en reporte
        if resultados:
            with open(report_file, "a", encoding="utf-8") as f:
                for res in resultados:
                    # Cuidar las comas en los textos para csv
                    tit = res['titulo'].replace('"', "'").replace(',', ' ')
                    emp = res['empresa'].replace('"', "'").replace(',', ' ')
                    f.write(f"{res['plataforma']},{tit},{emp},{res['link']},{res['estado']}\n")
            print(f"-> {len(resultados)} empleos de GetOnBoard encontrados y guardados.")
