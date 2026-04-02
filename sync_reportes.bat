@echo off
echo Sincronizando reportes diarios con GitHub...
echo.

echo 1. Descargando reportes creados por el bot en la nube...
git pull origin main

echo.
echo 2. Subiendo reportes creados localmente a la nube...
git add reportes_diarios/*.csv
git commit -m "chore: sincronizar reportes diarios locales con la nube"
git push origin main

echo.
echo Sincronizacion completada!
pause
