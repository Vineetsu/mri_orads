// State management
let selectedFiles = [];
let currentAnalysis = null;

// DOM Elements
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const fileGrid = document.getElementById('fileGrid');
const fileCount = document.getElementById('fileCount');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultsSection = document.getElementById('resultsSection');
const loadingIndicator = document.getElementById('loadingIndicator');
const resultsContent = document.getElementById('resultsContent');

// Event Listeners
uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', handleDragOver);
uploadArea.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleFileSelect);
analyzeBtn.addEventListener('click', analyzeImages);

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.style.borderColor = '#667eea';
    uploadArea.style.background = '#edf2f7';
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.style.borderColor = '#cbd5e0';
    uploadArea.style.background = '#f7fafc';
    
    const files = Array.from(e.dataTransfer.files);
    addFiles(files);
}

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    addFiles(files);
}

function addFiles(files) {
    const validFiles = files.filter(file => {
        const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
        return validTypes.includes(file.type);
    });
    
    selectedFiles = [...selectedFiles, ...validFiles];
    updateFileGrid();
}

function updateFileGrid() {
    fileGrid.innerHTML = '';
    fileCount.textContent = selectedFiles.length;
    
    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        const img = document.createElement('img');
        const reader = new FileReader();
        reader.onload = (e) => {
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
        
        const fileName = document.createElement('p');
        fileName.textContent = file.name.length > 20 ? 
            file.name.substring(0, 17) + '...' : file.name;
        
        const removeBtn = document.createElement('div');
        removeBtn.className = 'remove-file';
        removeBtn.innerHTML = '×';
        removeBtn.onclick = (e) => {
            e.stopPropagation();
            removeFile(index);
        };
        
        fileItem.appendChild(img);
        fileItem.appendChild(fileName);
        fileItem.appendChild(removeBtn);
        fileGrid.appendChild(fileItem);
    });
    
    analyzeBtn.disabled = selectedFiles.length === 0;
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFileGrid();
    
    // Reset file input
    fileInput.value = '';
}

async function analyzeImages() {
    if (selectedFiles.length === 0) return;
    
    // Show results section and loading
    resultsSection.style.display = 'block';
    loadingIndicator.style.display = 'block';
    resultsContent.innerHTML = '';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
    
    // Prepare form data
    const formData = new FormData();
    selectedFiles.forEach(file => {
        formData.append('images', file);
    });
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentAnalysis = data.analysis;
            displayResults(data.analysis);
        } else {
            displayError(data.error || 'Analysis failed');
        }
    } catch (error) {
        console.error('Error:', error);
        displayError('Failed to connect to server. Please try again.');
    } finally {
        loadingIndicator.style.display = 'none';
    }
}

function displayResults(analysis) {
    const oradsScore = analysis.orads_score;
    const riskDetails = analysis.risk_details || {};
    const cancerDetected = analysis.cancer_detected;
    
    let html = `
        <div class="score-card">
            <h3>O-RADS Score</h3>
            <div class="score-value">${oradsScore}</div>
            <div class="risk-level" style="color: ${riskDetails.risk_color || '#fff'}">
                ${riskDetails.risk_level || 'Risk Level'}
            </div>
            <p>Cancer Risk: ${riskDetails.risk_percentage || analysis.cancer_risk || 'N/A'}</p>
            <div class="cancer-status">
                ${cancerDetected ? 
                    '<span style="color: #e53e3e;">⚠️ Cancer Detected - High Suspicion</span>' : 
                    '<span style="color: #10B981;">✓ No Cancer Detected</span>'}
            </div>
        </div>
    `;
    
    if (analysis.analysis) {
        html += `
            <div class="analysis-section">
                <h3><i class="fas fa-microscope"></i> Image Analysis</h3>
                <p><strong>Lesion Type:</strong> ${analysis.analysis.lesion_type || 'N/A'}</p>
                <p><strong>Characteristics:</strong> ${analysis.analysis.characteristics || 'N/A'}</p>
                ${analysis.analysis.key_findings ? `
                    <h4>Key Findings:</h4>
                    <ul class="findings-list">
                        ${analysis.analysis.key_findings.map(finding => `<li>${finding}</li>`).join('')}
                    </ul>
                ` : ''}
            </div>
        `;
    }
    
    if (analysis.recommendations) {
        html += `
            <div class="recommendation-box">
                <h3><i class="fas fa-stethoscope"></i> Recommendations & Next Steps</h3>
                <p><strong>Immediate Actions:</strong> ${analysis.recommendations.next_steps || 'Consult with a radiologist'}</p>
                <p><strong>Recommended Consultations:</strong> ${analysis.recommendations.consulting_places || 'Gynecologic Oncologist, Radiologist'}</p>
                <p><strong>Additional Tests:</strong> ${analysis.recommendations.additional_tests || 'Consider biopsy, CT scan, or follow-up MRI'}</p>
                <p><strong>Follow-up:</strong> ${analysis.recommendations.follow_up || 'Schedule appointment within 2-4 weeks'}</p>
            </div>
        `;
    }
    
    html += `
        <div class="analysis-section">
            <h3><i class="fas fa-info-circle"></i> Important Notes</h3>
            <p>⚠️ This analysis is AI-generated and should not replace professional medical diagnosis.</p>
            <p>📋 Always consult with a qualified radiologist or gynecologic oncologist for proper evaluation.</p>
            <p>🏥 Recommended: Seek consultation at a tertiary care center with expertise in gynecologic oncology.</p>
        </div>
    `;
    
    resultsContent.innerHTML = html;
}

function displayError(error) {
    resultsContent.innerHTML = `
        <div class="analysis-section" style="background: #fed7d7;">
            <h3 style="color: #e53e3e;">Error</h3>
            <p>${error}</p>
            <p>Please try again or contact support if the issue persists.</p>
        </div>
    `;
}

// Reset styles on drag leave
uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = '#cbd5e0';
    uploadArea.style.background = '#f7fafc';
});