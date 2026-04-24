# MyGES to Home Assistant

Intégration Home Assistant qui synchronise automatiquement votre emploi du temps MyGES (réseau Kordis/Skolae) vers votre Home Assistant et vos entités de calendrier Google.

Cette intégration crée un calendrier interne (ex: `calendar.myges_t_krywak`) avec vos cours des prochaines semaines, et peut également synchroniser ces événements directement dans le calendrier Google officiel de votre choix.

## 🚀 Installation via HACS (Recommandé)

1. Assurez-vous d'avoir installé [HACS](https://hacs.xyz/).
2. Allez dans HACS > Intégrations.
3. Cliquez sur les 3 points en haut à droite, puis "Dépôts personnalisés".
4. Ajoutez l'URL de ce dépôt (`https://github.com/myges2ha/myges2ha`) avec la catégorie "Intégration".
5. Cliquez sur "Télécharger" et redémarrez Home Assistant.

## ⚙️ Configuration

1. Dans Home Assistant, allez dans **Paramètres > Appareils et services**.
2. Cliquez sur **Ajouter une intégration** en bas à droite.
3. Cherchez **MyGES to Home Assistant**.
4. Saisissez vos identifiants (Nom d'utilisateur et mot de passe MyGES).
5. (Optionnel) Sélectionnez le calendrier cible si vous souhaitez envoyer les événements vers un autre calendrier (ex: votre calendrier Google Agenda).

## 📅 Fonctionnement

- Vos cours seront téléchargés toutes les heures.
- Home Assistant créera une entité de calendrier que vous pourrez utiliser dans vos automatisations.
- Si vous avez sélectionné un calendrier cible, l'intégration y créera tous vos cours.
