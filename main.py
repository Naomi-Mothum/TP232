import uvicorn
from app.main import app

if __name__ == "__main__":
    print("Démarrage du serveur EduAnalysis sur http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
