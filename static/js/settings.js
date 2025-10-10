/**
 * Settings Module
 * Manages user preferences and settings modal
 */

class SettingsManager {
    constructor() {
        this.settings = this.loadSettings();
        this.modal = null;
        this.socket = null; // Will be set by dashboard
        
        this.initModal();
        this.applySettings();
    }
    
    /**
     * Default settings
     */
    getDefaults() {
        return {
            updateFrequency: 500, // ms (client-side display update)
            reducedMotion: DOMUtils.prefersReducedMotion(),
            highContrast: false,
            videoEnabled: true,
            audioEnabled: true,
            smoothingAlpha: 0.6, // Server-side (informational only)
            theme: 'dark'
        };
    }
    
    /**
     * Load settings from localStorage
     */
    loadSettings() {
        try {
            const stored = localStorage.getItem('emotionTrackerSettings');
            if (stored) {
                return { ...this.getDefaults(), ...JSON.parse(stored) };
            }
        } catch (error) {
            console.warn('Failed to load settings:', error);
        }
        return this.getDefaults();
    }
    
    /**
     * Save settings to localStorage
     */
    saveSettings() {
        try {
            localStorage.setItem('emotionTrackerSettings', JSON.stringify(this.settings));
            uiLogger.info('Settings saved', { settings: this.settings });
        } catch (error) {
            uiLogger.error('Failed to save settings', error);
        }
    }
    
    /**
     * Get setting value
     */
    get(key) {
        return this.settings[key];
    }
    
    /**
     * Set setting value
     */
    set(key, value) {
        this.settings[key] = value;
        this.saveSettings();
        this.applySettings();
    }
    
    /**
     * Initialize settings modal
     */
    initModal() {
        this.modal = document.getElementById('settingsModal');
        
        if (!this.modal) {
            uiLogger.error('Settings modal not found in DOM');
            return;
        }
        
        // Close button
        const closeBtn = this.modal.querySelector('.close-settings');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }
        
        // Close on outside click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });
        
        // Initialize form controls
        this.initFormControls();
        
        // Save button
        const saveBtn = document.getElementById('saveSettings');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.handleSave());
        }
    }
    
    /**
     * Initialize form controls with current values
     */
    initFormControls() {
        // Update frequency
        const updateFreqInput = document.getElementById('updateFrequency');
        const updateFreqValue = document.getElementById('updateFrequencyValue');
        if (updateFreqInput) {
            updateFreqInput.value = this.settings.updateFrequency;
            if (updateFreqValue) {
                updateFreqValue.textContent = `${this.settings.updateFrequency}ms`;
            }
            updateFreqInput.addEventListener('input', (e) => {
                if (updateFreqValue) {
                    updateFreqValue.textContent = `${e.target.value}ms`;
                }
            });
        }
        
        // Reduced motion
        const reducedMotionInput = document.getElementById('reducedMotion');
        if (reducedMotionInput) {
            reducedMotionInput.checked = this.settings.reducedMotion;
        }
        
        // High contrast
        const highContrastInput = document.getElementById('highContrast');
        if (highContrastInput) {
            highContrastInput.checked = this.settings.highContrast;
        }
        
        // Video enabled
        const videoEnabledInput = document.getElementById('videoEnabled');
        if (videoEnabledInput) {
            videoEnabledInput.checked = this.settings.videoEnabled;
        }
        
        // Audio enabled
        const audioEnabledInput = document.getElementById('audioEnabled');
        if (audioEnabledInput) {
            audioEnabledInput.checked = this.settings.audioEnabled;
        }
    }
    
    /**
     * Handle save button click
     */
    handleSave() {
        // Read values from form
        const updateFreqInput = document.getElementById('updateFrequency');
        if (updateFreqInput) {
            this.set('updateFrequency', parseInt(updateFreqInput.value));
        }
        
        const reducedMotionInput = document.getElementById('reducedMotion');
        if (reducedMotionInput) {
            this.set('reducedMotion', reducedMotionInput.checked);
        }
        
        const highContrastInput = document.getElementById('highContrast');
        if (highContrastInput) {
            this.set('highContrast', highContrastInput.checked);
        }
        
        const videoEnabledInput = document.getElementById('videoEnabled');
        if (videoEnabledInput) {
            const newValue = videoEnabledInput.checked;
            if (newValue !== this.settings.videoEnabled) {
                this.set('videoEnabled', newValue);
                this.toggleVideoAudio('video', newValue);
            }
        }
        
        const audioEnabledInput = document.getElementById('audioEnabled');
        if (audioEnabledInput) {
            const newValue = audioEnabledInput.checked;
            if (newValue !== this.settings.audioEnabled) {
                this.set('audioEnabled', newValue);
                this.toggleVideoAudio('audio', newValue);
            }
        }
        
        DOMUtils.announce('Settings saved successfully');
        this.close();
    }
    
    /**
     * Toggle video/audio processing via Socket.IO
     */
    toggleVideoAudio(type, enabled) {
        if (!this.socket || !this.socket.connected) {
            uiLogger.warn('Cannot toggle processing - socket not connected');
            return;
        }
        
        this.socket.emit('toggle_processing', {
            type: type,
            enabled: enabled
        });
        
        uiLogger.info(`${type} processing ${enabled ? 'enabled' : 'disabled'}`);
    }
    
    /**
     * Apply settings to UI
     */
    applySettings() {
        // High contrast theme
        if (this.settings.highContrast) {
            document.body.classList.add('high-contrast');
        } else {
            document.body.classList.remove('high-contrast');
        }
        
        // Reduced motion
        if (this.settings.reducedMotion) {
            document.body.classList.add('reduced-motion');
        } else {
            document.body.classList.remove('reduced-motion');
        }
    }
    
    /**
     * Open settings modal
     */
    open() {
        if (this.modal) {
            this.modal.style.display = 'flex';
            this.modal.setAttribute('aria-hidden', 'false');
            
            // Focus first input
            const firstInput = this.modal.querySelector('input, button');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
            
            uiLogger.info('Settings modal opened');
        }
    }
    
    /**
     * Close settings modal
     */
    close() {
        if (this.modal) {
            this.modal.style.display = 'none';
            this.modal.setAttribute('aria-hidden', 'true');
            uiLogger.info('Settings modal closed');
        }
    }
    
    /**
     * Set socket instance for server communication
     */
    setSocket(socket) {
        this.socket = socket;
    }
}

// Make available globally
window.SettingsManager = SettingsManager;

