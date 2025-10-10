/**
 * DOM Utilities Module
 * Helpers for ARIA, accessibility, and efficient DOM updates
 */

const DOMUtils = {
    /**
     * Set ARIA attributes on an element
     */
    setAria(element, attributes) {
        for (const [key, value] of Object.entries(attributes)) {
            const ariaKey = key.startsWith('aria-') ? key : `aria-${key}`;
            element.setAttribute(ariaKey, value);
        }
    },
    
    /**
     * Create element with attributes and content
     */
    createElement(tag, options = {}) {
        const element = document.createElement(tag);
        
        if (options.className) {
            element.className = options.className;
        }
        
        if (options.id) {
            element.id = options.id;
        }
        
        if (options.text) {
            element.textContent = options.text;
        }
        
        if (options.html) {
            element.innerHTML = options.html;
        }
        
        if (options.attributes) {
            for (const [key, value] of Object.entries(options.attributes)) {
                element.setAttribute(key, value);
            }
        }
        
        if (options.aria) {
            this.setAria(element, options.aria);
        }
        
        if (options.children) {
            options.children.forEach(child => element.appendChild(child));
        }
        
        return element;
    },
    
    /**
     * Efficiently update text content only if changed
     */
    updateText(element, newText) {
        if (element.textContent !== newText) {
            element.textContent = newText;
            return true;
        }
        return false;
    },
    
    /**
     * Efficiently update element class only if changed
     */
    updateClass(element, oldClass, newClass) {
        if (oldClass !== newClass) {
            if (oldClass) element.classList.remove(oldClass);
            if (newClass) element.classList.add(newClass);
            return true;
        }
        return false;
    },
    
    /**
     * Announce message to screen readers
     */
    announce(message, priority = 'polite') {
        let announcer = document.getElementById('aria-live-announcer');
        
        if (!announcer) {
            announcer = document.createElement('div');
            announcer.id = 'aria-live-announcer';
            announcer.setAttribute('aria-live', priority);
            announcer.setAttribute('aria-atomic', 'true');
            announcer.style.cssText = 'position:absolute;left:-10000px;width:1px;height:1px;overflow:hidden;';
            document.body.appendChild(announcer);
        }
        
        // Clear and set message to trigger announcement
        announcer.textContent = '';
        setTimeout(() => {
            announcer.textContent = message;
        }, 100);
    },
    
    /**
     * Add keyboard shortcut
     */
    addShortcut(key, callback, options = {}) {
        const handler = (event) => {
            // Check modifiers
            const ctrl = options.ctrl !== undefined ? options.ctrl : false;
            const shift = options.shift !== undefined ? options.shift : false;
            const alt = options.alt !== undefined ? options.alt : false;
            
            if (event.ctrlKey !== ctrl || event.shiftKey !== shift || event.altKey !== alt) {
                return;
            }
            
            // Check key
            if (event.key.toLowerCase() === key.toLowerCase()) {
                // Don't trigger if user is typing in input
                if (!options.allowInInput && ['INPUT', 'TEXTAREA'].includes(event.target.tagName)) {
                    return;
                }
                
                event.preventDefault();
                callback(event);
            }
        };
        
        document.addEventListener('keydown', handler);
        return handler; // Return for potential removal
    },
    
    /**
     * Set focus to element and scroll into view
     */
    setFocus(element) {
        element.focus();
        element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    },
    
    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * Throttle function
     */
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    /**
     * Check if user prefers reduced motion
     */
    prefersReducedMotion() {
        return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    },
    
    /**
     * Get contrast color for background
     */
    getContrastColor(hexColor) {
        // Convert hex to RGB
        const r = parseInt(hexColor.substr(1, 2), 16);
        const g = parseInt(hexColor.substr(3, 2), 16);
        const b = parseInt(hexColor.substr(5, 2), 16);
        
        // Calculate luminance
        const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
        
        return luminance > 0.5 ? '#000000' : '#ffffff';
    }
};

// Make available globally
window.DOMUtils = DOMUtils;

