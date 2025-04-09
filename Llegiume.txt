# Django Image Scraper

## Característiques principals

Django Image Scraper és una aplicació web desenvolupada amb Django que permet als usuaris cercar, visualitzar i guardar imatges d'Internet de manera intuïtiva.

### Funcionalitats bàsiques

- **Cerca d'imatges**: Cerca imatges a Google Images amb diferents filtres.
- **Filtres avançats**: 
  - Filtre per drets d'autor (lliure, comercial, no comercial)
  - Opció per mostrar només imatges transparents
  - Cerca avançada amb opcions addicionals
- **Visualització d'imatges**:
  - Graella responsiva d'imatges
  - Vista detallada d'imatge individual
  - Previsualització modal d'imatges
  - Càrrega diferida (lazy loading) per millorar el rendiment

### Funcionalitats socials

- **Sistema d'usuaris**:
  - Registre d'usuaris
  - Inici de sessió
  - Perfils d'usuari
- **Interacció**:
  - "M'agrada" a imatges
  - Comentaris en imatges
  - Historial de cerques per usuari

### Característiques tècniques

- **Arquitectura**:
  - Aplicació monolítica desenvolupada amb Django 4.2
  - Base de dades SQLite
  - Frontend amb HTML, CSS (Tailwind) i JavaScript
  
- **Tecnologies emprades**:
  - **Backend**: Python, Django
  - **Frontend**: HTML5, Tailwind CSS, JavaScript
  - **Base de dades**: SQLite
  - **Extracció de dades**: BeautifulSoup, Requests
  - **Processament d'imatges**: Pillow

- **Implementacions avançades**:
  - Web scraping robust per extreure imatges de Google
  - Sistema de paginació
  - Gestió d'errors
  - Sistema de notificacions
  - Previsualització d'imatges amb modal
  - Imatges de tendència basades en "m'agrada"

## Instal·lació i configuració

### Requisits previs

- Python 3.8 o superior
- pip (gestor de paquets de Python)
- Navegador web modern

### Passos d'instal·lació

1. **Clonar el repositori**:
   ```bash
   git clone <url-del-repositori>
   cd django-image-scraper
   ```

2. **Crear i activar un entorn virtual**:
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Unix/MacOS:
   source venv/bin/activate
   ```

3. **Instal·lar dependències**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Aplicar les migracions de la base de dades**:
   ```bash
   python manage.py migrate
   ```

5. **Crear un superusuari (opcional)**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Iniciar el servidor de desenvolupament**:
   ```bash
   python manage.py runserver
   ```

7. **Accedir a l'aplicació**:
   Obre el navegador i accedeix a `http://127.0.0.1:8000/`

## Ús de l'aplicació

### Cercar imatges

1. Introdueix el terme de cerca al camp de cerca a la pàgina principal
2. Opcionalment, selecciona filtres per drets d'autor o transparència
3. Fes clic a "Search Images" per obtenir resultats

### Interactuar amb imatges

1. Fes clic en una imatge per veure'n els detalls
2. Des de la vista detallada, pots:
   - Donar "m'agrada" a la imatge (requereix inici de sessió)
   - Afegir comentaris (requereix inici de sessió)
   - Veure imatges similars
   - Descarregar la imatge

### Gestió d'usuaris

1. Registra't mitjançant l'enllaç "Sign up"
2. Inicia sessió amb les teves credencials
3. Accedeix al teu perfil per veure el teu historial de cerques, imatges amb "m'agrada" i comentaris

## Personalització i desenvolupament

L'aplicació està dissenyada per ser extensible. Algunes àrees que es poden personalitzar:

- **Estils**: Modificant els arxius Tailwind CSS
- **Fonts de dades**: Canviant l'estratègia de scraping o utilitzant APIs d'imatges
- **Funcionalitats**: Afegint noves característiques a través de vistes de Django addicionals

## Llicència

Aquest projecte és només per a finalitats educatives.
