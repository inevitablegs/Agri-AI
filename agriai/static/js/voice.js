document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('start-listening');
    const outputDiv = document.getElementById('voice-output');
    
    if (startBtn) {
        startBtn.addEventListener('click', function() {
            // This would integrate with your Hindi voice assistant
            outputDiv.textContent = "Listening...";
            
            // Example using Web Speech API (you might use your existing Hindi STT/TTS)
            if ('webkitSpeechRecognition' in window) {
                const recognition = new webkitSpeechRecognition();
                recognition.lang = 'hi-IN'; // Hindi
                recognition.interimResults = false;
                
                recognition.onresult = function(event) {
                    const transcript = event.results[0][0].transcript;
                    outputDiv.textContent = transcript;
                    
                    // Send to your Django backend for processing
                    fetch('/voice/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': getCookie('csrftoken'),
                        },
                        body: `voice_input=${encodeURIComponent(transcript)}`
                    })
                    .then(response => response.json())
                    .then(data => {
                        outputDiv.textContent = data.output;
                        // You could use speechSynthesis for TTS
                        if ('speechSynthesis' in window) {
                            const utterance = new SpeechSynthesisUtterance(data.output);
                            utterance.lang = 'hi-IN'; // Hindi
                            window.speechSynthesis.speak(utterance);
                        }
                    });
                };
                
                recognition.start();
            } else {
                outputDiv.textContent = "Voice recognition not supported in this browser";
            }
        });
    }
});

function getCookie(name) {
    // Helper function to get CSRF token
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}