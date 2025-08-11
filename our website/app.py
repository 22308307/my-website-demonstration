from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
import threading
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Pour les messages flash

# Configuration des données
DATA_FOLDER = 'data'
LINKS_FILE = os.path.join(DATA_FOLDER, 'links.json')
TEAM_FILE = os.path.join(DATA_FOLDER, 'team.json')

# Configuration de l'email
EMAIL_CONFIG = {
    "sender_email": "jnfirst0@gmail.com",  # Remplacez par votre email Gmail
    "password": "vrauijegwoogkrul",     # Remplacez par votre mot de passe ou token d'application
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 465
}

# Créer le dossier data s'il n'existe pas
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Initialiser les fichiers de données s'ils n'existent pas
if not os.path.exists(LINKS_FILE):
    with open(LINKS_FILE, 'w') as f:
        json.dump([], f)

if not os.path.exists(TEAM_FILE):
    # Données pour l'équipe
    team_data = [
        {
            "name": "Richard Olenu",
            "role": "Developer",
            "photo": "richard.jpg",
            "hobbies": "Randonnée, Programmation",
            "email": "Richardhomie89@gmail.com"
        },
        {
            "name": "Samuel Fomba",
            "role": "Designer",
            "photo": "samuel.jpg",
            "hobbies": "Photography, Art",
            "email": "sfomba001@gmail.com"
        },
        {
            "name": "Telvin Z  Howard",
            "role": "Marketing",
            "photo": "telvin.jpg",
            "hobbies": "Music, Travel",
            "email": "howardtelvin112@gmail.com"
        },
        {
            "name": "Jonathan mbuyi",
            "role": "project manager",
            "photo": "jonathan.jpg",
            "hobbies": "Lecture, cooking",
            "email": "jnfirst0@gmail.com"
        }
    ]
    with open(TEAM_FILE, 'w') as f:
        json.dump(team_data, f)

def get_team_data():
    with open(TEAM_FILE, 'r') as f:
        return json.load(f)

def get_links_data():
    with open(LINKS_FILE, 'r') as f:
        return json.load(f)

def save_link(link_url, description):
    links = get_links_data()
    links.append({
        "url": link_url,
        "description": description,
        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    with open(LINKS_FILE, 'w') as f:
        json.dump(links, f)
        
def scrape_page_title(url):
    """Scrape the title of a webpage from its URL"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.title.string if soup.title else "No title found"
    except Exception as e:
        print(f"Error scraping title: {e}")
        return "Could not retrieve title"

def send_weekly_email():
    """Send an email with all the links to the team every Monday"""
    links = get_links_data()
    team = get_team_data()
    
    if not links:
        print("No links to send")
        return
    
    email_content = "Here are the links recorded this week:\n\n"
    for link in links:
        email_content += f"- {link['description']}: {link['url']} (ajouté le {link['date_added']})\n"
    
    # Configuration de l'email
    sender_email = EMAIL_CONFIG["sender_email"]
    password = EMAIL_CONFIG["password"]
    
    for member in team:
        receiver_email = member['email']
        
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = f"Weekly Link Recap"
        
        message.attach(MIMEText(email_content, "plain"))
        
        try:
            with smtplib.SMTP_SSL(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            print(f"Email successfully sent to {receiver_email}")
        except Exception as e:
            print(f"Error sending email to {receiver_email}: {e}")

# Fonction pour envoyer un email immédiatement (pour tester)
def send_test_email():
    """Envoyer un email test à tous les membres de l'équipe immédiatement"""
    print("Sending test email to all team members...")
    send_weekly_email()
    return "Test emails sent. Check console for details."

# Planification de l'envoi d'email (tous les lundis à 8h)
def start_scheduler():
    schedule.every().monday.at("08:00").do(send_weekly_email)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# Démarrer le planificateur dans un thread séparé
scheduler_thread = threading.Thread(target=start_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()

# Routes de l'application
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    team = get_team_data()
    return render_template('about.html', team=team)

@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if request.method == 'POST':
        link_url = request.form.get('link_url')
        description = request.form.get('description')
        
        if link_url:
            # Si la description est vide, essayez de récupérer le titre de la page
            if not description or description.strip() == "":
                try:
                    print(f"Tentative de scraping pour: {link_url}")
                    description = scrape_page_title(link_url)
                    print(f"Titre récupéré: {description}")
                    
                    # Utiliser une description par défaut si le scraping échoue
                    if not description or description == "Could not retrieve title" or description == "No title found":
                        description = "No description"
                        print("Échec du scraping, utilisation de la description par défaut")
                except Exception as e:
                    description = "No description"
                    print(f"Erreur pendant le scraping: {e}")

            save_link(link_url, description)
            flash('Link added successfully!', 'success')
        else:
            flash('Please enter a valid URL', 'danger')
        
        return redirect(url_for('tasks'))
    
    links = get_links_data()
    return render_template('tasks.html', links=links)
    
@app.route('/scrape-url', methods=['POST'])
def scrape_url():
    url = request.form.get('url')
    if url:
        title = scrape_page_title(url)
        return {"title": title}
    return {"title": ""}

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Route pour tester l'envoi d'email
@app.route('/test-email')
def test_email():
    result = send_test_email()
    flash('Test emails have been sent!', 'info')
    return redirect(url_for('tasks'))

if __name__ == '__main__':
    app.run(debug=True)