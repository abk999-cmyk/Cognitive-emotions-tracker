/**
 * Visualizations Module
 * Wraps Chart.js for emotion timeline sparklines
 */

class EmotionTimeline {
    constructor(canvasId, maxDataPoints = 120) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.maxDataPoints = maxDataPoints;
        this.timelineEmotions = EmotionMetadata.getTimelineEmotions();
        
        // Ring buffer for data
        this.dataBuffer = {};
        this.labels = [];
        
        // Initialize buffers
        this.timelineEmotions.forEach(emotion => {
            this.dataBuffer[emotion] = [];
        });
        
        // Chart instance
        this.chart = null;
        
        // Debounced update
        this.debouncedUpdate = DOMUtils.debounce(() => this.updateChart(), 250);
        
        this.initChart();
    }
    
    /**
     * Initialize Chart.js instance
     */
    initChart() {
        const datasets = this.timelineEmotions.map((emotion, index) => {
            const meta = EmotionMetadata.getMetadata(emotion);
            const colors = this.getEmotionColor(emotion);
            
            return {
                label: `${meta.icon} ${emotion.charAt(0).toUpperCase() + emotion.slice(1)}`,
                data: [],
                borderColor: colors.border,
                backgroundColor: colors.background,
                borderWidth: 2,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 4,
                fill: false
            };
        });
        
        this.chart = new Chart(this.ctx, {
            type: 'line',
            data: {
                labels: this.labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: DOMUtils.prefersReducedMotion() ? 0 : 200
                },
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: '#e0e0e0',
                            usePointStyle: true,
                            padding: 15,
                            font: {
                                size: 11
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#667eea',
                        borderWidth: 1,
                        padding: 10,
                        displayColors: true,
                        callbacks: {
                            label: (context) => {
                                const value = context.parsed.y;
                                return `${context.dataset.label}: ${value.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#9e9e9e',
                            maxTicksLimit: 6,
                            font: {
                                size: 10
                            }
                        }
                    },
                    y: {
                        display: true,
                        min: 0,
                        max: 1,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#9e9e9e',
                            stepSize: 0.2,
                            font: {
                                size: 10
                            },
                            callback: (value) => value.toFixed(1)
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Get color scheme for emotion
     */
    getEmotionColor(emotion) {
        const colorMap = {
            'happy': { border: '#4caf50', background: 'rgba(76, 175, 80, 0.1)' },
            'engaged': { border: '#667eea', background: 'rgba(102, 126, 234, 0.1)' },
            'anxious': { border: '#ff9800', background: 'rgba(255, 152, 0, 0.1)' },
            'confused': { border: '#9c27b0', background: 'rgba(156, 39, 176, 0.1)' },
            'excited': { border: '#f093fb', background: 'rgba(240, 147, 251, 0.1)' }
        };
        
        return colorMap[emotion] || { border: '#ffffff', background: 'rgba(255, 255, 255, 0.1)' };
    }
    
    /**
     * Add new data point
     */
    addDataPoint(emotions, timestamp = null) {
        // Add to ring buffer
        this.timelineEmotions.forEach(emotion => {
            const value = emotions[emotion] || 0;
            this.dataBuffer[emotion].push(value);
            
            // Maintain max size
            if (this.dataBuffer[emotion].length > this.maxDataPoints) {
                this.dataBuffer[emotion].shift();
            }
        });
        
        // Add label (time)
        const time = timestamp ? new Date(timestamp * 1000) : new Date();
        const label = time.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        });
        this.labels.push(label);
        
        if (this.labels.length > this.maxDataPoints) {
            this.labels.shift();
        }
        
        // Debounced chart update
        this.debouncedUpdate();
    }
    
    /**
     * Update chart with current buffer
     */
    updateChart() {
        if (!this.chart) return;
        
        // Update datasets
        this.chart.data.labels = this.labels;
        this.chart.data.datasets.forEach((dataset, index) => {
            const emotion = this.timelineEmotions[index];
            dataset.data = this.dataBuffer[emotion];
        });
        
        this.chart.update('none'); // No animation for performance
    }
    
    /**
     * Clear timeline
     */
    clear() {
        this.timelineEmotions.forEach(emotion => {
            this.dataBuffer[emotion] = [];
        });
        this.labels = [];
        this.updateChart();
    }
    
    /**
     * Resize chart
     */
    resize() {
        if (this.chart) {
            this.chart.resize();
        }
    }
}

// Make available globally
window.EmotionTimeline = EmotionTimeline;

