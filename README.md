# MyGES to Home Assistant

Intégration Home Assistant qui synchronise automatiquement votre emploi du temps MyGES (réseau Kordis/Skolae) vers votre Home Assistant et vos entités de calendrier Google.

Cette intégration crée un calendrier interne (ex: `calendar.myges_t_krywak`) avec vos cours des prochaines semaines, et peut également synchroniser ces événements directement dans le calendrier Google officiel de votre choix.

## 🚀 Installation via HACS (Recommandé)

1. Assurez-vous d'avoir installé [HACS](https://hacs.xyz/).
2. Allez dans HACS > Intégrations.
3. Cliquez sur les 3 points en haut à droite, puis "Dépôts personnalisés".
4. Ajoutez l'URL de ce dépôt (`https://github.com/myges2ha/myges2ha` ou votre propre URL) avec la catégorie "Intégration".
5. Cliquez sur "Télécharger" et redémarrez Home Assistant.

## ⚙️ Configuration et Calendrier Cible

1. **Prérequis pour Google Agenda :** Assurez-vous d'avoir configuré [l'intégration officielle Google Agenda de Home Assistant](https://www.home-assistant.io/integrations/google/). Repérez l'ID de l'entité de votre agenda (ex: `calendar.votre_adresse_email_gmail_com`).
2. Dans Home Assistant, allez dans **Paramètres > Appareils et services**.
3. Cliquez sur **Ajouter une intégration** en bas à droite.
4. Cherchez **MyGES to Home Assistant**.
5. Saisissez vos identifiants (Nom d'utilisateur et mot de passe MyGES).
6. **Calendrier cible :** Sélectionnez l'entité de votre calendrier Google (ex: `calendar.votre_adresse_email_gmail_com`) parmi la liste pour que l'intégration puisse envoyer automatiquement vos cours vers Google Agenda.

## 📅 Fonctionnement

- Vos cours seront téléchargés toutes les heures.
- Home Assistant créera une entité de calendrier que vous pourrez utiliser dans vos automatisations.
- Si vous avez sélectionné un calendrier cible, l'intégration y créera tous vos cours.
