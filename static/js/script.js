// Animated text rotation
const words = [
    'программиста', 'дизайнера', 'архитектора', 'менеджера', 'аналитика',
    'DevOps', 'тестировщика', 'документацию', 'решение', 'команду'
];

let currentWordIndex = 0;
let currentCharIndex = 0;
let isDeleting = false;
let typeSpeed = 100;

function typeEffect() {
    const animatedText = document.getElementById('animatedText');
    if (!animatedText) return;
    
    const currentWord = words[currentWordIndex];
    
    if (isDeleting) {
        animatedText.textContent = currentWord.substring(0, currentCharIndex - 1);
        currentCharIndex--;
        typeSpeed = 50;
    } else {
        animatedText.textContent = currentWord.substring(0, currentCharIndex + 1);
        currentCharIndex++;
        typeSpeed = 100;
    }
    
    if (!isDeleting && currentCharIndex === currentWord.length) {
        isDeleting = true;
        typeSpeed = 2000; // Pause before deleting
    } else if (isDeleting && currentCharIndex === 0) {
        isDeleting = false;
        currentWordIndex = (currentWordIndex + 1) % words.length;
        typeSpeed = 500; // Pause before typing next word
    }
    
    setTimeout(typeEffect, typeSpeed);
}

// Search functionality
function initSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const resultsSection = document.getElementById('resultsSection');
    const resultsContainer = document.getElementById('resultsContainer');
    
    // Check if elements exist
    if (!searchInput || !searchBtn || !resultsSection || !resultsContainer) {
        console.log('Search elements not found on this page');
        return;
    }

    // Auto-resize textarea
    function autoResize() {
        // Reset height to calculate new height
        searchInput.style.height = 'auto';
        
        // Get the actual content dimensions
        const style = window.getComputedStyle(searchInput);
        const paddingLeft = parseInt(style.paddingLeft);
        const paddingRight = parseInt(style.paddingRight);
        
        // Calculate available width (excluding button space on the right)
        const containerWidth = searchInput.offsetWidth;
        const buttonSpace = 52; // space reserved for the search button (36px + margins)
        const availableWidth = containerWidth - paddingLeft - paddingRight - buttonSpace;
        
        // Measure text width
        const textWidth = getTextWidth(searchInput.value, searchInput);
        
        // Check if we need multiple lines or if scrollHeight indicates wrapping
        const needsMultipleLines = textWidth > availableWidth || searchInput.scrollHeight > 52;
        
        if (needsMultipleLines) {
            // Allow natural expansion
            const newHeight = Math.min(searchInput.scrollHeight, 150);
            searchInput.style.height = newHeight + 'px';
        } else {
            // Keep single line
            searchInput.style.height = '52px';
        }
    }
    
    // Helper function to measure text width more accurately (keeping for potential future use)
    function getTextWidth(text, element) {
        // Create a temporary span to measure text
        const tempSpan = document.createElement('span');
        tempSpan.style.position = 'absolute';
        tempSpan.style.visibility = 'hidden';
        tempSpan.style.whiteSpace = 'nowrap';
        tempSpan.style.font = window.getComputedStyle(element).font;
        tempSpan.textContent = text;
        
        document.body.appendChild(tempSpan);
        const width = tempSpan.offsetWidth;
        document.body.removeChild(tempSpan);
        
        return width;
    }
    
    // Character limit handler
    function handleCharacterLimit(e) {
        const maxLength = 100;
        if (searchInput.value.length >= maxLength && e.key !== 'Backspace' && e.key !== 'Delete' && !e.ctrlKey) {
            e.preventDefault();
        }
    }
    
    // Update character counter
    function updateCharacterCounter() {
        const charCount = document.getElementById('charCount');
        const counter = document.getElementById('characterCounter');
        const currentLength = searchInput.value.length;
        
        if (charCount) {
            charCount.textContent = currentLength;
            
            // Update counter color based on remaining characters
            counter.classList.remove('warning', 'danger');
            if (currentLength >= 90) {
                counter.classList.add('danger');
            } else if (currentLength >= 80) {
                counter.classList.add('warning');
            }
        }
    }

    // Add event listeners for auto-resize and character limit
    searchInput.addEventListener('input', () => {
        // Enforce character limit
        if (searchInput.value.length > 100) {
            searchInput.value = searchInput.value.substring(0, 100);
        }
        updateCharacterCounter();
        autoResize();
    });
    
    searchInput.addEventListener('keydown', handleCharacterLimit);
    
    searchInput.addEventListener('paste', (e) => {
        setTimeout(() => {
            // Enforce character limit after paste
            if (searchInput.value.length > 100) {
                searchInput.value = searchInput.value.substring(0, 100);
            }
            updateCharacterCounter();
            autoResize();
        }, 0);
    });
    
    // Initialize character counter
    updateCharacterCounter();

    // Search button handler
    searchBtn.addEventListener('click', function() {
        performSearch();
    });
    
    // Enter key handler (Ctrl+Enter or Shift+Enter for new line)
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey) {
            e.preventDefault();
            performSearch();
        }
    });

    function performSearch() {
        const query = searchInput.value.trim();
        if (!query) return;
        
        console.log('Performing search for:', query);
        
        // Create or get the extracted info container for loading state
        let extractedContainer = document.querySelector('.extracted-info-container');
        if (!extractedContainer) {
            extractedContainer = document.createElement('div');
            extractedContainer.className = 'extracted-info-container';
            // Insert right after the search card
            const searchCard = document.querySelector('.search-card');
            searchCard.parentNode.insertBefore(extractedContainer, searchCard.nextSibling);
        }
        
        // Show loading state
        extractedContainer.innerHTML = '<div class="loading">Разбираем запрос...</div>';
        
        // Make actual API call to search endpoint
        fetch(`/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                console.log('Parsing results:', data);
                displayParsingResults(data.parsed, data.query);
            })
            .catch(error => {
                console.error('Parsing error:', error);
                extractedContainer.innerHTML = '<div class="error">Ошибка разбора запроса. Попробуйте снова.</div>';
            });
    }
    
    function displayParsingResults(parsed, originalQuery) {
        // Create or get the extracted info container that goes right below search
        let extractedContainer = document.querySelector('.extracted-info-container');
        if (!extractedContainer) {
            extractedContainer = document.createElement('div');
            extractedContainer.className = 'extracted-info-container';
            // Insert right after the search card
            const searchCard = document.querySelector('.search-card');
            searchCard.parentNode.insertBefore(extractedContainer, searchCard.nextSibling);
        }
        
        // Helper function to get requirement status
        function getRequirementStatus(fieldType, requirements) {
            const fieldMapping = {
                'course': 'курс',
                'user_type': 'тип пользователя',
                'faculty': 'факультет',
                'group': 'номер группы'
            };
            
            if (!requirements || !fieldMapping[fieldType]) {
                return '';
            }
            
            const russianField = fieldMapping[fieldType];
            const status = requirements[russianField];
            
            // Return empty string - we only need the CSS classes for visual indication
            return '';
        }

        // Helper function to get requirement class
        function getRequirementClass(fieldType, requirements) {
            const fieldMapping = {
                'course': 'курс',
                'user_type': 'тип пользователя',
                'faculty': 'факультет',
                'group': 'номер группы'
            };
            
            if (!requirements || !fieldMapping[fieldType]) {
                return '';
            }
            
            const russianField = fieldMapping[fieldType];
            const status = requirements[russianField];
            
            if (status === 'required') {
                return 'required';
            } else if (status === 'optional') {
                return 'optional';
            }
            
            return '';
        }
        
        let html = '';
        
        // Compact tags display
        html += '<div class="compact-tags">';
        html += '<div class="tags-row">';
        
        // Collect all tags with their status and data
        const allTags = [];
        
        // Skills tags (blue) - now with individual status
        if (parsed.skills_with_status && parsed.skills_with_status.length > 0) {
            parsed.skills_with_status.forEach((skillObj, originalIndex) => {
                let skill = skillObj.навык || skillObj.skill || skillObj;
                let status = skillObj.статус || skillObj.status || 'optional';
                let score = skillObj.баллы || skillObj.score || null;
                
                const statusClass = (status === 'required') ? 'required' : 'optional';
                
                let scoreDisplay = '';
                if (status === 'optional' && score) {
                    scoreDisplay = `<span class="skill-score" onclick="editScore(this, ${originalIndex})">${score}</span>`;
                }
                
                allTags.push({
                    html: `<div class="compact-tag skill-tag ${statusClass}" data-type="skill" data-index="${originalIndex}" data-score="${score || ''}">
                        <span class="tag-text" contenteditable="true">${skill}</span>
                        ${scoreDisplay}
                        <button class="remove-tag" onclick="removeTag(this)">×</button>
                    </div>`,
                    status: status,
                    type: 'skill'
                });
            });
        } else if (parsed.skills && parsed.skills.length > 0) {
            // Fallback для старого формата
            parsed.skills.forEach((skill, index) => {
                const statusText = getRequirementStatus('skill', parsed.requirements);
                const statusClass = getRequirementClass('skill', parsed.requirements);
                const status = statusClass === 'required' ? 'required' : 'optional';
                
                allTags.push({
                    html: `<div class="compact-tag skill-tag ${statusClass}" data-type="skill" data-index="${index}">
                        <span class="tag-text" contenteditable="true">${skill}${statusText}</span>
                        <button class="remove-tag" onclick="removeTag(this)">×</button>
                    </div>`,
                    status: status,
                    type: 'skill'
                });
            });
        }
        
        // Course tag (green)
        if (parsed.course) {
            const statusText = getRequirementStatus('course', parsed.requirements);
            const statusClass = getRequirementClass('course', parsed.requirements);
            const status = statusClass === 'required' ? 'required' : 'optional';
            
            allTags.push({
                html: `<div class="compact-tag course-tag ${statusClass}" data-type="course">
                    <span class="tag-text" contenteditable="true">${parsed.course}${statusText}</span>
                    <button class="remove-tag" onclick="removeTag(this)">×</button>
                </div>`,
                status: status,
                type: 'course'
            });
        }
        
        // User type tag (purple)
        if (parsed.user_type) {
            const statusText = getRequirementStatus('user_type', parsed.requirements);
            const statusClass = getRequirementClass('user_type', parsed.requirements);
            const status = statusClass === 'required' ? 'required' : 'optional';
            
            allTags.push({
                html: `<div class="compact-tag user-type-tag ${statusClass}" data-type="user_type">
                    <span class="tag-text" contenteditable="true">${parsed.user_type}${statusText}</span>
                    <button class="remove-tag" onclick="removeTag(this)">×</button>
                </div>`,
                status: status,
                type: 'user_type'
            });
        }
        
        // Faculty tag (orange)
        if (parsed.faculty) {
            const statusText = getRequirementStatus('faculty', parsed.requirements);
            const statusClass = getRequirementClass('faculty', parsed.requirements);
            const status = statusClass === 'required' ? 'required' : 'optional';
            
            allTags.push({
                html: `<div class="compact-tag faculty-tag ${statusClass}" data-type="faculty">
                    <span class="tag-text" contenteditable="true">${parsed.faculty}${statusText}</span>
                    <button class="remove-tag" onclick="removeTag(this)">×</button>
                </div>`,
                status: status,
                type: 'faculty'
            });
        }
        
        // Group tag (red)
        if (parsed.group) {
            const statusText = getRequirementStatus('group', parsed.requirements);
            const statusClass = getRequirementClass('group', parsed.requirements);
            const status = statusClass === 'required' ? 'required' : 'optional';
            
            allTags.push({
                html: `<div class="compact-tag group-tag ${statusClass}" data-type="group">
                    <span class="tag-text" contenteditable="true">${parsed.group}${statusText}</span>
                    <button class="remove-tag" onclick="removeTag(this)">×</button>
                </div>`,
                status: status,
                type: 'group'
            });
        }
        
        // Sort all tags: required first, then optional
        allTags.sort((a, b) => {
            if (a.status === 'required' && b.status !== 'required') return -1;
            if (a.status !== 'required' && b.status === 'required') return 1;
            return 0;
        });
        
        // Add sorted tags to HTML
        allTags.forEach(tag => {
            html += tag.html;
        });
        
        // Single add button with dropdown
        html += '<div class="add-tag-dropdown">';
        html += '<button class="add-tag-main" onclick="toggleAddDropdown()">+</button>';
        html += '<div class="add-dropdown-menu" id="addDropdown" style="display: none;">';
        html += '<div class="dropdown-item skill-dropdown" onclick="showAddInput(\'skill\')">Навык</div>';
        html += '<div class="dropdown-item course-dropdown" onclick="showAddInput(\'course\')">Курс</div>';
        html += '<div class="dropdown-item user-type-dropdown" onclick="showAddInput(\'user_type\')">Тип пользователя</div>';
        html += '<div class="dropdown-item faculty-dropdown" onclick="showAddInput(\'faculty\')">Факультет</div>';
        html += '<div class="dropdown-item group-dropdown" onclick="showAddInput(\'group\')">Группа</div>';
        html += '</div>';
        html += '</div>';
        
        html += '</div>'; // close tags-row
        
        // Input field for adding new tags (initially hidden)
        html += '<div class="add-input-container" id="addInputContainer" style="display: none;">';
        html += '<input type="text" id="newTagInput" placeholder="Введите значение..." onkeypress="handleAddInputKeypress(event)">';
        html += '<button class="confirm-add" onclick="confirmAddTag()">✓</button>';
        html += '<button class="cancel-add" onclick="cancelAddTag()">×</button>';
        html += '</div>';
        
        html += '</div>'; // close compact-tags
        
        extractedContainer.innerHTML = html;
        
        // Hide the old results section if it exists
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
    }
}

// New compact interface functions
let currentAddType = null;

function toggleAddDropdown() {
    const dropdown = document.getElementById('addDropdown');
    dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function closeDropdown(e) {
        if (!e.target.closest('.add-tag-dropdown')) {
            dropdown.style.display = 'none';
            document.removeEventListener('click', closeDropdown);
        }
    });
}

function showAddInput(type) {
    currentAddType = type;
    const dropdown = document.getElementById('addDropdown');
    const inputContainer = document.getElementById('addInputContainer');
    const input = document.getElementById('newTagInput');
    
    dropdown.style.display = 'none';
    inputContainer.style.display = 'flex';
    input.focus();
    
    // Update placeholder based on type
    const placeholders = {
        'skill': 'Введите навык...',
        'course': 'Введите курс...',
        'user_type': 'Введите тип пользователя...',
        'faculty': 'Введите факультет...',
        'group': 'Введите группу...'
    };
    input.placeholder = placeholders[type];
}

function handleAddInputKeypress(event) {
    if (event.key === 'Enter') {
        confirmAddTag();
    } else if (event.key === 'Escape') {
        cancelAddTag();
    }
}

function confirmAddTag() {
    const input = document.getElementById('newTagInput');
    const value = input.value.trim();
    
    if (value && currentAddType) {
        // Create new tag element
        const tagsRow = document.querySelector('.tags-row');
        const addDropdown = document.querySelector('.add-tag-dropdown');
        
        const newTag = document.createElement('div');
        newTag.className = `compact-tag ${currentAddType}-tag`;
        newTag.dataset.type = currentAddType;
        
        let tagContent = `
            <span class="tag-text" contenteditable="true">${value}</span>
            <button class="remove-tag" onclick="removeTag(this)">×</button>
        `;
        
        // Для навыков добавляем баллы по умолчанию
        if (currentAddType === 'skill') {
            const defaultScore = 3; // Средний балл по умолчанию
            newTag.classList.add('optional'); // Новые навыки по умолчанию необязательные
            newTag.dataset.score = defaultScore;
            tagContent = `
                <span class="tag-text" contenteditable="true">${value}</span>
                <span class="skill-score" onclick="editScore(this, -1)">${defaultScore}</span>
                <button class="remove-tag" onclick="removeTag(this)">×</button>
            `;
        }
        
        newTag.innerHTML = tagContent;
        
        // Insert before the add button
        tagsRow.insertBefore(newTag, addDropdown);
        
        // Reset input
        cancelAddTag();
    }
}

function cancelAddTag() {
    const inputContainer = document.getElementById('addInputContainer');
    const input = document.getElementById('newTagInput');
    
    inputContainer.style.display = 'none';
    input.value = '';
    currentAddType = null;
}

// Updated tag management functions
function removeTag(button) {
    const tag = button.parentElement;
    tag.remove();
}

function getTypeLabel(type) {
    const labels = {
        'skill': 'навык',
        'course': 'курс',
        'user_type': 'тип',
        'faculty': 'факультет',
        'group': 'группу'
    };
    return labels[type] || 'элемент';
}

function saveExtractedInfo() {
    const extractedData = {
        skills: [],
        course: null,
        user_type: null,
        faculty: null,
        group: null
    };
    
    // Collect all tags
    document.querySelectorAll('.compact-tag').forEach(tag => {
        const type = tag.dataset.type;
        const value = tag.querySelector('.tag-text').textContent.trim();
        
        if (type === 'skill') {
            extractedData.skills.push(value);
        } else {
            extractedData[type] = value;
        }
    });
    
    console.log('Сохранённые данные:', extractedData);
    
    // Show success message
    const actionsDiv = document.querySelector('.compact-actions');
    const successMsg = document.createElement('div');
    successMsg.className = 'success-message';
    successMsg.textContent = 'Сохранено!';
    actionsDiv.appendChild(successMsg);
    
    setTimeout(() => {
        successMsg.remove();
    }, 2000);
}

function clearAllTags() {
    if (confirm('Очистить все теги?')) {
        document.querySelectorAll('.compact-tag').forEach(tag => {
            tag.remove();
        });
    }
}

function toggleRawResponse() {
    const rawContent = document.querySelector('.raw-content');
    rawContent.style.display = rawContent.style.display === 'none' ? 'block' : 'none';
}

// Функция для редактирования баллов навыков
function editScore(scoreElement, index) {
    const currentScore = parseInt(scoreElement.textContent);
    const newScore = prompt(`Введите новый балл важности (1-5):`, currentScore);
    
    if (newScore !== null && !isNaN(newScore) && newScore >= 1 && newScore <= 5) {
        const intScore = parseInt(newScore);
        scoreElement.textContent = intScore;
        
        // Обновляем data-score атрибут родительского элемента
        const tagElement = scoreElement.closest('.compact-tag');
        tagElement.setAttribute('data-score', intScore);
        
        console.log(`Балл навыка обновлен на ${intScore}`);
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    typeEffect();
    initSearch();
}); 
