@echo off
title HAME Enterprise - Auto Installer & Setup
chcp 65001 >nul
color 0B
cd /d "%~dp0"

echo =====================================================================
echo    🚀 HAME ENTERPRISE - BỘ CÀI ĐẶT TỰ ĐỘNG CHO MÁY TÍNH MỚI
echo =====================================================================
echo.
echo Đang kiểm tra môi trường Python trên máy...

where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    where py >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [!] May tinh chua co Python.
        echo [*] Dang tu dong tai Python 3.10 tu python.org...
        powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe' -OutFile 'python_setup.exe'"
        echo [*] Dang cai dat Python tu dong vao may (Vui long doi 1-2 phut)...
        python_setup.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 SimpleInstall=1
        del /f /q python_setup.exe >nul 2>&1
        echo [OK] Da cai dat xong Python!
        set "PATH=%LOCALAPPDATA%\Programs\Python\Python310;%LOCALAPPDATA%\Programs\Python\Python310\Scripts;%PATH%"
    )
)

echo.
echo [*] Dang cai dat cac thu vien can thiet (requirements.txt)...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo [*] Dang khoi tao Co so du lieu SQLite noi bo...
python -c "import database; database.init_db(); import customer_memory; customer_memory.init_customer_memory_db()"

echo.
echo [*] Dang tao loi tat ngoai man hinh Desktop...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([System.IO.Path]::Combine([System.Environment]::GetFolderPath('Desktop'), 'FBPoster Enterprise.lnk')); $s.TargetPath = [System.IO.Path]::Combine('%~dp0', 'KHOI_DONG_PHAN_MEM.bat'); $s.WorkingDirectory = '%~dp0'; $s.Description = 'FBPoster Enterprise'; $s.Save()"

echo.
echo =====================================================================
echo    ✅ CAI DAT HOAN TAT! DANG MO PHAN MEM TREN MAY TINH CUA BAN...
echo =====================================================================
echo.
start KHOI_DONG_PHAN_MEM.bat
exit
