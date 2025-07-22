@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

echo ==========================================
echo    YouTube Financial Report Generator v1.0.0
echo    YouTube 財經報告生成器 v1.0.0 - 自動啟動設定
echo ==========================================
echo.

:: Set working directory to batch file location
cd /d "%~dp0"

echo [INFO] 正在設定開機自動啟動...
echo [INFO] Setting up auto-startup on boot...
echo.

:: Get current script directory
set "SCRIPT_DIR=%~dp0"
set "VBS_FILE=%SCRIPT_DIR%Start_Streamlit_Hidden.vbs"

:: Windows Startup folder path
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

:: Create shortcut name
set "SHORTCUT_NAME=YouTube_Report_Generator.lnk"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\%SHORTCUT_NAME%"

echo [INFO] 創建啟動捷徑...
echo [INFO] Creating startup shortcut...

:: Create VBS script to create shortcut
set "CREATE_SHORTCUT_VBS=%TEMP%\create_shortcut.vbs"

echo Set objShell = CreateObject("WScript.Shell") > "%CREATE_SHORTCUT_VBS%"
echo Set objShortcut = objShell.CreateShortcut("%SHORTCUT_PATH%") >> "%CREATE_SHORTCUT_VBS%"
echo objShortcut.TargetPath = "%VBS_FILE%" >> "%CREATE_SHORTCUT_VBS%"
echo objShortcut.WorkingDirectory = "%SCRIPT_DIR%" >> "%CREATE_SHORTCUT_VBS%"
echo objShortcut.Description = "YouTube Financial Report Generator Auto-Start" >> "%CREATE_SHORTCUT_VBS%"
echo objShortcut.Save >> "%CREATE_SHORTCUT_VBS%"

:: Execute the VBS script to create shortcut
cscript //nologo "%CREATE_SHORTCUT_VBS%"

:: Clean up temporary VBS file
del "%CREATE_SHORTCUT_VBS%"

if exist "%SHORTCUT_PATH%" (
    echo.
    echo [SUCCESS] 自動啟動設定完成！
    echo [SUCCESS] Auto-startup setup completed!
    echo.
    echo [INFO] 捷徑已創建於: %SHORTCUT_PATH%
    echo [INFO] Shortcut created at: %SHORTCUT_PATH%
    echo.
    echo [INFO] 應用程式將在下次開機時自動啟動並在後台運行
    echo [INFO] The application will auto-start in background on next boot
    echo [INFO] 您可以透過 http://localhost:8501 訪問應用程式
    echo [INFO] You can access the application at http://localhost:8501
    echo.
    echo [INFO] 如需移除自動啟動，請刪除以下檔案:
    echo [INFO] To remove auto-startup, delete the following file:
    echo       %SHORTCUT_PATH%
) else (
    echo.
    echo [ERROR] 自動啟動設定失敗！
    echo [ERROR] Auto-startup setup failed!
    echo [INFO] 請確認您有足夠的權限寫入啟動資料夾
    echo [INFO] Please ensure you have sufficient permissions to write to startup folder
)

echo.
echo [INFO] 是否要立即測試後台啟動？(Y/N)
echo [INFO] Do you want to test background startup now? (Y/N)
set /p "choice=請選擇 (Please choose): "

if /i "%choice%"=="Y" (
    echo.
    echo [INFO] 正在啟動後台服務...
    echo [INFO] Starting background service...
    cscript //nologo "%VBS_FILE%"
    
    echo.
    echo [INFO] 等待應用程式啟動... (5秒)
    echo [INFO] Waiting for application to start... (5 seconds)
    timeout /t 5 /nobreak >nul
    
    echo [INFO] 檢查應用程式狀態...
    echo [INFO] Checking application status...
    netstat -ano | findstr :8501 >NUL
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] 應用程式已成功啟動！
        echo [SUCCESS] Application started successfully!
        echo [INFO] 請開啟瀏覽器訪問: http://localhost:8501
        echo [INFO] Please open browser and visit: http://localhost:8501
    ) else (
        echo [WARNING] 無法確認應用程式狀態，請檢查日誌檔案
        echo [WARNING] Cannot confirm application status, please check log files
        echo [INFO] 日誌位置: %SCRIPT_DIR%logs\
        echo [INFO] Log location: %SCRIPT_DIR%logs\
    )
)

echo.
pause
