/**
 * Cloudry.in — Shared frontend utilities
 * Handles API calls, file uploads, downloads, and UI state.
 */

const API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api/v1'
    : 'https://api.cloudry.in/api/v1';

/**
 * Submit a form with files to the API and trigger download of the result.
 */
async function submitTool(endpoint, formData, outputFilename) {
    const statusEl = document.getElementById('status');
    const resultEl = document.getElementById('result');
    
    try {
        setStatus('processing', 'Processing...');
        
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(err.detail || err.error?.message || `Error ${response.status}`);
        }

        const contentType = response.headers.get('content-type');
        
        // If JSON response, show it
        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();
            setStatus('success', 'Done!');
            showJsonResult(data);
            return data;
        }

        // Otherwise, download the file
        const blob = await response.blob();
        downloadBlob(blob, outputFilename || 'output', contentType);
        setStatus('success', `Done! File downloaded (${formatSize(blob.size)})`);
        return blob;

    } catch (error) {
        setStatus('error', error.message);
        throw error;
    }
}

/**
 * Submit a form and show JSON result (for hash, validate, etc.)
 */
async function submitToolJson(endpoint, formData) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(err.detail || err.error?.message || `Error ${response.status}`);
    }

    return await response.json();
}

function downloadBlob(blob, filename, contentType) {
    // Try native download for mobile compatibility
    if (navigator.userAgent.match(/iPhone|iPad|Android/i)) {
        // Mobile: open in new tab (allows save via long-press or share)
        const url = URL.createObjectURL(blob);
        window.open(url, '_blank');
        setTimeout(() => URL.revokeObjectURL(url), 60000);
        return;
    }
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function setStatus(type, message) {
    const el = document.getElementById('status');
    if (!el) return;
    
    const colors = {
        processing: 'text-blue-600',
        success: 'text-green-600',
        error: 'text-red-600',
        idle: 'text-gray-500',
    };
    
    el.className = `mt-4 text-sm font-medium ${colors[type] || colors.idle}`;
    el.textContent = message;
}

function showJsonResult(data) {
    const el = document.getElementById('result');
    if (!el) return;
    el.innerHTML = `<pre class="bg-gray-100 p-4 rounded-lg text-sm overflow-x-auto">${JSON.stringify(data, null, 2)}</pre>`;
    el.classList.remove('hidden');
}

function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function getSelectedFiles(inputId) {
    const input = document.getElementById(inputId);
    return input?.files || [];
}
