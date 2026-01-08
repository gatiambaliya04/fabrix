// Enhancer Page JavaScript

// Global variables
let uploadedFilename = null;
let originalWidth = 0;
let originalHeight = 0;
let enhancedFilename = null;
let currentZoom = 1;
let currentUnit = 'pixels'; // 'pixels' or 'inches'

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadSection = document.getElementById('uploadSection');
const controlsSection = document.getElementById('controlsSection');
const previewSection = document.getElementById('previewSection');
const loadingSpinner = document.getElementById('loadingSpinner');
const alertBox = document.getElementById('alertBox');

// Form controls
const widthInput = document.getElementById('widthInput');
const heightInput = document.getElementById('heightInput');
const ppiHorizontalInput = document.getElementById('ppiHorizontal');
const ppiVerticalInput = document.getElementById('ppiVertical');
const maintainAspectCheckbox = document.getElementById('maintainAspect');
const outputFormatSelect = document.getElementById('outputFormat');

// Buttons
const enhanceBtn = document.getElementById('enhanceBtn');
const resetBtn = document.getElementById('resetBtn');
const downloadBtn = document.getElementById('downloadBtn');
const sendToOutlinerBtn = document.getElementById('sendToOutlinerBtn');

// Preview elements
const originalPreview = document.getElementById('originalPreview');
const enhancedPreview = document.getElementById('enhancedPreview');
const zoomSlider = document.getElementById('zoomSlider');
const zoomValue = document.getElementById('zoomValue');

// Image info
const imageInfoDiv = document.getElementById('imageInfo');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

// Setup all event listeners
function setupEventListeners() {
    // Upload area events
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);

    // Unit toggle
    const unitRadios = document.querySelectorAll('input[name="dimensionUnit"]');
    unitRadios.forEach(radio => {
        radio.addEventListener('change', handleUnitChange);
    });

    // Dimension inputs
    widthInput.addEventListener('input', handleWidthChange);
    heightInput.addEventListener('input', handleHeightChange);
    maintainAspectCheckbox.addEventListener('change', handleAspectRatioToggle);

    // Buttons
    enhanceBtn.addEventListener('click', handleEnhance);
    resetBtn.addEventListener('click', handleReset);
    downloadBtn.addEventListener('click', handleDownload);
    sendToOutlinerBtn.addEventListener('click', handleSendToOutliner);

    // Zoom slider
    zoomSlider.addEventListener('input', handleZoomChange);
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
            originalWidth = data.image_info.width;
            originalHeight = data.image_info.height;

            // Populate form with original dimensions
            widthInput.value = originalWidth;
            heightInput.value = originalHeight;

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

// Handle unit change (pixels/inches)
function handleUnitChange(e) {
    const newUnit = e.target.value;
    const ppiH = parseInt(ppiHorizontalInput.value) || 72;
    const ppiV = parseInt(ppiVerticalInput.value) || 72;
    
    const currentWidth = parseFloat(widthInput.value);
    const currentHeight = parseFloat(heightInput.value);
    
    if (currentWidth && currentHeight) {
        if (newUnit === 'inches' && currentUnit === 'pixels') {
            // Convert pixels to inches
            widthInput.value = (currentWidth / ppiH).toFixed(2);
            heightInput.value = (currentHeight / ppiV).toFixed(2);
        } else if (newUnit === 'pixels' && currentUnit === 'inches') {
            // Convert inches to pixels
            widthInput.value = Math.round(currentWidth * ppiH);
            heightInput.value = Math.round(currentHeight * ppiV);
        }
    }
    
    currentUnit = newUnit;
    
    // Update labels
    document.getElementById('widthLabel').textContent = `Width (${newUnit})`;
    document.getElementById('heightLabel').textContent = `Height (${newUnit})`;
    
    // Update input step
    if (newUnit === 'inches') {
        widthInput.step = '0.01';
        heightInput.step = '0.01';
    } else {
        widthInput.step = '1';
        heightInput.step = '1';
    }
}

// Handle width input change
function handleWidthChange() {
    if (maintainAspectCheckbox.checked && originalWidth > 0 && originalHeight > 0) {
        const newWidth = parseFloat(widthInput.value);
        if (!isNaN(newWidth) && newWidth > 0) {
            const aspectRatio = originalHeight / originalWidth;
            const newHeight = newWidth * aspectRatio;
            heightInput.value = currentUnit === 'inches' ? newHeight.toFixed(2) : Math.round(newHeight);
        }
    }
}

