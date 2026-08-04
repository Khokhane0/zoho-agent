@echo off
echo  Installation de Zoho Agent...
echo.

echo  Installation des dépendances backend...
cd backend
pip install -r requirements.txt
echo.

echo  Installation des dépendances frontend...
cd ../frontend
npm install
echo.

echo Création du fichier .env...
cd ..
copy .env.example .env
echo.

echo  N'oublie pas de remplir le fichier .env avec tes clés API !
echo  Modifie le fichier .env avec tes informations.
echo.
echo  Pour démarrer :
echo   1. Backend : cd backend && python main.py
echo   2. Frontend : cd frontend && npm run dev
echo.
pause