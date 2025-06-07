# Grok : Générateur de suggestions, scripts, scènes et automatisation

![Logo](./images/logo.png)

[![GitHub release](https://img.shields.io/github/v/release/XAV59213/freesmsxa)](https://github.com/XAV59213/freesmsxa/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg?logo=home-assistant)](https://hacs.xyz/)
[![License: LGPL v2.1](https://img.shields.io/badge/License-LGPL%20v2.1-blue.svg)](./LICENSE)

<a href="https://www.buymeacoffee.com/xav59213"> <img src="https://img.buymeacoffee.com/button-api/?text=xav59213&emoji=&slug=xav59213&button_colour=5F7FFF&font_colour=ffffff&font_family=Cookie&outline_colour=000000&coffee_colour=FFDD00" /> 

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
Yo, j’ai scanné ton salon et trouvé light.living_room_lamp et sensor.motion_living_room. Voici une idée d’automatisation pour rendre ton salon plus cool :
- id: living_room_motion_light
  alias: Allumer la lampe du salon sur détection de mouvement
  description: Active la lampe quand quelqu’un entre dans le salon, mais seulement le soir.
  trigger:
    - platform: state
      entity_id: sensor.motion_living_room
      to: "on"
  condition:
    - condition: sun
      after: sunset
  action:
    - service: light.turn_on
      target:
        entity_id: light.living_room_lamp
      data:
        brightness_pct: 80

Qu’en penses-tu ? Prêt à transformer ton salon en vaisseau spatial ? 🚀
Contribution

Forkez le dépôt sur https://github.com/XAV59213/grok_automation_suggester.
Faites vos modifications et soumettez une Pull Request.
Signalez les bugs ou suggestions via Issues.
Pour tester localement, placez les fichiers dans custom_components/grok_automation_suggester/ et redémarrez Home Assistant.

Crédits

Basé sur l’intégration originale ai_automation_suggester.
Propulsé par xAI.


Allez, à vos automations, et que la force intergalactique soit avec vous ! 😎
