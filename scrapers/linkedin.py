import os
import asyncio
from playwright.async_api import async_playwright

async def run_linkedin(params):
    perfiles = params.get("perfiles", [])
    interactive = params.get("interactive", False)
    report_file = params.get("report_file")
    ubicacion = params.get("ubicacion", "Santiago, Chile")
    seen_links = params.get("seen_links", set())
    
    print("Iniciando busqueda en LinkedIn...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not interactive)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        resultados = []

        try:
            # En LinkedIn, la búsqueda pública (sin login) devuelve resultados diferentes.
            # Para postular, es obligatorio el login, lo cual puede requerir manejo de CAPTCHA o 2FA.
            
            for perfil in perfiles:
                query = perfil.replace(" ", "%20")
                loc = ubicacion.replace(" ", "%20")
                # Filtro f_AL=true es para "Easy Apply", f_E=2 es "Entry level", f_TPR=r2592000 es "Último mes" (30 días)
                url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={loc}&f_AL=true&f_E=2&f_TPR=r2592000"
                
                print(f"Buscando: {url}")
                await page.goto(url)
                await page.wait_for_timeout(3000)
                
                # Cerrar modal de login si aparece en modo publico
                try:
                    dismiss_btn = page.locator("button.cta-modal__dismiss-btn")
                    if await dismiss_btn.is_visible():
                        await dismiss_btn.click()
                except Exception as e:
                    pass
                
                # Buscar tarjetas de trabajo
                lista_jobs = await page.query_selector_all("ul.jobs-search__results-list > li")
                
                for job in lista_jobs[:5]: # Primeros 5 de Easy Apply por perfil
                    try:
                        titulo_elem = await job.query_selector("h3.base-search-card__title")
                        empresa_elem = await job.query_selector("h4.base-search-card__subtitle")
                        link_elem = await job.query_selector("a.base-card__full-link")
                        
                        titulo = await titulo_elem.inner_text() if titulo_elem else "N/A"
                        empresa = await empresa_elem.inner_text() if empresa_elem else "N/A"
                        link = await link_elem.get_attribute("href") if link_elem else "N/A"
                        
                        titulo = titulo.replace('\n', ' ').strip()
                        empresa = empresa.replace('\n', ' ').strip()
                        
                        # Limpiar link para no llevar parametros extras
                        if "?" in link:
                            link = link.split("?")[0]
                        
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
                            "plataforma": "LinkedIn",
                            "titulo": titulo,
                            "empresa": empresa,
                            "link": link,
                            "estado": "Encontrado - Easy Apply potencial"
                        })
                    except Exception as e:
                        print(f"Error procesando un trabajo: {e}")
                
        except Exception as e:
            print(f"Error general en LinkedIn: {e}")
        finally:
            await browser.close()
            
        # Guardar en reporte
        if resultados:
            with open(report_file, "a", encoding="utf-8") as f:
                for res in resultados:
                    tit = res['titulo'].replace('"', "'").replace(',', ' ')
                    emp = res['empresa'].replace('"', "'").replace(',', ' ')
                    f.write(f"{res['plataforma']},{tit},{emp},{res['link']},{res['estado']}\n")
            print(f"-> {len(resultados)} empleos de LinkedIn (Easy Apply) encontrados y guardados.")
