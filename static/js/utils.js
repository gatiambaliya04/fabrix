// Utility Functions for Image Enhancer and Outliner

/**
 * Format file size in human-readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Validate image file type
 * @param {File} file - File object to validate
 * @returns {boolean} True if valid image type
 */
function isValidImageType(file) {
    const validTypes = [
        'image/png',
        'image/jpeg',
        'image/jpg',
        'image/bmp',
        'image/tiff',
        'image/webp'
    ];
    return validTypes.includes(file.type);
}

/**
 * Validate file size
 * @param {File} file - File object to validate
 * @param {number} maxSizeMB - Maximum size in MB (default: 50)
 * @returns {boolean} True if file size is within limit
 */
function isValidFileSize(file, maxSizeMB = 50) {
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    return file.size <= maxSizeBytes;
}

/**
 * Calculate aspect ratio locked dimensions
 * @param {number} originalWidth - Original width
 * @param {number} originalHeight - Original height
 * @param {number} newValue - New value for changed dimension
 * @param {string} changedDimension - Which dimension changed ('width' or 'height')
 * @returns {object} Object with calculated width and height
 */
function calculateAspectRatioDimensions(originalWidth, originalHeight, newValue, changedDimension) {
    if (changedDimension === 'width') {
        const aspectRatio = originalHeight / originalWidth;
        return {
            width: newValue,
            height: Math.round(newValue * aspectRatio)
        };
    } else {
        const aspectRatio = originalWidth / originalHeight;
        return {
            width: Math.round(newValue * aspectRatio),
            height: newValue
        };
    }
}

/**
 * Convert pixels to inches based on PPI
 * @param {number} pixels - Number of pixels
 * @param {number} ppi - Pixels per inch
 * @returns {number} Dimension in inches
 */
function pixelsToInches(pixels, ppi) {
    return (pixels / ppi).toFixed(2);
}

/**
 * Convert inches to pixels based on PPI
 * @param {number} inches - Dimension in inches
 * @param {number} ppi - Pixels per inch
 * @returns {number} Number of pixels
 */
function inchesToPixels(inches, ppi) {
    return Math.round(inches * ppi);
}

/**
 * Debounce function to limit rate of function execution
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Show a toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type of notification ('success', 'error', 'info', 'warning')
 * @param {number} duration - Duration in milliseconds (default: 3000)
 */
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // Style the toast
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 6px;
        color: white;
        font-size: 14px;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    
    // Set background color based on type
    const colors = {
        success: '#50c878',
        error: '#e74c3c',
        info: '#4a90e2',
        warning: '#f39c12'
    };
    toast.style.backgroundColor = colors[type] || colors.info;
    
    // Add animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
    
    // Add to document
    document.body.appendChild(toast);
    
    // Remove after duration
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            document.body.removeChild(toast);
            document.head.removeChild(style);
        }, 300);
    }, duration);
}

/**
 * Create a loading overlay
 * @param {string} message - Loading message
 * @returns {HTMLElement} Loading overlay element
 */
function createLoadingOverlay(message = 'Processing...') {
    const overlay = document.createElement('div');
    overlay.id = 'loadingOverlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    `;
    
    const spinner = document.createElement('div');
    spinner.style.cssText = `
        border: 4px solid rgba(255, 255, 255, 0.3);
        border-top: 4px solid white;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
    `;
    
    const text = document.createElement('p');
    text.textContent = message;
    text.style.cssText = `
        color: white;
        margin-top: 20px;
        font-size: 16px;
    `;
    
    overlay.appendChild(spinner);
    overlay.appendChild(text);
    
    // Add spin animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
    
    return overlay;
}

/**
 * Show loading overlay
 * @param {string} message - Loading message
 */
function showLoadingOverlay(message = 'Processing...') {
    // Remove existing overlay if present
    removeLoadingOverlay();
    
    const overlay = createLoadingOverlay(message);
    document.body.appendChild(overlay);
}

/**
 * Remove loading overlay
 */
function removeLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        document.body.removeChild(overlay);
    }
}

/**
 * Download file from URL
 * @param {string} url - URL of the file to download
 * @param {string} filename - Name for the downloaded file
 */
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise} Promise that resolves when text is copied
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        const success = document.execCommand('copy');
        document.body.removeChild(textarea);
        return success;
    }
}

/**
 * Get image dimensions from file
 * @param {File} file - Image file
 * @returns {Promise} Promise that resolves with {width, height}
 */
function getImageDimensions(file) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        const url = URL.createObjectURL(file);
        
        img.onload = () => {
            URL.revokeObjectURL(url);
            resolve({
                width: img.width,
                height: img.height
            });
        };
        
        img.onerror = () => {
            URL.revokeObjectURL(url);
            reject(new Error('Failed to load image'));
        };
        
        img.src = url;
    });
}

/**
 * Compress image quality
 * @param {File} file - Image file to compress
 * @param {number} quality - Quality (0-1)
 * @returns {Promise} Promise that resolves with compressed blob
 */
function compressImage(file, quality = 0.8) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                
                canvas.toBlob((blob) => {
                    resolve(blob);
                }, 'image/jpeg', quality);
            };
            img.onerror = reject;
            img.src = e.target.result;
        };
        
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

/**
 * Parse URL parameters
 * @returns {Object} Object with URL parameters
 */
function getURLParameters() {
    const params = {};
    const searchParams = new URLSearchParams(window.location.search);
    
    for (const [key, value] of searchParams) {
        params[key] = value;
    }
    
    return params;
}

/**
 * Validate numeric input within range
 * @param {number} value - Value to validate
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @returns {boolean} True if valid
 */
function isValidRange(value, min, max) {
    return !isNaN(value) && value >= min && value <= max;
}

/**
 * Clamp value between min and max
 * @param {number} value - Value to clamp
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @returns {number} Clamped value
 */
function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
}

/**
 * Format duration in human-readable format
 * @param {number} seconds - Duration in seconds
 * @returns {string} Formatted duration
 */
function formatDuration(seconds) {
    if (seconds < 60) {
        return `${Math.round(seconds)}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
}

// Export functions if using modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatFileSize,
        isValidImageType,
        isValidFileSize,
        calculateAspectRatioDimensions,
        pixelsToInches,
        inchesToPixels,
        debounce,
        showToast,
        showLoadingOverlay,
        removeLoadingOverlay,
        downloadFile,
        copyToClipboard,
        getImageDimensions,
        compressImage,
        getURLParameters,
        isValidRange,
        clamp,
        formatDuration
    };
}