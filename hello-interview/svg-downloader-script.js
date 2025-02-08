// Function to get the last segment of the current URL path
function getLastPathSegment() {
    const path = window.location.pathname;
    const segments = path.split('/').filter(segment => segment.length > 0);
    return segments[segments.length - 1] || 'default';
}

// Function to process a single SVG
function processSVG(svg, index, prefix, targetWidth) {
    return new Promise((resolve, reject) => {
        try {
            console.log(`Processing SVG ${index}...`);
            
            // Get original SVG dimensions
            const originalWidth = svg.viewBox.baseVal.width || svg.width.baseVal.value;
            const originalHeight = svg.viewBox.baseVal.height || svg.height.baseVal.value;
            
            console.log(`Original dimensions for SVG ${index}: ${originalWidth}x${originalHeight}`);
            
            // Calculate height maintaining aspect ratio
            const targetHeight = Math.round((targetWidth * originalHeight) / originalWidth);
            
            // Get the SVG data
            const svgData = new XMLSerializer().serializeToString(svg);
            const svgBlob = new Blob([svgData], {type: 'image/svg+xml;charset=utf-8'});
            
            // Create the URL
            const DOMURL = window.URL || window.webkitURL || window;
            const url = DOMURL.createObjectURL(svgBlob);
            
            // Create a canvas element
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            // Create an image element
            const img = new Image();
            
            // Set up error handling for image loading
            img.onerror = (error) => {
                console.error(`Error loading SVG ${index}:`, error);
                reject(error);
            };
            
            img.onload = function() {
                try {
                    console.log(`Image ${index} loaded, converting to PNG...`);
                    
                    // Set canvas dimensions to target size
                    canvas.width = targetWidth;
                    canvas.height = targetHeight;
                    
                    // Draw the image on the canvas with the target dimensions
                    ctx.drawImage(img, 0, 0, targetWidth, targetHeight);
                    // Enable high-quality rendering
                    ctx.imageSmoothingEnabled = true;
                    ctx.imageSmoothingQuality = 'high';
                    
                    // Convert canvas to PNG
                    DOMURL.revokeObjectURL(url);
                    const imgURI = canvas.toDataURL('image/png', 1.0);
                    
                    // Create download link with prefix in filename
                    const downloadLink = document.createElement('a');
                    downloadLink.download = `${prefix}-${index}.png`;
                    downloadLink.href = imgURI;
                    
                    console.log(`Initiating download for image ${index}...`);
                    
                    // Add a small delay between downloads
                    setTimeout(() => {
                        document.body.appendChild(downloadLink);
                        downloadLink.click();
                        document.body.removeChild(downloadLink);
                        console.log(`Download completed for image ${index}`);
                        resolve();
                    }, index * 10); // 500ms delay between each download
                    
                } catch (error) {
                    console.error(`Error processing SVG ${index}:`, error);
                    reject(error);
                }
            };
            
            // Set image source to SVG URL
            // Enable crisp image rendering
            img.style.imageRendering = 'crisp-edges';
            img.src = url;
            
        } catch (error) {
            console.error(`Error in SVG ${index} main process:`, error);
            reject(error);
        }
    });
}

// Main function to convert SVGs to PNGs and download
async function downloadSVGAsPNG() {
    try {
        // Fixed width for all PNGs
        const targetWidth = 2500;
        
        // Get filename prefix from URL
        const prefix = getLastPathSegment();
        
        // Find all SVG elements on the page that don't have a class attribute
        const svgElements = Array.from(document.querySelectorAll('svg')).filter(svg => !svg.hasAttribute('class'));
        
        console.log(`Found ${svgElements.length} SVGs without class attribute`);
        
        // Process SVGs sequentially
        for (let i = 0; i < svgElements.length; i++) {
            try {
                await processSVG(svgElements[i], i, prefix, targetWidth);
            } catch (error) {
                console.error(`Failed to process SVG ${i}:`, error);
            }
        }
        
        console.log('All SVGs processed');
        
    } catch (error) {
        console.error('Error in main process:', error);
    }
}

// Execute the function
downloadSVGAsPNG().then(() => {
    console.log('Download process completed');
}).catch(error => {
    console.error('Error in download process:', error);
});