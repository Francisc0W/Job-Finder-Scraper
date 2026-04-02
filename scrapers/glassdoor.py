import os
import asyncio
from playwright.async_api import async_playwright
from utils import es_valido_para_junior

async def run_glassdoor(params):
    perfiles = params.get("perfiles", [])
    interactive = params.get("interactive", False)
    report_file = params.get("report_file")
    seen_links = params.get("seen_links", set())
    
    print("Iniciando busqueda en Glassdoor...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not interactive)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        resultados = []

        try:
            for perfil in perfiles:
                query = perfil.replace(" ", "%20")
                url = f"https://www.glassdoor.cl/Empleo/buscar-empleos.htm?sc.keyword={query}&locT=C&locId=2538186&locKeyword=Santiago"
                print(f"Buscando: {url}")
                await page.goto(url)
                await page.wait_for_timeout(5000)
                
                # Meticuloso: Selectores de listas de empleos generalistas de Glassdoor
                jobs = await page.query_selector_all("li.react-job-listing, li[data-test='jobListing'], article#MainCol div ul li")
                
                for job in jobs[:5]:
                    try:
                        titulo_elem = await job.query_selector("a[data-test='job-title'], a.jobLink, .job-title")
                        empresa_elem = await job.query_selector("span[data-test='emp-name'], .employerName, .EmployerProfile_employerName__nE1y2")
                        
                        titulo = await titulo_elem.inner_text() if titulo_elem else "N/A"
                        empresa = await empresa_elem.inner_text() if empresa_elem else "N/A"
                        
                        tag_name = await job.evaluate("el => el.tagName")
                        if tag_name.lower() == "a":
                            link = await job.get_attribute("href")
                        else:
                            enlace_elem = await job.query_selector("a[data-test='job-link'], a.jobLink")
                            if not enlace_elem:
                                enlace_elem = await job.query_selector("a")
                            link = await enlace_elem.get_attribute("href") if enlace_elem else "N/A"
                        
                        if not link or link == "N/A":
                            continue
                            
                        if link.startswith("/"):
                            link = "https://www.glassdoor.cl" + link
                            
                        # Limpiar salto de linea
                        titulo = titulo.replace('\n', ' ').strip()
                        empresa = empresa.replace('\n', ' ').strip()
                        
                        # Remover cosas como puntajes del nombre de empresa (Glassdoor suele tener ej: Walmart 3.4*)
                        if "★" in empresa:
                            empresa = empresa.split("★")[0].strip()
                            
                        # Filtro estricto Junior
                        titulo_chk = titulo.lower()
                        # Filtro estricto Junior (Excluye niveles Mid/Senior)
                        if not es_valido_para_junior(titulo):
                            continue
                            
                        if link in seen_links:
                            continue
                            
                        seen_links.add(link)
                        
                        resultados.append({
                            "plataforma": "Glassdoor",
                            "titulo": titulo,
                            "empresa": empresa,
                            "link": link,
                            "estado": "Encontrado - Requiere aplicar manualmente"
                        })
                    except Exception as e:
                        pass
                
        except Exception as e:
            print(f"Error general en Glassdoor: {e}")
        finally:
            await browser.close()
            
        return resultados
