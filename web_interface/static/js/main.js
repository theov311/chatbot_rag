// Variables globales
let conversations = [];
let currentConversationIndex = 0;
let abortController = null;
let lastUserQuestion = "";
let lastBotAnswer = "";
let lastSourceIds = [];

// Initialisation au chargement de la page
document.addEventListener("DOMContentLoaded", async () => {
  hideLoading();
  await loadConversationsFromServer();
  updateConversationTitle();
});

// Gestion des conversations
async function loadConversationsFromServer() {
  try {
    const res = await fetch('/api/loadConversations');
    if (!res.ok) throw new Error(`Erreur HTTP : ${res.status}`);
    conversations = await res.json();
    if (!conversations.length) {
      conversations.push({ title: "Nouvelle conversation", messages: [] });
    }
    updateHistory();
  } catch (err) {
    console.error("Erreur lors du chargement des conversations :", err);
    conversations = [{ title: "Nouvelle conversation", messages: [] }];
    updateHistory();
  }
}

async function saveConversationsToServer() {
  try {
    const res = await fetch('/api/saveConversations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(conversations)
    });
    if (!res.ok) throw new Error(`Erreur HTTP : ${res.status}`);
  } catch (err) {
    console.error("Erreur lors de la sauvegarde des conversations :", err);
  }
}

function startNewConversation() {
  conversations.unshift({ title: "Nouvelle conversation", messages: [] });
  currentConversationIndex = 0;
  updateHistory();
  updateConversationTitle();
  document.getElementById("chat-box").innerHTML = "";
  
  // Masquer les sources s'il y en a
  const sourcesContainer = document.getElementById("sources-container");
  if (sourcesContainer) {
    sourcesContainer.classList.add("hidden");
  }
}

// Communication avec le chatbot
async function sendMessage() {
  const input = document.getElementById("user-input");
  const userMessage = input.value.trim();
  
  if (!userMessage) return;
  
  // Effacer l'input et ajouter le message à l'interface
  input.value = "";
  addMessage("user", userMessage);
  
  // Masquer les sources précédentes s'il y en a
  const sourcesContainer = document.getElementById("sources-container");
  if (sourcesContainer) {
    sourcesContainer.classList.add("hidden");
  }
  
  try {
    showLoading();
    document.getElementById("stop-button").disabled = false;
    
    // Préparer l'annulation de requête
    abortController = new AbortController();
    
    // Envoyer la requête au serveur
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMessage }),
      signal: abortController.signal
    });
    
    if (!response.ok) {
      throw new Error(`Erreur HTTP : ${response.status}`);
    }
    
    // Obtenir la réponse
    const data = await response.json();
    
    // Ajouter la réponse à l'interface
    const botMessage = data.response;
    addMessage("bot", botMessage);
    
    // Sauvegarder la conversation
    conversations[currentConversationIndex].messages.push({
      user: userMessage,
      bot: botMessage
    });
    saveConversationsToServer();
    
    // Afficher les sources si disponibles
    if (data.sources && data.sources.length > 0) {
      lastSourceIds = data.sources.map(source => source.id);
      displaySources(data.sources);
    }
    
    // Enregistrer la dernière question/réponse pour l'évaluation
    lastUserQuestion = userMessage;
    lastBotAnswer = botMessage;
    
    // Ajouter les contrôles d'évaluation
    addFeedbackControls();
    
  } catch (err) {
    if (err.name === "AbortError") {
      addMessage("bot", "[Réponse interrompue]");
    } else {
      console.error("Erreur lors de l'envoi du message :", err);
      addMessage("bot", "[Erreur] Impossible d'obtenir une réponse du serveur.");
    }
  } finally {
    hideLoading();
    document.getElementById("stop-button").disabled = true;
  }
}

function stopResponse() {
  if (abortController) {
    abortController.abort();
    document.getElementById("stop-button").disabled = true;
  }
}

function addMessage(sender, message) {
  const chatBox = document.getElementById("chat-box");
  const messageElement = document.createElement("div");
  messageElement.className = `message ${sender}`;
  
  // Remplacer les sauts de ligne par des balises <br>
  const formattedMessage = message.replace(/\n/g, "<br>");
  messageElement.innerHTML = formattedMessage;
  
  chatBox.appendChild(messageElement);
  chatBox.scrollTop = chatBox.scrollHeight;
  return messageElement;
}

