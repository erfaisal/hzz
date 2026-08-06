@echo off
echo Installing CupX Package Manager (hzz)...

:: 1. Create a hidden folder in the user's directory (doesn't require Admin rights)
mkdir "%USERPROFILE%\CupX\hzz" 2>nul

:: 2. Download the core files from your GitHub Pages
echo Downloading core files...
powershell -Command "Invoke-WebRequest -Uri 'https://hzz.cupx.in/install/hzz.py' -OutFile '%USERPROFILE%\CupX\hzz\hzz.py'"
powershell -Command "Invoke-WebRequest -Uri 'https://hzz.cupx.in/install/hzz.bat' -OutFile '%USERPROFILE%\CupX\hzz\hzz.bat'"

:: 3. Tell the terminal that 'hzz' exists (Adding to PATH)
echo Adding hzz to system commands...
powershell -Command "$oldPath = [Environment]::GetEnvironmentVariable('Path', 'User'); if ($oldPath -notlike '*%USERPROFILE%\CupX\hzz*') { [Environment]::SetEnvironmentVariable('Path', \"$oldPath;%USERPROFILE%\CupX\hzz\", 'User') }"

echo Installation Complete!
echo IMPORTANT: Close this terminal and open a NEW terminal to start using 'hzz'.
pause
