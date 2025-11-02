@echo off
echo Creating default categories for Forums and Resources...
echo.

cd /d "%~dp0"
python manage.py create_default_categories

echo.
echo ========================================
echo.

REM Note: Resources command needs to be run separately if needed
echo For resource categories, run in Django admin panel at:
echo http://127.0.0.1:8000/admin/resources/resourcecategory/
echo.
pause

