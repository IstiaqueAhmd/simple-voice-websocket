class VoiceAssistant {
    constructor() {
        this.ws = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.isProcessing = false;
        this.stream = null;
        
        this.micButton = document.getElementById('micButton');
        this.status = document.getElementById('status');
        this.chatMessages = document.getElementById('chatMessages');
        this.clearButton = document.getElementById('clearChat');
        this.connectionStatus = document.getElementById('connectionStatus');
        
        this.initializeWebSocket();
        this.setupEventListeners();
        this.initializeAudio();
    }
    
    async initializeAudio() {
        try {
            // Request microphone access
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                } 
            });
            this.updateStatus('Microphone access granted. Ready to record!');
        } catch (error) {
            console.error('Error accessing microphone:', error);
            this.updateStatus('Microphone access denied. Please enable microphone access.');
            this.micButton.disabled = true;
        }
    }
    
    initializeWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.connectionStatus.textContent = 'Connecting...';
        this.connectionStatus.className = 'status-indicator connecting';
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.connectionStatus.textContent = 'Connected';
            this.connectionStatus.className = 'status-indicator connected';
            this.updateStatus('Connected! Ready to record.');
        };
        
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.connectionStatus.textContent = 'Disconnected';
            this.connectionStatus.className = 'status-indicator disconnected';
            this.updateStatus('Disconnected. Attempting to reconnect...');
            
            // Attempt to reconnect after 3 seconds
            setTimeout(() => {
                this.initializeWebSocket();
            }, 3000);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateStatus('Connection error occurred.');
        };
    }
    
    setupEventListeners() {
        this.micButton.addEventListener('click', () => {
            if (this.isRecording) {
                this.stopRecording();
            } else {
                this.startRecording();
            }
        });
        
        this.clearButton.addEventListener('click', () => {
            this.clearChat();
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            if (event.code === 'Space' && event.ctrlKey) {
                event.preventDefault();
                if (this.isRecording) {
                    this.stopRecording();
                } else {
                    this.startRecording();
                }
            }
        });
    }
    
    startRecording() {
        if (!this.stream || this.isRecording || this.isProcessing) return;
        
        try {
            this.audioChunks = [];
            this.mediaRecorder = new MediaRecorder(this.stream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                this.processRecording();
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            this.micButton.classList.add('listening');
            this.updateStatus('Recording... Click again to stop.');
            
        } catch (error) {
            console.error('Error starting recording:', error);
            this.updateStatus('Error starting recording.');
        }
    }
    
    stopRecording() {
        if (!this.isRecording || !this.mediaRecorder) return;
        
        this.isRecording = false;
        this.micButton.classList.remove('listening');
        this.updateStatus('Processing...');
        
        this.mediaRecorder.stop();
    }
    
    async processRecording() {
        if (this.audioChunks.length === 0) return;
        
        try {
            // Create blob from audio chunks
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm;codecs=opus' });
            
            // Convert to base64
            const reader = new FileReader();
            reader.onload = () => {
                const base64Audio = reader.result.split(',')[1]; // Remove data:audio/webm;base64, prefix
                this.sendAudioData(base64Audio);
            };
            reader.readAsDataURL(audioBlob);
            
        } catch (error) {
            console.error('Error processing recording:', error);
            this.updateStatus('Error processing recording.');
            this.isProcessing = false;
        }
    }
    
    sendAudioData(base64Audio) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.isProcessing = true;
            this.micButton.classList.add('processing');
            
            const data = {
                type: 'audio_data',
                audio: base64Audio,
                timestamp: Date.now()
            };
            
            this.ws.send(JSON.stringify(data));
        } else {
            this.updateStatus('WebSocket not connected. Cannot send audio.');
            this.isProcessing = false;
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'ai_response':
                // Add transcription if available
                if (data.transcription) {
                    this.addMessage(data.transcription, 'user');
                }
                
                this.addMessage(data.message, 'assistant');
                
                // Play audio response if available
                if (data.audio) {
                    this.playAudioResponse(data.audio);
                }
                
                this.isProcessing = false;
                this.micButton.classList.remove('processing');
                this.updateStatus('Ready to record');
                break;
                
            case 'error':
                console.error('Server error:', data.message);
                this.updateStatus(`Error: ${data.message}`);
                this.isProcessing = false;
                this.micButton.classList.remove('processing');
                break;
                
            case 'pong':
                console.log('Received pong from server');
                break;
                
            default:
                console.log('Unknown message type:', data.type);
        }
    }
    
    playAudioResponse(base64Audio) {
        try {
            // Convert base64 to blob
            const audioData = atob(base64Audio);
            const arrayBuffer = new ArrayBuffer(audioData.length);
            const uint8Array = new Uint8Array(arrayBuffer);
            
            for (let i = 0; i < audioData.length; i++) {
                uint8Array[i] = audioData.charCodeAt(i);
            }
            
            const audioBlob = new Blob([arrayBuffer], { type: 'audio/mpeg' });
            const audioUrl = URL.createObjectURL(audioBlob);
            
            const audio = new Audio(audioUrl);
            audio.onended = () => {
                URL.revokeObjectURL(audioUrl);
                console.log('Audio playback completed');
            };
            
            audio.onerror = (error) => {
                console.error('Error playing audio:', error);
                URL.revokeObjectURL(audioUrl);
            };
            
            audio.play().catch(error => {
                console.error('Error starting audio playback:', error);
            });
            
        } catch (error) {
            console.error('Error processing audio response:', error);
        }
    }
    
    addMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const senderLabel = sender === 'user' ? 'You' : 'Assistant';
        contentDiv.innerHTML = `<strong>${senderLabel}:</strong> ${message}`;
        
        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    updateStatus(message) {
        this.status.textContent = message;
    }
    
    clearChat() {
        this.chatMessages.innerHTML = `
            <div class="message assistant">
                <div class="message-content">
                    <strong>Assistant:</strong> Chat cleared! How can I help you?
                </div>
            </div>
        `;
    }
    
    // Send periodic ping to keep connection alive
    startHeartbeat() {
        setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ type: 'ping' }));
            }
        }, 30000); // Send ping every 30 seconds
    }
}

// Initialize the voice assistant when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const assistant = new VoiceAssistant();
    assistant.startHeartbeat();
});
