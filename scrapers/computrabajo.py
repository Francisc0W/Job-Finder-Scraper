import os
import asyncio
from playwright.async_api import async_playwright

async def run_computrabajo(params):
    perfiles = params.get("perfiles", [])
    interactive = params.get("interactive", False)
    report_file = params.get("report_file")
    seen_links = params.get("seen_links", set())
    
    print("Iniciando busqueda en Computrabajo...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not interactive)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        resultados = []

        try:
            for perfil in perfiles:
                query = perfil.replace(" ", "-").lower()
                # Filtrando por RM / Santiago y por el ultimo mes (?pubdate=30)
                url = f"https://cl.computrabajo.com/trabajo-de-{query}-en-metropolitana-de-santiago?pubdate=30"
                print(f"Buscando: {url}")
                await page.goto(url)
                
                await page.wait_for_timeout(3000)
                
                jobs = await page.query_selector_all("article.box_offer")
                
                for job in jobs[:5]: # Primeros 5 por perfil
                    try:
                        titulo_elem = await job.query_selector("h1.fs18") or await job.query_selector("h2.fs18") or await job.query_selector("a.js-o-link")
                        empresa_elem = await job.query_selector("p.fs16")
                        enlace_elem = await job.query_selector("a.js-o-link")
                        fecha_elem = await job.query_selector("p.fs13")
                        
                        tiempo_pub = await fecha_elem.inner_text() if fecha_elem else ""
                        
                        titulo = await titulo_elem.inner_text() if titulo_elem else "N/A"
                        empresa = await empresa_elem.inner_text() if empresa_elem else "N/A"
                        link = await enlace_elem.get_attribute("href") if enlace_elem else "N/A"
                        
                        if not link.startswith("http"):
                            link = "https://cl.computrabajo.com" + link
                            
                        # Limpiar saltos de linea
                        titulo = titulo.replace('\n', ' ').strip()
                        empresa = empresa.replace('\n', ' ').strip()
                        
                        # Filtro por antigüedad de más de 30 días
                        if "más de 30" in tiempo_pub.lower() or "más de un mes" in tiempo_pub.lower() or "30+ días" in tiempo_pub.lower():
                            continue
                            
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
                            "plataforma": "Computrabajo",
                            "titulo": titulo,
                            "empresa": empresa,
                            "link": link,
                            "estado": "Encontrado - Requiere aplicar manualmente"
                        })
                    except Exception as e:
                        print(f"Error procesando un trabajo: {e}")
                
        except Exception as e:
            print(f"Error general en Computrabajo: {e}")
        finally:
            await browser.close()
            
        # Guardar en reporte
        if resultados:
            with open(report_file, "a", encoding="utf-8") as f:
                for res in resultados:
                    tit = res['titulo'].replace('"', "'").replace(',', ' ')
                    emp = res['empresa'].replace('"', "'").replace(',', ' ')
                    f.write(f"{res['plataforma']},{tit},{emp},{res['link']},{res['estado']}\n")
            print(f"-> {len(resultados)} empleos de Computrabajo encontrados y guardados.")
