// Outliner Page JavaScript

// Global variables
let uploadedFilename = null;
let outlinedFilename = null;
let useEnhancedImage = false;
let currentZoom = 1;

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadSection = document.getElementById('uploadSection');
const enhancedImageSection = document.getElementById('enhancedImageSection');
const controlsSection = document.getElementById('controlsSection');
const previewSection = document.getElementById('previewSection');
const loadingSpinner = document.getElementById('loadingSpinner');
const alertBox = document.getElementById('alertBox');

// Buttons
const useEnhancedBtn = document.getElementById('useEnhancedBtn');
const uploadNewBtn = document.getElementById('uploadNewBtn');
const extractBtn = document.getElementById('extractBtn');
const resetBtn = document.getElementById('resetBtn');
const downloadBtn = document.getElementById('downloadBtn');

// Form controls
const thicknessInput = document.getElementById('thicknessInput');
const outputFormatSelect = document.getElementById('outputFormat');

// Preview elements
const originalPreview = document.getElementById('originalPreview');
const outlinedPreview = document.getElementById('outlinedPreview');
const zoomSlider = document.getElementById('zoomSlider');
const zoomValue = document.getElementById('zoomValue');

// Image info
const imageInfoDiv = document.getElementById('imageInfo');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkForEnhancedImage();
    setupEventListeners();
});

// Check if there's an enhanced image from the enhancer page
function checkForEnhancedImage() {
    const enhancedImage = sessionStorage.getItem('enhancedImage');
    
    if (enhancedImage) {
        // Show option to use enhanced image
        enhancedImageSection.classList.remove('hidden');
        uploadSection.classList.add('hidden');
    } else {
        // Show upload section
        enhancedImageSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');
    }
}

// Setup all event listeners
function setupEventListeners() {
    // Enhanced image buttons
    if (useEnhancedBtn) {
        useEnhancedBtn.addEventListener('click', handleUseEnhanced);
    }
    if (uploadNewBtn) {
        uploadNewBtn.addEventListener('click', handleUploadNew);
    }

    // Upload area events
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);

    // Buttons
    extractBtn.addEventListener('click', handleExtractOutline);
    resetBtn.addEventListener('click', handleReset);
    downloadBtn.addEventListener('click', handleDownload);

    // Zoom slider
    zoomSlider.addEventListener('input', handleZoomChange);
}

// Handle use enhanced image button
function handleUseEnhanced() {
    const enhancedImage = sessionStorage.getItem('enhancedImage');
    
    if (enhancedImage) {
        uploadedFilename = enhancedImage;
        useEnhancedImage = true;
        
        // Show controls section
        enhancedImageSection.classList.add('hidden');
        controlsSection.classList.remove('hidden');
        
        // Display image info
        displayEnhancedImageInfo();
        
        showAlert('Enhanced image loaded successfully!', 'success');
    }
}

// Handle upload new image button
function handleUploadNew() {
    // Clear session storage
    sessionStorage.removeItem('enhancedImage');
    
    // Show upload section
    enhancedImageSection.classList.add('hidden');
    uploadSection.classList.remove('hidden');
}

// Display enhanced image info
function displayEnhancedImageInfo() {
    imageInfoDiv.innerHTML = `
        <p><strong>Source:</strong> Enhanced image from enhancer</p>
        <p><strong>Ready for outline extraction</strong></p>
    `;
    imageInfoDiv.classList.add('active');
}

