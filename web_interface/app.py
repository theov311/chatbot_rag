import os
import sys
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Ajouter le chemin parent aux chemins d'importation Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer les modules du projet RAG
from src.rag import RAGChatbot
from src.evaluation import EvaluationSystem

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# Chemin vers la base de données vectorielle
VECTOR_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             "data", "vectordb")
# Fichier pour stocker les conversations
CONVERSATIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                 "conversations.json")

# Initialiser le chatbot RAG et le système d'évaluation
chatbot = None
evaluator = None

def initialize_chatbot():
    global chatbot, evaluator
    
    # Vérifier si la base de données vectorielle existe
    if not os.path.exists(VECTOR_DB_PATH):
        print("ERREUR: Base de données vectorielle non trouvée. Exécutez d'abord src/main.py.")
        return False
    
    try:
        # Initialiser le chatbot RAG
        chatbot = RAGChatbot(
            vector_db_path=VECTOR_DB_PATH,
            model_name="tinyllama",
            num_passages=4
        )
        
        # Initialiser le système d'évaluation
        evaluator = EvaluationSystem()
        
        print("Chatbot RAG et système d'évaluation initialisés avec succès!")
        return True
    except Exception as e:
        print(f"Erreur lors de l'initialisation du chatbot: {e}")
        return False

# Route principale pour servir index.html
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# Endpoint API pour le chatbot
@app.route("/chat", methods=["POST"])
def chat():
    global chatbot
    
    # Vérifier si le chatbot est initialisé
    if chatbot is None:
        if not initialize_chatbot():
            return jsonify({"error": "Impossible d'initialiser le chatbot. Vérifiez les logs."}), 500
    
    # Récupérer le message de l'utilisateur
    data = request.get_json()
    user_message = data.get("message", "")
    
    if not user_message:
        return jsonify({"error": "Message manquant"}), 400

    try:
        # Obtenir une réponse du chatbot RAG
        response = chatbot.query(user_message)
        
        # Extraire la réponse et les sources
        answer = response["answer"]
        sources = [
            {
                "content": doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content,
                "source": doc.metadata.get("source", "Inconnu"),
                "id": doc.metadata.get("id", "Inconnu")
            }
            for doc in response["source_documents"]
        ]
        
        # Préparer la réponse
        result = {
            "response": answer,
            "sources": sources
        }
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Erreur lors du traitement de la requête: {e}")
        return jsonify({"error": f"Erreur: {str(e)}"}), 500

# Endpoint pour charger les conversations
@app.route("/api/loadConversations", methods=["GET"])
def load_conversations():
    if os.path.exists(CONVERSATIONS_FILE):
        with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as file:
            conversations = json.load(file)
        return jsonify(conversations)
    else:
        return jsonify([])  # Retourne une liste vide si le fichier n'existe pas

# Endpoint pour sauvegarder les conversations
@app.route("/api/saveConversations", methods=["POST"])
def save_conversations():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"error": "Format de données invalide"}), 400

    try:
        with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        return jsonify({"message": "Conversations sauvegardées avec succès"}), 200
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la sauvegarde: {str(e)}"}), 500

# Endpoint pour évaluer une réponse
@app.route("/api/evaluate", methods=["POST"])
def evaluate_response():
    global evaluator
    
    # Vérifier si l'évaluateur est initialisé
    if evaluator is None:
        if not initialize_chatbot():  # Initialise également l'évaluateur
            return jsonify({"error": "Impossible d'initialiser le système d'évaluation"}), 500
    
    data = request.get_json()
    question = data.get("question", "")
    answer = data.get("answer", "")
    rating = data.get("rating", 0)
    feedback = data.get("feedback", "")
    source_ids = data.get("source_ids", [])
    
    if not question or not answer or rating < 1 or rating > 5:
        return jsonify({"error": "Données d'évaluation invalides"}), 400
    
    try:
        # Enregistrer l'évaluation
        eval_data = evaluator.log_evaluation(
            question=question,
            answer=answer,
            rating=rating,
            feedback=feedback,
            source_ids=source_ids
        )
        
        return jsonify({"message": "Évaluation enregistrée avec succès", "data": eval_data}), 200
    except Exception as e:
        return jsonify({"error": f"Erreur lors de l'enregistrement de l'évaluation: {str(e)}"}), 500

if __name__ == "__main__":
    if initialize_chatbot():
        print("Démarrage du serveur web...")
        app.run(host="0.0.0.0", port=5000, debug=True)
    else:
        print("Impossible de démarrer le serveur en raison d'erreurs d'initialisation.")