# Chatbot RAG LangChain

Ce projet implémente un chatbot basé sur l'architecture RAG (Retrieval-Augmented Generation) utilisant la bibliothèque LangChain, capable de répondre à des questions concernant la documentation de LangChain.

## Architecture du projet

```
.
├── data/
│   ├── input/            # Données d'entrée (fichiers JSONL)
│   └── vectordb/         # Base de données vectorielle persistante
├── logs/                 # Journaux d'évaluation
├── src/
│   ├── chatbot.py        # Interface en ligne de commande pour le chatbot
│   ├── embedding.py      # Outils pour la création d'embeddings et de la base vectorielle
│   ├── evaluation.py     # Système d'évaluation des réponses
│   ├── main.py           # Script principal pour traiter les documents
│   ├── rag.py            # Implémentation du chatbot RAG
│   └── utils.py          # Fonctions utilitaires
└── web_interface/
    ├── app.py            # Serveur web Flask
    ├── static/           # Fichiers statiques (CSS, JS, HTML)
    └── conversations.json # Historique des conversations
```

## Choix techniques

1. **LangChain** : Framework pour construire des applications basées sur des LLM (Large Language Models).
2. **Ollama** : Pour exécuter des modèles de langage localement.
3. **HuggingFace Embeddings** : Modèle `all-MiniLM-L6-v2` pour la génération d'embeddings de haute qualité avec des ressources limitées.
4. **Chroma DB** : Base de données vectorielle pour stocker et rechercher des embeddings.
5. **Flask** : Serveur web léger pour l'interface utilisateur web.

## Flux de fonctionnement

1. **Indexation** :
   - Les documents JSONL de la documentation LangChain sont chargés
   - Découpage des documents en chunks plus petits
   - Génération des embeddings pour chaque chunk
   - Stockage dans la base de données vectorielle ChromaDB

2. **Interrogation** :
   - La question de l'utilisateur est transformée en embedding
   - Recherche des passages les plus similaires dans la base vectorielle
   - Les passages sont injectés dans un prompt avec la question
   - Le LLM (via Ollama) génère une réponse basée sur ces informations

3. **Évaluation** :
   - L'utilisateur peut évaluer la qualité des réponses (1-5 étoiles)
   - Les évaluations sont enregistrées pour amélioration future

## Prérequis

- Python 3.8+
- Ollama installé localement avec le modèle `tinyllama` (ou autre modèle compatible)

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/theov311/chatbot_rag.git
cd exam_ia
```

2. Créez un environnement virtuel et activez-le :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Téléchargez les données de la documentation LangChain :
```bash
mkdir -p data/input
# Téléchargez le fichier train.jsonl depuis https://huggingface.co/datasets/antonioibars/langchain-docs
# et placez-le dans data/input/ si ce n'est pas déjà fait.
```

5. Créez la base de données vectorielle :
```bash
python src/main.py
```

## Utilisation

### Interface en ligne de commande
```bash
python src/chatbot.py
```

### Interface web
```bash
cd web_interface
pip install -r requirements_web.txt
python app.py
```
Puis ouvrez votre navigateur à l'adresse http://localhost:5000

## Fonctionnalités

- Réponse à des questions sur la documentation LangChain
- Affichage des sources utilisées pour générer la réponse
- Historique des conversations
- Évaluation des réponses par l'utilisateur
- Mode sombre/clair pour l'interface web
