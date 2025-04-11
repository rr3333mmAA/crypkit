// API URL configuration
const API_BASE_URL = '/api/cryptocurrencies';
const ITEMS_PER_PAGE = 10;

// DOM Elements
const cryptoListElement = document.getElementById('crypto-list');
const loadingElement = document.getElementById('loading');
const addForm = document.getElementById('add-crypto-form');
const addDropdownBtn = document.getElementById('add-dropdown-btn');
const addDropdownContent = document.getElementById('add-dropdown-content');
const prevPageButton = document.getElementById('prev-page');
const nextPageButton = document.getElementById('next-page');
const currentPageElement = document.getElementById('current-page');
const deleteIconTemplate = document.getElementById('delete-icon-template');
const checkIconTemplate = document.getElementById('check-icon-template');

// State management
let currentPage = 1;
let totalItems = 0;
let editingItem = null;

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadCryptocurrencies();
    
    addForm.addEventListener('submit', handleAddCrypto);
    prevPageButton.addEventListener('click', () => changePage(-1));
    nextPageButton.addEventListener('click', () => changePage(1));
    
    // Dropdown toggle
    addDropdownBtn.addEventListener('click', toggleAddDropdown);
    
    // Close dropdown when clicking outside
    window.addEventListener('click', (e) => {
        if (!e.target.matches('#add-dropdown-btn') && !addDropdownContent.contains(e.target)) {
            closeAddDropdown();
        }
    });

    // Global event handlers for editing
    document.addEventListener('click', (e) => {
        const target = e.target;

        // Handle clicks on editable fields
        if (target.classList.contains('crypto-symbol') || target.classList.contains('crypto-platform')) {
            if (!target.isContentEditable) {
                startEditing(target);
            }
        } 
        // Handle clicks outside of editing fields
        else if (editingItem && !target.closest('.check-btn') && !target.classList.contains('crypto-symbol') && !target.classList.contains('crypto-platform')) {
            stopEditing(false);
        }
    });
});

// Dropdown functions
function toggleAddDropdown() {
    addDropdownContent.classList.toggle('show');
}

function closeAddDropdown() {
    addDropdownContent.classList.remove('show');
}

// API Functions
async function loadCryptocurrencies() {
    showLoading(true);
    try {
        const offset = (currentPage - 1) * ITEMS_PER_PAGE;
        const response = await fetch(`${API_BASE_URL}?offset=${offset}&limit=${ITEMS_PER_PAGE}`);
        if (!response.ok) throw new Error('Failed to load cryptocurrencies');
        
        const data = await response.json();
        totalItems = Array.isArray(data) ? data.length : 0;
        
        renderCryptocurrencies(data);
        updatePaginationState();
    } catch (error) {
        console.error('Error loading cryptocurrencies:', error);
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

async function getCoinPrice(cryptoId) {
    try {
        const response = await fetch(`${API_BASE_URL}/${cryptoId}/price?currency=usd`);
        if (!response.ok) {
            return 'N/A';
        }
        
        const data = await response.json();
        if (data && data.price) {
            return `$${data.price}`;
        }
        return '$0.00';
    } catch (error) {
        console.error('Error fetching price:', error);
        return 'N/A';
    }
}

async function addCryptocurrency(cryptoData) {
    showLoading(true);
    try {
        const response = await fetch(API_BASE_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(cryptoData),
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to add cryptocurrency');
        }
        
        const data = await response.json();
        loadCryptocurrencies(); // Refresh the list
        return data;
    } catch (error) {
        console.error('Error adding cryptocurrency:', error);
        showError(error.message);
        throw error;
    } finally {
        showLoading(false);
    }
}

async function updateCryptocurrency(id, cryptoData) {
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE_URL}/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(cryptoData),
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to update cryptocurrency');
        }
        
        const data = await response.json();
        loadCryptocurrencies(); // Refresh the list
        return data;
    } catch (error) {
        console.error('Error updating cryptocurrency:', error);
        showError(error.message);
        throw error;
    } finally {
        showLoading(false);
    }
}