// Drag and drop handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// File selection handler
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// Handle file upload
async function handleFile(file) {
    // Validate file type
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 'image/tiff', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        showAlert('Please upload a valid image file (PNG, JPG, BMP, TIFF, WEBP)', 'error');
        return;
    }

    // Validate file size (50MB max)
    if (file.size > 50 * 1024 * 1024) {
        showAlert('File size must be less than 50MB', 'error');
        return;
    }

    // Show loading
    showLoading('Uploading image...');

    // Create form data
    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            uploadedFilename = data.filename;
            useEnhancedImage = false;

            // Show image info
            displayImageInfo(data.image_info);

            // Show controls section
            uploadSection.classList.add('hidden');
            controlsSection.classList.remove('hidden');

            showAlert('Image uploaded successfully!', 'success');
        } else {
            showAlert(data.error || 'Upload failed', 'error');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showAlert('Failed to upload image. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Display image information
function displayImageInfo(info) {
    imageInfoDiv.innerHTML = `
        <p><strong>Dimensions:</strong> ${info.width} x ${info.height} pixels</p>
        <p><strong>File Size:</strong> ${(info.file_size / 1024).toFixed(2)} KB</p>
        <p><strong>Format:</strong> ${info.format}</p>
        <p><strong>Color Mode:</strong> ${info.mode}</p>
    `;
    imageInfoDiv.classList.add('active');
}

// Handle extract outline button
async function handleExtractOutline() {
    if (!uploadedFilename) {
        showAlert('Please upload an image first', 'error');
        return;
    }

    const thickness = parseInt(thicknessInput.value);

    // Validate thickness
    if (isNaN(thickness) || thickness < 1 || thickness > 5) {
        showAlert('Thickness must be between 1 and 5', 'error');
        return;
    }

    // Show loading
    showLoading('Extracting outline... This may take a moment.');
    extractBtn.disabled = true;

    try {
        const requestBody = {
            thickness: thickness,
            format: outputFormatSelect.value
        };

        // Add appropriate filename based on source
        if (useEnhancedImage) {
            requestBody.use_enhanced = true;
            requestBody.enhanced_image = uploadedFilename;
        } else {
            requestBody.filename = uploadedFilename;
        }

        const response = await fetch('/api/extract-outline', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        if (data.success) {
            outlinedFilename = data.outlined_url.split('/').pop();
            
            // Display preview
            displayPreview(data.original_url, data.outlined_url);
            
            // Show preview section
            controlsSection.classList.add('hidden');
            previewSection.classList.remove('hidden');

            showAlert('Outline extracted successfully!', 'success');
        } else {
            showAlert(data.error || 'Outline extraction failed', 'error');
        }
    } catch (error) {
        console.error('Extraction error:', error);
        showAlert('Failed to extract outline. Please try again.', 'error');
    } finally {
        hideLoading();
        extractBtn.disabled = false;
    }
}

// Display preview images
function displayPreview(originalUrl, outlinedUrl) {
    originalPreview.src = originalUrl;
    outlinedPreview.src = outlinedUrl;
    
    // Reset zoom
    currentZoom = 1;
    zoomSlider.value = 100;
    zoomValue.textContent = '100%';
    applyZoom();
}

// Handle zoom slider change
function handleZoomChange() {
    currentZoom = zoomSlider.value / 100;
    zoomValue.textContent = zoomSlider.value + '%';
    applyZoom();
}

// Apply zoom to both images
function applyZoom() {
    const scale = `scale(${currentZoom})`;
    originalPreview.style.transform = scale;
    outlinedPreview.style.transform = scale;
}

// Handle download button
function handleDownload() {
    if (!outlinedFilename) {
        showAlert('No outlined image available', 'error');
        return;
    }

    const downloadUrl = `/api/download/outlined/${outlinedFilename}`;
    
    // Create temporary link and click it
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = outlinedFilename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showAlert('Download started!', 'success');
}

// Handle reset button
function handleReset() {
    // Reset all variables
    uploadedFilename = null;
    outlinedFilename = null;
    useEnhancedImage = false;
    currentZoom = 1;

    // Clear session storage
    sessionStorage.removeItem('enhancedImage');

    // Reset form
    fileInput.value = '';
    thicknessInput.value = 1;
    outputFormatSelect.value = 'png';

    // Reset UI
    enhancedImageSection.classList.add('hidden');
    uploadSection.classList.remove('hidden');
    controlsSection.classList.add('hidden');
    previewSection.classList.add('hidden');
    imageInfoDiv.classList.remove('active');
    alertBox.classList.remove('active');

    // Clear previews
    originalPreview.src = '';
    outlinedPreview.src = '';
}

// Show loading spinner
function showLoading(message = 'Processing...') {
    loadingSpinner.querySelector('.loading-text').textContent = message;
    loadingSpinner.classList.add('active');
}

// Hide loading spinner
function hideLoading() {
    loadingSpinner.classList.remove('active');
}

// Show alert message
function showAlert(message, type = 'info') {
    alertBox.textContent = message;
    alertBox.className = `alert alert-${type} active`;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        alertBox.classList.remove('active');
    }, 5000);
}