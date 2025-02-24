# WorkHours-Analytics
Outil d’analyse des heures travaillées chez Domino’s Pizza, permettant aux équipiers de suivre leurs horaires et salaires via des dashboards interactifs sur Power BI. Extraction des données automatisée avec Playwright et calculs optimisés via DAX.

Comment ça marche ?

1- Exécutez le script Python et renseignez vos identifiants ainsi que la date à partir de laquelle vous souhaitez récupérer vos horaires de travail.

2- Le script utilise Playwright pour se connecter automatiquement à la plateforme de gestion des horaires, extraire les données et les enregistrer dans un fichier CSV.

3- Ouvrez le fichier Power BI et sélectionnez le fichier CSV généré par Python comme source de données.

4- Actualisez Power BI pour charger les nouvelles données et visualiser vos horaires, salaires et statistiques sous forme de dashboards interactifs.
