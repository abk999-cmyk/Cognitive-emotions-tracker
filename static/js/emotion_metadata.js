/**
 * Emotion Metadata Module
 * Provides definitions, categories, and icons for all emotions
 */

const EmotionMetadata = {
    // Emotion definitions and categories
    emotions: {
        // Visual emotions (from DeepFace)
        'happy': {
            category: 'visual',
            definition: 'Feeling joy, contentment, or pleasure',
            icon: '😊',
            group: 'Basic'
        },
        'sad': {
            category: 'visual',
            definition: 'Feeling sorrow, unhappiness, or grief',
            icon: '😢',
            group: 'Basic'
        },
        'angry': {
            category: 'visual',
            definition: 'Feeling strong displeasure or hostility',
            icon: '😠',
            group: 'Basic'
        },
        'fear': {
            category: 'visual',
            definition: 'Feeling afraid or anxious about a threat',
            icon: '😨',
            group: 'Basic'
        },
        'surprise': {
            category: 'visual',
            definition: 'Feeling astonishment or wonder',
            icon: '😲',
            group: 'Basic'
        },
        'disgust': {
            category: 'visual',
            definition: 'Feeling revulsion or strong disapproval',
            icon: '🤢',
            group: 'Basic'
        },
        'neutral': {
            category: 'visual',
            definition: 'Balanced emotional state without strong feelings',
            icon: '😐',
            group: 'Basic'
        },
        
        // Vocal emotions (from speech)
        'calm': {
            category: 'vocal',
            definition: 'Peaceful and composed state of mind',
            icon: '😌',
            group: 'Basic'
        },
        'excited': {
            category: 'vocal',
            definition: 'Energetic enthusiasm and eagerness',
            icon: '🤩',
            group: 'Basic'
        },
        'frustrated': {
            category: 'vocal',
            definition: 'Feeling blocked or prevented from progress',
            icon: '😤',
            group: 'Basic'
        },
        'engaged': {
            category: 'vocal',
            definition: 'Actively involved and focused',
            icon: '🤔',
            group: 'Basic'
        },
        'confused': {
            category: 'vocal',
            definition: 'Unable to understand or think clearly',
            icon: '😕',
            group: 'Basic'
        },
        'anxious': {
            category: 'vocal',
            definition: 'Feeling nervous or worried',
            icon: '😰',
            group: 'Basic'
        },
        'confident': {
            category: 'vocal',
            definition: 'Self-assured and certain',
            icon: '😎',
            group: 'Basic'
        },
        'interested': {
            category: 'vocal',
            definition: 'Curious and attentive',
            icon: '🧐',
            group: 'Basic'
        },
        'bored': {
            category: 'vocal',
            definition: 'Lacking interest or engagement',
            icon: '😑',
            group: 'Basic'
        },
        'curious': {
            category: 'vocal',
            definition: 'Eager to learn or know',
            icon: '🤨',
            group: 'Basic'
        },
        'stressed': {
            category: 'vocal',
            definition: 'Under mental or emotional pressure',
            icon: '😫',
            group: 'Basic'
        },
        
        // Derived/composite emotions
        'receptiveness': {
            category: 'derived',
            definition: 'Openness to new ideas and information (engagement + positive emotions)',
            icon: '👂',
            group: 'Derived'
        },
        'awareness': {
            category: 'derived',
            definition: 'Conscious attention and alertness (attention indicators)',
            icon: '👁️',
            group: 'Derived'
        },
        'trust': {
            category: 'derived',
            definition: 'Confidence in reliability (calm + happy + confident)',
            icon: '🤝',
            group: 'Derived'
        },
        'anticipation': {
            category: 'derived',
            definition: 'Expectation of future events (excited + curious)',
            icon: '⏰',
            group: 'Derived'
        },
        'relaxed': {
            category: 'derived',
            definition: 'Free from tension (calm + neutral)',
            icon: '😊',
            group: 'Derived'
        },
        'skeptical': {
            category: 'derived',
            definition: 'Doubtful or questioning (confused + neutral)',
            icon: '🤨',
            group: 'Derived'
        },
        'distracted': {
            category: 'derived',
            definition: 'Lacking focus (inverse of engaged)',
            icon: '😵',
            group: 'Derived'
        },
        'enthusiastic': {
            category: 'derived',
            definition: 'Intense excitement and interest (excited + happy)',
            icon: '🎉',
            group: 'Derived'
        },
        'contemplative': {
            category: 'derived',
            definition: 'Thoughtfully reflective (neutral + interested)',
            icon: '🤔',
            group: 'Derived'
        },
        'alert': {
            category: 'derived',
            definition: 'Quick to notice and respond (awareness + surprise)',
            icon: '⚡',
            group: 'Derived'
        }
    },
    
    /**
     * Get metadata for an emotion
     */
    getMetadata(emotion) {
        return this.emotions[emotion] || {
            category: 'unknown',
            definition: 'Unknown emotion',
            icon: '❓',
            group: 'Unknown'
        };
    },
    
    /**
     * Get all emotions in a category
     */
    getByCategory(category) {
        return Object.entries(this.emotions)
            .filter(([_, meta]) => meta.category === category)
            .map(([name, _]) => name);
    },
    
    /**
     * Get all emotions in a group
     */
    getByGroup(group) {
        return Object.entries(this.emotions)
            .filter(([_, meta]) => meta.group === group)
            .map(([name, _]) => name);
    },
    
    /**
     * Get emotion groups
     */
    getGroups() {
        return ['Basic', 'Derived'];
    },
    
    /**
     * Get top emotions for timeline display
     */
    getTimelineEmotions() {
        // Return 5 key emotions that are most informative
        return ['happy', 'engaged', 'anxious', 'confused', 'excited'];
    }
};

// Make available globally
window.EmotionMetadata = EmotionMetadata;

