@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ==========================================
echo    VidScript 版本管理工具
echo    YouTube 財經報告生成器 - 版本控制
echo ==========================================
echo.

cd /d "%~dp0.."

if "%1"=="" (
    echo 📋 使用方法:
    echo.
    echo   查看當前版本:
    echo     version.bat current
    echo.
    echo   增加版本號:
    echo     version.bat increment patch    ^(修復: 1.0.0 → 1.0.1^)
    echo     version.bat increment minor    ^(功能: 1.0.0 → 1.1.0^)
    echo     version.bat increment major    ^(重大: 1.0.0 → 2.0.0^)
    echo.
    echo   設定特定版本:
    echo     version.bat set 2.0.0
    echo.
    echo   生成變更日誌:
    echo     version.bat changelog
    echo.
    echo   發布新版本 ^(增加版本號 + Git 標籤^):
    echo     version.bat release patch "修復bug" "改進性能"
    echo     version.bat release minor "新增功能" "改進介面"
    echo.
    goto :end
)

if "%1"=="current" (
    python tools\version_manager.py --current
    goto :end
)

if "%1"=="changelog" (
    python tools\version_manager.py --changelog
    goto :end
)

if "%1"=="increment" (
    if "%2"=="" (
        echo ❌ 請指定要增加的版本部分 ^(major/minor/patch^)
        goto :end
    )
    
    set "notes_args="
    set "counter=0"
    for %%i in (%*) do (
        set /a counter+=1
        if !counter! GTR 2 (
            set "notes_args=!notes_args! "%%~i""
        )
    )
    
    if defined notes_args (
        python tools\version_manager.py --increment %2 --notes %notes_args%
    ) else (
        python tools\version_manager.py --increment %2
    )
    goto :end
)

if "%1"=="set" (
    if "%2"=="" (
        echo ❌ 請指定版本號 ^(例如: 2.0.0^)
        goto :end
    )
    
    set "notes_args="
    set "counter=0"
    for %%i in (%*) do (
        set /a counter+=1
        if !counter! GTR 2 (
            set "notes_args=!notes_args! "%%~i""
        )
    )
    
    if defined notes_args (
        python tools\version_manager.py --set %2 --notes %notes_args%
    ) else (
        python tools\version_manager.py --set %2
    )
    goto :end
)

if "%1"=="release" (
    if "%2"=="" (
        echo ❌ 請指定要增加的版本部分 ^(major/minor/patch^)
        goto :end
    )
    
    echo 🚀 準備發布新版本...
    echo.
    
    set "notes_args="
    set "counter=0"
    for %%i in (%*) do (
        set /a counter+=1
        if !counter! GTR 2 (
            set "notes_args=!notes_args! "%%~i""
        )
    )
    
    if defined notes_args (
        python tools\version_manager.py --increment %2 --notes %notes_args% --tag
    ) else (
        python tools\version_manager.py --increment %2 --tag
    )
    
    echo.
    echo 📝 生成變更日誌...
    python tools\version_manager.py --changelog
    
    echo.
    echo ✅ 發布完成！
    echo 💡 別忘了推送到 Git 倉庫:
    echo    git push origin master --tags
    goto :end
)

echo ❌ 未知命令: %1
echo 使用 'version.bat' 查看使用說明

:end
echo.
pause
