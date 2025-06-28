@echo off

:: Verificar si Python está instalado
echo Verificando instalación de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado en el sistema.
    echo Por favor, instala Python desde https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Crear entorno virtual si no existe
if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
)

:: Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate

:: Instalar dependencias
echo Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt

:: Verificar instalación
echo Verificando instalación de dependencias...
pip list

:: Mensaje de finalización
echo.
echo Instalación completada exitosamente!
echo.
echo Para ejecutar la aplicación:
echo 1. Ejecuta el script start_server.bat
echo 2. O ejecuta python run.py directamente
pause

echo Python encontrado. Versión:
python --version

echo.
echo Instalando dependencias...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Hubo un problema al instalar las dependencias.
    pause
    exit /b 1
)

echo.
echo Todas las dependencias se han instalado correctamente.
echo.
echo Puedes ejecutar la aplicación con:
echo.
echo     cd Clinicaaaaaaaa
echo     python run.py

echo.
pause