function displaySources(sources) {
  // Créer ou récupérer le conteneur de sources
  let sourcesContainer = document.getElementById("sources-container");
  
  if (!sourcesContainer) {
    sourcesContainer = document.createElement("div");
    sourcesContainer.id = "sources-container";
    sourcesContainer.className = "sources-container";
    document.querySelector('.chat-area').insertBefore(
      sourcesContainer,
      document.querySelector('.input-container')
    );
  }
  
  // Vider le conteneur
  sourcesContainer.innerHTML = "";
  sourcesContainer.classList.remove("hidden");
  
  // Créer l'en-tête des sources
  const sourcesHeader = document.createElement("div");
  sourcesHeader.className = "sources-header";
  
  const sourcesTitle = document.createElement("div");
  sourcesTitle.textContent = "Sources";
  sourcesTitle.className = "sources-title";
  
  const sourcesToggle = document.createElement("div");
  sourcesToggle.textContent = "Masquer";
  sourcesToggle.className = "sources-toggle";
  sourcesToggle.onclick = function() {
    const sourcesList = document.getElementById("sources-list");
    if (sourcesList.classList.contains("hidden")) {
      sourcesList.classList.remove("hidden");
      this.textContent = "Masquer";
    } else {
      sourcesList.classList.add("hidden");
      this.textContent = "Afficher";
    }
  };
  
  sourcesHeader.appendChild(sourcesTitle);
  sourcesHeader.appendChild(sourcesToggle);
  sourcesContainer.appendChild(sourcesHeader);
  
  // Créer la liste des sources
  const sourcesList = document.createElement("div");
  sourcesList.id = "sources-list";
  sourcesList.className = "sources-list";
  
  sources.forEach((source, index) => {
    const sourceItem = document.createElement("div");
    sourceItem.className = "source-item";
    
    const sourceContent = document.createElement("div");
    sourceContent.innerHTML = `<strong>Source ${index+1}:</strong> ${source.content}`;
    
    const sourceMetadata = document.createElement("div");
    sourceMetadata.className = "source-metadata";
    sourceMetadata.textContent = `ID: ${source.id} | Source: ${source.source}`;
    
    sourceItem.appendChild(sourceContent);
    sourceItem.appendChild(sourceMetadata);
    sourcesList.appendChild(sourceItem);
  });
  
  sourcesContainer.appendChild(sourcesList);
}

// Gestion de l'interface utilisateur
function handleKeyPress(event) {
  if (event.key === "Enter") {
    sendMessage();
  }
}

function showLoading() {
  const loadingElement = document.getElementById("loading");
  if (loadingElement) {
    loadingElement.classList.remove("hidden");
  }
}

function hideLoading() {
  const loadingElement = document.getElementById("loading");
  if (loadingElement) {
    loadingElement.classList.add("hidden");
  }
}

function updateHistory() {
  const history = document.getElementById("history");
  history.innerHTML = "";
  
  conversations.forEach((conv, index) => {
    const li = document.createElement("li");
    li.className = "conversation-item";
    if (index === currentConversationIndex) {
      li.classList.add("active");
    }
    
    const titleSpan = document.createElement("span");
    titleSpan.textContent = conv.title || "Sans titre";
    titleSpan.onclick = () => loadConversation(index);
    
    const deleteButton = document.createElement("button");
    deleteButton.className = "delete-button";
    deleteButton.textContent = "🗑️";
    deleteButton.onclick = (e) => {
      e.stopPropagation();
      deleteConversation(index);
    };
    
    li.appendChild(titleSpan);
    li.appendChild(deleteButton);
    history.appendChild(li);
  });
}

function updateConversationTitle() {
  const titleElement = document.getElementById("conversation-title");
  if (conversations.length > currentConversationIndex) {
    titleElement.textContent = conversations[currentConversationIndex].title;
  } else {
    titleElement.textContent = "Nouvelle conversation";
  }
}

function loadConversation(index) {
  currentConversationIndex = index;
  const chatBox = document.getElementById("chat-box");
  chatBox.innerHTML = "";
  
  // Masquer les sources s'il y en a
  const sourcesContainer = document.getElementById("sources-container");
  if (sourcesContainer) {
    sourcesContainer.classList.add("hidden");
  }
  
  const conversation = conversations[index];
  conversation.messages.forEach(msg => {
    addMessage("user", msg.user);
    addMessage("bot", msg.bot);
  });
  
  updateHistory();
  updateConversationTitle();
}

function deleteConversation(index) {
  if (confirm("Êtes-vous sûr de vouloir supprimer cette conversation ?")) {
    conversations.splice(index, 1);
    
    // Si aucune conversation ne reste, en créer une nouvelle
    if (conversations.length === 0) {
      conversations.push({ title: "Nouvelle conversation", messages: [] });
    }
    
    // Ajuster l'index actuel si nécessaire
    if (currentConversationIndex >= conversations.length) {
      currentConversationIndex = 0;
    }
    
    updateHistory();
    loadConversation(currentConversationIndex);
    saveConversationsToServer();
  }
}

