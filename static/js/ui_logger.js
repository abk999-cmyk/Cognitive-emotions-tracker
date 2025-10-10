/**
 * UI Logger Module
 * Batches client-side errors and events, sends to server without PII
 */

class UILogger {
    constructor() {
        this.buffer = [];
        this.maxBufferSize = 50;
        this.flushInterval = 10000; // Flush every 10 seconds
        this.endpoint = '/api/ui_log';
        this.flushTimer = null;
        
        // Start flush timer
        this.startFlushTimer();
        
        // Flush on page unload
        window.addEventListener('beforeunload', () => this.flush());
    }
    
    /**
     * Log an event (non-PII)
     */
    log(eventType, message, data = {}) {
        const entry = {
            type: eventType,
            message: this.sanitize(message),
            path: window.location.pathname,
            timestamp: new Date().toISOString(),
            data: this.sanitizeObject(data)
        };
        
        this.buffer.push(entry);
        
        // Flush if buffer is full
        if (this.buffer.length >= this.maxBufferSize) {
            this.flush();
        }
    }
    
    /**
     * Log an error
     */
    error(message, error = null) {
        const data = {};
        
        if (error) {
            data.error = {
                name: error.name,
                message: this.sanitize(error.message),
                stack: error.stack ? error.stack.split('\n').slice(0, 3).join('\n') : null
            };
        }
        
        this.log('error', message, data);
        console.error('[UILogger]', message, error);
    }
    
    /**
     * Log a warning
     */
    warn(message, data = {}) {
        this.log('warning', message, data);
        console.warn('[UILogger]', message, data);
    }
    
    /**
     * Log info
     */
    info(message, data = {}) {
        this.log('info', message, data);
    }
    
    /**
     * Sanitize string to remove PII
     */
    sanitize(str) {
        if (typeof str !== 'string') return str;
        
        // Remove potential PII patterns (emails, phone numbers, etc.)
        return str
            .replace(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g, '[EMAIL]')
            .replace(/\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g, '[PHONE]')
            .replace(/\b\d{3}-\d{2}-\d{4}\b/g, '[SSN]');
    }
    
    /**
     * Sanitize object recursively
     */
    sanitizeObject(obj) {
        if (!obj || typeof obj !== 'object') return obj;
        
        const sanitized = {};
        for (const [key, value] of Object.entries(obj)) {
            if (typeof value === 'string') {
                sanitized[key] = this.sanitize(value);
            } else if (typeof value === 'object') {
                sanitized[key] = this.sanitizeObject(value);
            } else {
                sanitized[key] = value;
            }
        }
        return sanitized;
    }
    
    /**
     * Flush buffer to server
     */
    async flush() {
        if (this.buffer.length === 0) return;
        
        const logs = [...this.buffer];
        this.buffer = [];
        
        try {
            const response = await fetch(this.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ logs })
            });
            
            if (!response.ok) {
                console.error('[UILogger] Failed to send logs:', response.status);
            }
        } catch (error) {
            console.error('[UILogger] Error sending logs:', error);
            // Re-add to buffer if failed (but limit total size)
            this.buffer = [...logs.slice(-10), ...this.buffer];
        }
    }
    
    /**
     * Start automatic flush timer
     */
    startFlushTimer() {
        this.flushTimer = setInterval(() => {
            this.flush();
        }, this.flushInterval);
    }
    
    /**
     * Stop flush timer
     */
    stopFlushTimer() {
        if (this.flushTimer) {
            clearInterval(this.flushTimer);
            this.flushTimer = null;
        }
    }
}

// Create global logger instance
window.uiLogger = new UILogger();

// Capture global errors
window.addEventListener('error', (event) => {
    window.uiLogger.error('Uncaught error', event.error);
});

// Capture unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    window.uiLogger.error('Unhandled promise rejection', new Error(event.reason));
});