// Handle height input change
function handleHeightChange() {
    if (maintainAspectCheckbox.checked && originalWidth > 0 && originalHeight > 0) {
        const newHeight = parseFloat(heightInput.value);
        if (!isNaN(newHeight) && newHeight > 0) {
            const aspectRatio = originalWidth / originalHeight;
            const newWidth = newHeight * aspectRatio;
            widthInput.value = currentUnit === 'inches' ? newWidth.toFixed(2) : Math.round(newWidth);
        }
    }
}

// Handle aspect ratio toggle
function handleAspectRatioToggle() {
    if (maintainAspectCheckbox.checked) {
        // Lock to current dimensions
        handleWidthChange();
    }
}

// Handle enhance button click
async function handleEnhance() {
    if (!uploadedFilename) {
        showAlert('Please upload an image first', 'error');
        return;
    }

    let width = parseFloat(widthInput.value);
    let height = parseFloat(heightInput.value);
    const ppiH = parseInt(ppiHorizontalInput.value);
    const ppiV = parseInt(ppiVerticalInput.value);

    // Convert inches to pixels if needed
    if (currentUnit === 'inches') {
        width = Math.round(width * ppiH);
        height = Math.round(height * ppiV);
    } else {
        width = Math.round(width);
        height = Math.round(height);
    }

    // Validate inputs
    if (isNaN(width) || width <= 0 || isNaN(height) || height <= 0) {
        showAlert('Please enter valid dimensions', 'error');
        return;
    }

    if (isNaN(ppiH) || ppiH < 1 || ppiH > 1200 || isNaN(ppiV) || ppiV < 1 || ppiV > 1200) {
        showAlert('PPI values must be between 1 and 1200', 'error');
        return;
    }

    // Show loading
    showLoading('Enhancing image... This may take a moment.');
    enhanceBtn.disabled = true;

    try {
        const response = await fetch('/api/enhance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: uploadedFilename,
                width: width,
                height: height,
                ppi_horizontal: ppiH,
                ppi_vertical: ppiV,
                maintain_aspect: maintainAspectCheckbox.checked,
                format: outputFormatSelect.value
            })
        });

        const data = await response.json();

        if (data.success) {
            enhancedFilename = data.enhanced_url.split('/').pop();
            
            // Display preview
            displayPreview(data.original_url, data.enhanced_url);
            
            // Show preview section
            controlsSection.classList.add('hidden');
            previewSection.classList.remove('hidden');

            showAlert('Image enhanced successfully!', 'success');
        } else {
            showAlert(data.error || 'Enhancement failed', 'error');
        }
    } catch (error) {
        console.error('Enhancement error:', error);
        showAlert('Failed to enhance image. Please try again.', 'error');
    } finally {
        hideLoading();
        enhanceBtn.disabled = false;
    }
}

// Display preview images
function displayPreview(originalUrl, enhancedUrl) {
    originalPreview.src = originalUrl;
    enhancedPreview.src = enhancedUrl;
    
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
    enhancedPreview.style.transform = scale;
}

// Handle download button
function handleDownload() {
    if (!enhancedFilename) {
        showAlert('No enhanced image available', 'error');
        return;
    }

    const downloadUrl = `/api/download/enhanced/${enhancedFilename}`;
    
    // Create temporary link and click it
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = enhancedFilename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showAlert('Download started!', 'success');
}

// Handle send to outliner button
function handleSendToOutliner() {
    if (!enhancedFilename) {
        showAlert('No enhanced image available', 'error');
        return;
    }

    // Store enhanced filename in session storage
    sessionStorage.setItem('enhancedImage', enhancedFilename);
    
    // Redirect to outliner page
    window.location.href = '/outliner';
}

// Handle reset button
function handleReset() {
    // Reset all variables
    uploadedFilename = null;
    originalWidth = 0;
    originalHeight = 0;
    enhancedFilename = null;
    currentZoom = 1;

    // Reset form
    fileInput.value = '';
    widthInput.value = '';
    heightInput.value = '';
    ppiHorizontalInput.value = 72;
    ppiVerticalInput.value = 72;
    maintainAspectCheckbox.checked = true;
    outputFormatSelect.value = 'png';

    // Reset UI
    uploadSection.classList.remove('hidden');
    controlsSection.classList.add('hidden');
    previewSection.classList.add('hidden');
    imageInfoDiv.classList.remove('active');
    alertBox.classList.remove('active');

    // Clear previews
    originalPreview.src = '';
    enhancedPreview.src = '';
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