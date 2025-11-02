// Wake device function
async function wakeDevice(deviceId, buttonElement) {
    // Disable button and show loading
    const originalText = buttonElement.textContent;
    buttonElement.disabled = true;
    buttonElement.textContent = '⏳ Envoi...';
    
    try {
        const response = await fetch(`/wake/${deviceId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            buttonElement.textContent = '✓ Envoyé';
            setTimeout(() => {
                buttonElement.textContent = originalText;
                buttonElement.disabled = false;
            }, 3000);
        } else {
            showNotification(data.message, 'error');
            buttonElement.textContent = originalText;
            buttonElement.disabled = false;
        }
    } catch (error) {
        showNotification('Erreur de connexion au serveur', 'error');
        buttonElement.textContent = originalText;
        buttonElement.disabled = false;
    }
}

// Delete device with confirmation
function confirmDelete(deviceId, deviceName) {
    if (confirm(`Êtes-vous sûr de vouloir supprimer l'appareil "${deviceName}" ?`)) {
        const form = document.getElementById(`delete-form-${deviceId}`);
        if (form) {
            form.submit();
        }
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.style.maxWidth = '500px';
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// Format MAC address on input
function formatMACAddress(input) {
    let value = input.value.replace(/[^0-9A-Fa-f]/g, '');
    if (value.length > 12) {
        value = value.substring(0, 12);
    }
    
    // Add colons every 2 characters
    let formatted = '';
    for (let i = 0; i < value.length; i += 2) {
        if (i > 0) {
            formatted += ':';
        }
        formatted += value.substring(i, i + 2);
    }
    
    input.value = formatted.toUpperCase();
}

// Validate form before submission
function validateDeviceForm(form) {
    const name = form.querySelector('[name="name"]').value.trim();
    const mac = form.querySelector('[name="mac_address"]').value.trim();
    const port = form.querySelector('[name="port"]').value;
    
    if (!name) {
        showNotification('Le nom de l\'appareil est requis', 'error');
        return false;
    }
    
    if (!mac) {
        showNotification('L\'adresse MAC est requise', 'error');
        return false;
    }
    
    // Validate MAC format
    const macPattern = /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/;
    if (!macPattern.test(mac)) {
        showNotification('Format d\'adresse MAC invalide. Utilisez XX:XX:XX:XX:XX:XX', 'error');
        return false;
    }
    
    // Validate port
    const portNum = parseInt(port);
    if (isNaN(portNum) || portNum < 1 || portNum > 65535) {
        showNotification('Le port doit être entre 1 et 65535', 'error');
        return false;
    }
    
    return true;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.3s';
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 300);
        }, 5000);
    });
    
    // Add MAC address formatting to input fields
    const macInputs = document.querySelectorAll('input[name="mac_address"]');
    macInputs.forEach(input => {
        input.addEventListener('input', function() {
            formatMACAddress(this);
        });
    });
});