async function deleteCryptocurrency(id) {
    if (!confirm('Are you sure you want to delete this cryptocurrency?')) {
        return;
    }
    
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE_URL}/${id}`, {
            method: 'DELETE',
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to delete cryptocurrency');
        }
        
        loadCryptocurrencies(); // Refresh the list
    } catch (error) {
        console.error('Error deleting cryptocurrency:', error);
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

// UI Functions
function renderCryptocurrencies(cryptocurrencies) {
    cryptoListElement.innerHTML = '';
    
    if (!Array.isArray(cryptocurrencies) || cryptocurrencies.length === 0) {
        cryptoListElement.innerHTML = '<div class="crypto-item">No cryptocurrencies found</div>';
        return;
    }
    
    cryptocurrencies.forEach(async (crypto) => {
        const cryptoItem = document.createElement('div');
        cryptoItem.className = 'crypto-item';
        cryptoItem.dataset.id = crypto.id;
        
        const price = await getCoinPrice(crypto.id, crypto.symbol);
        
        cryptoItem.innerHTML = `
            <div class="crypto-info">
                <span class="crypto-symbol" data-original="${crypto.symbol}">${crypto.symbol}</span>
                <span class="crypto-platform" data-original="${crypto.platform}">${crypto.platform}</span>
                <span class="crypto-price">${price}</span>
            </div>
            <div class="crypto-actions">
                <button class="icon-btn check-btn" title="Save changes">
                    ${checkIconTemplate.outerHTML.replace('id="check-icon-template"', '')}
                </button>
                <button class="icon-btn delete-btn" title="Delete cryptocurrency">
                    ${deleteIconTemplate.outerHTML.replace('id="delete-icon-template"', '')}
                </button>
            </div>
        `;
        
        cryptoListElement.appendChild(cryptoItem);
        
        // Add event listeners to the buttons
        const deleteBtn = cryptoItem.querySelector('.delete-btn');
        const checkBtn = cryptoItem.querySelector('.check-btn');
        
        deleteBtn.addEventListener('click', () => {
            deleteCryptocurrency(crypto.id);
        });
        
        checkBtn.addEventListener('click', () => {
            saveEdits(cryptoItem);
        });
    });
}

// Inline editing functions
function startEditing(element) {
    // If already editing something else, save or discard those changes first
    if (editingItem && editingItem !== element.closest('.crypto-item')) {
        stopEditing(false);
    }
    
    const cryptoItem = element.closest('.crypto-item');
    editingItem = cryptoItem;
    
    // Make the clicked element editable
    element.contentEditable = true;
    element.classList.add('editable');
    element.focus();
    
    // Select all text in the element
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(element);
    selection.removeAllRanges();
    selection.addRange(range);
    
    // Show the check button
    const checkBtn = cryptoItem.querySelector('.check-btn');
    checkBtn.classList.add('visible');
    
    // Event listener for Enter key
    element.addEventListener('keydown', handleEditKeydown);
}

function handleEditKeydown(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        saveEdits(editingItem);
    } else if (e.key === 'Escape') {
        e.preventDefault();
        stopEditing(false);
    }
}

function stopEditing(save = false) {
    if (!editingItem) return;
    
    const symbolElement = editingItem.querySelector('.crypto-symbol');
    const platformElement = editingItem.querySelector('.crypto-platform');
    
    // Remove editable state
    symbolElement.contentEditable = false;
    platformElement.contentEditable = false;
    symbolElement.classList.remove('editable');
    platformElement.classList.remove('editable');
    
    // Remove event listeners
    symbolElement.removeEventListener('keydown', handleEditKeydown);
    platformElement.removeEventListener('keydown', handleEditKeydown);
    
    if (!save) {
        // Restore original values
        symbolElement.textContent = symbolElement.getAttribute('data-original');
        platformElement.textContent = platformElement.getAttribute('data-original');
    }
    
    // Hide check button
    editingItem.querySelector('.check-btn').classList.remove('visible');
    
    editingItem = null;
}

async function saveEdits(cryptoItem) {
    const id = cryptoItem.dataset.id;
    const symbolElement = cryptoItem.querySelector('.crypto-symbol');
    const platformElement = cryptoItem.querySelector('.crypto-platform');
    
    const newSymbol = symbolElement.textContent.trim();
    const newPlatform = platformElement.textContent.trim();
    
    // Validate fields aren't empty
    if (!newSymbol || !newPlatform) {
        showError('Symbol and platform cannot be empty');
        return;
    }
    
    // Only update if something changed
    if (newSymbol !== symbolElement.getAttribute('data-original') || 
        newPlatform !== platformElement.getAttribute('data-original')) {
        
        const cryptoData = {
            symbol: newSymbol,
            platform: newPlatform
        };
        
        await updateCryptocurrency(id, cryptoData);
    }
    
    stopEditing(true);
}

function showLoading(isLoading) {
    loadingElement.style.display = isLoading ? 'block' : 'none';
    if (isLoading) {
        cryptoListElement.style.opacity = '0.5';
    } else {
        cryptoListElement.style.opacity = '1';
    }
}

function showError(message) {
    alert(`Error: ${message}`);
}

function changePage(direction) {
    const newPage = currentPage + direction;
    if (newPage < 1) return;
    
    currentPage = newPage;
    loadCryptocurrencies();
}

function updatePaginationState() {
    currentPageElement.textContent = currentPage;
    prevPageButton.disabled = currentPage === 1;
    
    // Since we don't know total pages, we disable next if we have fewer items than the page limit
    nextPageButton.disabled = totalItems < ITEMS_PER_PAGE;
}

// Form Handlers
async function handleAddCrypto(e) {
    e.preventDefault();
    
    const formData = new FormData(addForm);
    const cryptoData = {
        symbol: formData.get('symbol'),
        platform: formData.get('platform'),
    };
    
    await addCryptocurrency(cryptoData);
    addForm.reset();
    closeAddDropdown();
}