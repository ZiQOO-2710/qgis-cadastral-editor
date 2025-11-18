@echo off
echo ======================================================================
echo 웹맵 로컬 서버 시작
echo ======================================================================
echo.
echo 서버 주소: http://localhost:8000
echo 종료: Ctrl+C
echo.
cd /d C:\Users\ksj27\PROJECTS\QGIS\output\webmap
python -m http.server 8000
