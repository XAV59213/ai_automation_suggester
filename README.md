Grok Automation Suggester
Une intégration Home Assistant qui utilise l’IA Grok de xAI pour générer des suggestions d’automatisations intelligentes et fun pour votre maison connectée. Inspirée par le Guide du voyageur galactique et JARVIS de Iron Man, cette intégration apporte une touche d’humour et de créativité à vos automations YAML ! 🚀
Fonctionnalités

Suggestions IA : Génère des automations basées sur vos entités, zones et appareils.
Style Grok : Prompts personnalisés avec de l’humour et une vibe intergalactique.
Notifications persistantes : Recevez des suggestions directement dans Home Assistant.
Capteurs : Suivez les suggestions et l’état via des capteurs (sensor.grok_automation_suggestions, sensor.grok_automation_status).
Configuration simple : Utilise uniquement l’API Grok, facile à configurer via l’interface UI.

Installation

Via HACS :
Ajoutez ce dépôt comme dépôt personnalisé dans HACS (https://github.com/XAV59213/grok_automation_suggester).
Recherchez "Grok Automation Suggester" et installez.


Manuelle :
Copiez le dossier custom_components/grok_automation_suggester/ dans votre répertoire custom_components/ de Home Assistant.
Redémarrez Home Assistant.



Configuration

Allez dans Settings > Devices & Services > Add Integration.
Sélectionnez Grok Automation Suggester.
Entrez votre clé API Grok (obtenue sur https://console.x.ai).
Configurez les paramètres optionnels (modèle, tokens max).
Validez pour activer l’intégration.

Utilisation

Service : Appelez le service grok_automation_suggester.generate_suggestions pour générer des suggestions manuellement.
Paramètres :
all_entities (boolean) : Analyse toutes les entités ou seulement les nouvelles.
custom_prompt (string, facultatif) : Ajoute un prompt personnalisé pour guider les suggestions (ex. "Crée des automatisations pour économiser l’énergie").




Automatisation : Une automatisation exemple (grok_new_entity_automation.yaml) est incluse pour déclencher des suggestions sur de nouvelles entités.
Capteurs :
sensor.grok_automation_suggestions : Contient les suggestions et le YAML généré.
sensor.grok_automation_status : Affiche l’état de connexion à l’API Grok.



Obtenir une clé API
Pour utiliser cette intégration, vous avez besoin d’une clé API Grok. Rendez-vous sur https://console.x.ai pour en obtenir une.
Exemple de suggestion
Yo, j’ai scanné ton salon et trouvé light.living_room_lamp et `sensor.motion
