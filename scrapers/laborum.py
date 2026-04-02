import os
import asyncio
from playwright.async_api import async_playwright
from utils import es_valido_para_junior

async def run_laborum(params):
    perfiles = params.get("perfiles", [])
    interactive = params.get("interactive", False)
    report_file = params.get("report_file")
    seen_links = params.get("seen_links", set())
    
    print("Iniciando busqueda en Laborum...")

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
                url = f"https://www.laborum.cl/empleos-busqueda-{query}.html"
                print(f"Buscando: {url}")
                await page.goto(url)
                await page.wait_for_timeout(4000)
                
                # Meticuloso: Intentamos varios posibles selectores genéricos de tarjetas de empleo (Navent usa varias clases)
                jobs = await page.query_selector_all("div[id^='react-job']")
                if not jobs:
                    jobs = await page.query_selector_all("a[href*='/empleos/']")
                
                for job in jobs[:5]:
                    try:
                        titulo_elem = await job.query_selector("h2") or await job.query_selector("h3")
                        empresa_elem = await job.query_selector("h3") or await job.query_selector("h4")
                        
                        titulo = await titulo_elem.inner_text() if titulo_elem else "N/A"
                        empresa = await empresa_elem.inner_text() if empresa_elem else "N/A"
                        
                        tag_name = await job.evaluate("el => el.tagName")
                        if tag_name.lower() == "a":
                            link = await job.get_attribute("href")
                        else:
                            enlace_elem = await job.query_selector("a")
                            link = await enlace_elem.get_attribute("href") if enlace_elem else "N/A"
                        
                        if not link or link == "N/A":
                            continue
                            
                        if not link.startswith("http"):
                            link = "https://www.laborum.cl" + link
                            
                        titulo = titulo.replace('\n', ' ').strip()
                        empresa = empresa.replace('\n', ' ').strip()
                        
                        # Filtro estricto Junior
                        titulo_chk = titulo.lower()
                        # Filtro estricto Junior (Excluye niveles Mid/Senior)
                        if not es_valido_para_junior(titulo):
                            continue
                            
                        if link in seen_links:
                            continue
                            
                        seen_links.add(link)
                        
                        resultados.append({
                            "plataforma": "Laborum",
                            "titulo": titulo,
                            "empresa": empresa,
                            "link": link,
                            "estado": "Encontrado - Requiere aplicar manualmente"
                        })
                    except Exception as e:
                        pass
                
        except Exception as e:
            print(f"Error general en Laborum: {e}")
        finally:
            await browser.close()
            
        return resultados