function editConversationTitle() {
  if (conversations.length <= currentConversationIndex) return;
  
  const newTitle = prompt("Modifier le titre de la conversation :", 
                          conversations[currentConversationIndex].title);
  
  if (newTitle) {
    conversations[currentConversationIndex].title = newTitle;
    updateConversationTitle();
    updateHistory();
    saveConversationsToServer();
  }
}

function toggleTheme() {
  const body = document.body;
  const themeToggle = document.getElementById("theme-toggle");
  body.classList.toggle("dark-mode");
  themeToggle.textContent = body.classList.contains("dark-mode") ? "Mode clair" : "Mode sombre";
}

// Système d'évaluation
function addFeedbackControls() {
  // Vérifier si l'élément de feedback existe déjà
  let feedbackContainer = document.getElementById("feedback-container");
  
  if (feedbackContainer) {
    feedbackContainer.remove();
  }
  
  // Créer un nouveau conteneur de feedback
  feedbackContainer = document.createElement("div");
  feedbackContainer.id = "feedback-container";
  feedbackContainer.className = "feedback-container";
  
  // Ajouter le texte
  const feedbackLabel = document.createElement("span");
  feedbackLabel.textContent = "Cette réponse était-elle utile ?";
  feedbackContainer.appendChild(feedbackLabel);
  
  // Ajouter les étoiles pour la notation
  const ratingStars = document.createElement("div");
  ratingStars.className = "rating-stars";
  
  for (let i = 1; i <= 5; i++) {
    const star = document.createElement("span");
    star.className = "star";
    star.textContent = "★";
    star.dataset.value = i;
    star.onclick = function() {
      // Mettre à jour les étoiles sélectionnées
      document.querySelectorAll('.star').forEach(s => {
        s.classList.remove('selected');
      });
      
      document.querySelectorAll(`.star[data-value="${i}"], .star[data-value="${i-1}"], .star[data-value="${i-2}"], .star[data-value="${i-3}"], .star[data-value="${i-4}"]`).forEach(s => {
        if (parseInt(s.dataset.value) <= i) {
          s.classList.add('selected');
        }
      });
      
      // Afficher le champ de commentaire
      document.getElementById("feedback-comment").classList.remove("hidden");
      document.getElementById("submit-feedback").classList.remove("hidden");
    };
    
    ratingStars.appendChild(star);
  }
  
  feedbackContainer.appendChild(ratingStars);
  
  // Ajouter un champ pour les commentaires
  const feedbackInput = document.createElement("input");
  feedbackInput.type = "text";
  feedbackInput.placeholder = "Commentaire (optionnel)";
  feedbackInput.className = "feedback-input hidden";
  feedbackInput.id = "feedback-comment";
  feedbackContainer.appendChild(feedbackInput);
  
  // Ajouter le bouton d'envoi
  const submitButton = document.createElement("button");
  submitButton.textContent = "Envoyer";
  submitButton.className = "submit-feedback hidden";
  submitButton.id = "submit-feedback";
  submitButton.onclick = function() {
    // Récupérer la note
    const rating = document.querySelectorAll('.star.selected').length;
    const feedback = feedbackInput.value;
    
    // Envoyer l'évaluation au serveur
    submitFeedback(rating, feedback);
    
    // Masquer les contrôles après envoi
    feedbackContainer.innerHTML = "<span>Merci pour votre évaluation !</span>";
    setTimeout(() => {
      feedbackContainer.remove();
    }, 3000);
  };
  
  feedbackContainer.appendChild(submitButton);
  
  // Ajouter le conteneur de feedback à l'interface
  document.querySelector('.chat-area').insertBefore(
    feedbackContainer,
    document.querySelector('.input-container')
  );
}

async function submitFeedback(rating, feedback) {
  if (rating < 1 || rating > 5) return;
  
  try {
    const response = await fetch('/api/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: lastUserQuestion,
        answer: lastBotAnswer,
        rating: rating,
        feedback: feedback,
        source_ids: lastSourceIds
      })
    });
    
    if (!response.ok) {
      throw new Error(`Erreur HTTP : ${response.status}`);
    }
    
    console.log('Évaluation envoyée avec succès');
  } catch (err) {
    console.error('Erreur lors de l\'envoi de l\'évaluation:', err);
  }
}