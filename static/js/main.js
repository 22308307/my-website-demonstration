/**
 * Script principal pour le site web
 */

// Attendre que le DOM soit complètement chargé
document.addEventListener('DOMContentLoaded', function() {
    // Animation pour les messages flash
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Ajouter une animation de fade-in
        alert.style.opacity = '0';
        let opacity = 0;
        const fadeIn = setInterval(() => {
            if (opacity >= 1) {
                clearInterval(fadeIn);
            }
            alert.style.opacity = opacity.toString();
            opacity += 0.1;
        }, 30);
        
        // Faire disparaître l'alerte après 5 secondes
        setTimeout(() => {
            let opacity = 1;
            const fadeOut = setInterval(() => {
                if (opacity <= 0) {
                    clearInterval(fadeOut);
                    alert.style.display = 'none';
                }
                alert.style.opacity = opacity.toString();
                opacity -= 0.1;
            }, 30);
        }, 5000);
    });

    // Validation du formulaire d'ajout de lien
const linkForm = document.querySelector('form');
const urlInput = document.getElementById('link_url');
const descInput = document.getElementById('description');

// Ajouter un écouteur d'événement pour récupérer le titre automatiquement
if (urlInput && descInput) {
    urlInput.addEventListener('blur', function() {
        const url = urlInput.value.trim();
        if (url && isValidURL(url) && !descInput.value.trim()) {
            // Montrer un indicateur de chargement
            descInput.placeholder = "Loading title...";
            
            // Créer une requête AJAX pour récupérer le titre
            fetch('/scrape-url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'url=' + encodeURIComponent(url)
            })
            .then(response => response.json())
            .then(data => {
                if (data.title && data.title !== "No title found" && data.title !== "Could not retrieve title") {
                    descInput.value = data.title;
                }
                descInput.placeholder = "Describe this Link (optional)";
            })
            .catch(error => {
                console.error('Error fetching title:', error);
                descInput.placeholder = "Describe this Link (optional)";
            });
        }
    });
}

if (linkForm) {
    linkForm.addEventListener('submit', function(event) {
        // Validation simple de l'URL
        if (!isValidURL(urlInput.value)) {
            event.preventDefault();
            showError(urlInput, 'Please enter a valid URL valid (starting with http:// or https://)');
        } else {
            removeError(urlInput);
        }
        
        // Nous ne vérifions plus si la description est vide
        removeError(descInput);
    });
}

// Fonction pour vérifier si une URL est valide
function isValidURL(url) {
    return url.startsWith('http://') || url.startsWith('https://');
}
    
    
    // Fonction pour valider les URLs
    function isValidURL(url) {
        try {
            const newUrl = new URL(url);
            return newUrl.protocol === 'http:' || newUrl.protocol === 'https:';
        } catch (err) {
            return false;
        }
    }
    
    // Fonctions pour afficher/supprimer les messages d'erreur
    function showError(input, message) {
        removeError(input);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'input-error';
        errorDiv.textContent = message;
        errorDiv.style.color = 'var(--danger-color)';
        errorDiv.style.fontSize = '0.8rem';
        errorDiv.style.marginTop = '0.5rem';
        input.parentNode.appendChild(errorDiv);
        input.style.borderColor = 'var(--danger-color)';
    }
    
    function removeError(input) {
        const existingError = input.parentNode.querySelector('.input-error');
        if (existingError) {
            existingError.remove();
        }
        input.style.borderColor = '';
    }
    
    // Effet hover sur les liens du tableau
    const tableRows = document.querySelectorAll('table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transition = 'background-color 0.3s';
        });
    });
    
    // Animation pour la section héros
    const heroSection = document.querySelector('.hero');
    if (heroSection) {
        window.addEventListener('scroll', function() {
            const scrollPos = window.scrollY;
            // Effet de parallaxe simple
            heroSection.style.backgroundPositionY = -scrollPos * 0.2 + 'px';
        });
    }
    
    // Animation pour faire apparaître les membres de l'équipe
    const teamMembers = document.querySelectorAll('.member');
    if (teamMembers.length > 0) {
        window.addEventListener('scroll', function() {
            const windowHeight = window.innerHeight;
            
            teamMembers.forEach(member => {
                const rect = member.getBoundingClientRect();
                
                // Si l'élément est visible dans la fenêtre
                if (rect.top < windowHeight * 0.9) {
                    member.style.transition = 'opacity 1s, transform 1s';
                    member.style.opacity = '1';
                    member.style.transform = 'translateY(0)';
                } else {
                    member.style.opacity = '0';
                    member.style.transform = 'translateY(20px)';
                }
            });
        });
        
        // Déclencher l'événement de scroll pour initialiser l'état
        window.dispatchEvent(new Event('scroll'));
    }
});