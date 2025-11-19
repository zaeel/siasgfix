@echo off
setlocal

REM === Caminho do Chrome (ajuste se necessário) ===
set CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"

REM === Diretório do perfil dedicado para Selenium ===
set PROFILE_DIR=C:\temp\SeleniumDataDir

REM === Porta do Remote Debugging ===
set REMOTE_PORT=9222

echo Iniciando Chrome com remote debugging na porta %REMOTE_PORT%...
start "" %CHROME_PATH% --user-data-dir="%PROFILE_DIR%" --remote-debugging-port=%REMOTE_PORT%

endlocal
