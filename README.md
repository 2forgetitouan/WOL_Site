# ⚡ WOL Site - Wake On LAN Web Application

Un site web complet pour contrôler vos appareils à distance via Wake-On-LAN.

## 🌟 Fonctionnalités

- ✅ **Authentification utilisateur** : Inscription, connexion et gestion de session sécurisée
- ✅ **Gestion d'appareils** : Ajout, suppression et organisation de vos appareils WOL
- ✅ **Envoi de paquets magiques** : Réveillez vos ordinateurs d'un simple clic
- ✅ **Interface moderne** : Design responsive et agréable (mobile + desktop)
- ✅ **Documentation complète** : Guide détaillé sur la configuration WOL
- ✅ **Support et contact** : Page de contact pour obtenir de l'aide

## 🛠️ Technologies utilisées

- **Backend** : Python 3 + Flask
- **Frontend** : HTML5 + CSS3 + JavaScript (Vanilla)
- **Base de données** : SQLite
- **Sécurité** : Werkzeug (hachage de mots de passe), sessions Flask

## 📋 Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

## 🚀 Installation

1. **Cloner le dépôt** :
```bash
git clone https://github.com/2forgetitouan/WOL_Site.git
cd WOL_Site
```

2. **Créer un environnement virtuel** (recommandé) :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

4. **Lancer l'application** :
```bash
python app.py
```

5. **Accéder à l'application** :
Ouvrez votre navigateur et allez sur : `http://localhost:5000`

## 📖 Utilisation

### Première utilisation

1. **Créer un compte** : Cliquez sur "Inscription" et créez votre compte utilisateur
2. **Se connecter** : Connectez-vous avec vos identifiants
3. **Ajouter un appareil** : 
   - Cliquez sur "Ajouter un appareil"
   - Renseignez le nom, l'adresse MAC, l'IP (optionnel) et le port
   - Sauvegardez
4. **Réveiller un appareil** : Sur le tableau de bord, cliquez sur "Wake" pour envoyer le paquet magique

### Configuration Wake-On-LAN

Consultez la page **Aide** du site pour un guide complet sur :
- Comment activer WOL dans le BIOS
- Configuration du système d'exploitation (Windows, Linux, macOS)
- Comment trouver l'adresse MAC de votre appareil
- Configuration réseau (IP, port, NAT, port forwarding)
- Dépannage et résolution de problèmes

## 🔐 Sécurité

- Les mots de passe sont hachés avec Werkzeug (PBKDF2)
- Sessions sécurisées avec clé secrète aléatoire
- Validation des entrées utilisateur
- Protection contre les injections SQL (requêtes paramétrées)

## 📂 Structure du projet

```
WOL_Site/
├── app.py                  # Application Flask principale
├── requirements.txt        # Dépendances Python
├── .gitignore             # Fichiers à ignorer par Git
├── README.md              # Documentation
├── static/                # Fichiers statiques
│   ├── css/
│   │   └── style.css      # Styles CSS
│   └── js/
│       └── main.js        # JavaScript
└── templates/             # Templates HTML
    ├── base.html          # Template de base
    ├── index.html         # Page d'accueil
    ├── login.html         # Page de connexion
    ├── register.html      # Page d'inscription
    ├── dashboard.html     # Tableau de bord
    ├── add_device.html    # Ajouter un appareil
    ├── help.html          # Page d'aide
    └── contact.html       # Page de contact
```

## 🌐 Pages disponibles

- `/` - Page d'accueil avec présentation
- `/register` - Inscription
- `/login` - Connexion
- `/dashboard` - Tableau de bord (authentification requise)
- `/add-device` - Ajouter un appareil (authentification requise)
- `/help` - Guide complet Wake-On-LAN
- `/contact` - Page de contact

## 🤝 Contact

Pour toute question ou assistance : **titouan@deforge.me**

## 📝 Licence

Ce projet est un projet personnel open-source.

## 🎯 Améliorations futures possibles

- [ ] Modification d'appareils existants
- [ ] Historique des réveils
- [ ] Planification de réveils automatiques
- [ ] API REST pour intégration avec d'autres services
- [ ] Support multi-langues
- [ ] Notifications par email
- [ ] Interface d'administration