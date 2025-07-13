document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const suggestions = document.getElementById('suggestions');
    const resultsSection = document.getElementById('resultsSection');
    const resultsContainer = document.getElementById('resultsContainer');
    const animatedText = document.getElementById('animatedText');
    const charCount = document.getElementById('charCount');
    const characterCounter = document.getElementById('characterCounter');
    
    // Tags functionality (elements created dynamically after search)
    const addTagBtn = document.getElementById('addTagBtn'); // Will be null initially
    const tagDropdown = document.getElementById('tagDropdown'); // Will be null initially
    const tagsDisplay = document.getElementById('tagsDisplay'); // Will be null initially
    const tagsContainer = document.getElementById('tagsContainer'); // Will be null initially
    
    let activeTags = [];
    let requiredFields = [];

    // Animated text rotation
    const words = [
        'программиста',
        'дизайнера', 
        'архитектора',
        'менеджера',
        'аналитика',
        'DevOps',
        'тестировщика',
        'документацию',
        'решение',
        'команду'
    ];
    
    let currentWordIndex = 0;
    
    function typeWord(word, callback) {
        let currentLength = 0;
        animatedText.textContent = '';
        
        const typeInterval = setInterval(() => {
            animatedText.textContent = word.substring(0, currentLength + 1);
            currentLength++;
            
            if (currentLength === word.length) {
                clearInterval(typeInterval);
                setTimeout(callback, 2000); // Wait 2 seconds before erasing
            }
        }, 100); // Type speed
    }
    
    function eraseWord(callback) {
        const currentWord = animatedText.textContent;
        let currentLength = currentWord.length;
        
        const eraseInterval = setInterval(() => {
            animatedText.textContent = currentWord.substring(0, currentLength - 1);
            currentLength--;
            
            if (currentLength === 0) {
                clearInterval(eraseInterval);
                setTimeout(callback, 500); // Wait before typing next word
            }
        }, 50); // Erase speed
    }
    
    function animateText() {
        typeWord(words[currentWordIndex], () => {
            eraseWord(() => {
                currentWordIndex = (currentWordIndex + 1) % words.length;
                animateText();
            });
        });
    }
    
    // Start text animation after initial load
    setTimeout(() => {
        animateText();
    }, 1500);

    // Character counter functionality
    function updateCharacterCounter() {
        const count = searchInput.value.length;
        charCount.textContent = count;
        
        if (count >= 90) {
            characterCounter.style.color = '#ef4444';
        } else if (count >= 80) {
            characterCounter.style.color = '#f59e0b';
        } else {
            characterCounter.style.color = 'var(--text-muted)';
        }
    }

    // Auto-resize textarea
    function autoResize() {
        const maxHeight = 120;
        searchInput.style.height = 'auto';
        const newHeight = Math.min(searchInput.scrollHeight, maxHeight);
        searchInput.style.height = newHeight + 'px';
    }

    // Update tags display based on required fields
    function updateTagsDisplay() {
        const currentTagsDisplay = document.getElementById('tagsDisplay');
        if (!currentTagsDisplay) {
            console.log('tagsDisplay element not found - skipping update');
            return;
        }
        
        const tags = currentTagsDisplay.querySelectorAll('.tag');
        console.log('=== UPDATING TAGS DISPLAY ===');
        console.log('Current required fields:', requiredFields);
        console.log('Found tags:', tags.length);
        
        tags.forEach(tag => {
            const tagType = tag.dataset.type;
            const tagText = tag.querySelector('span').textContent;
            
            console.log(`\nProcessing tag: "${tagText}" (type: ${tagType})`);
            console.log('Tag classes before update:', tag.className);
            
            if (requiredFields.includes(tagType)) {
                tag.classList.remove('optional');
                tag.classList.add('required');
                console.log(`→ REQUIRED: Added 'required' class`);
            } else {
                tag.classList.remove('required');
                tag.classList.add('optional');
                console.log(`→ OPTIONAL: Added 'optional' class`);
            }
            
            console.log('Tag classes after update:', tag.className);
            
            // Check computed styles
            const computedStyle = window.getComputedStyle(tag);
            console.log('Computed border:', computedStyle.border);
            console.log('Computed border-style:', computedStyle.borderStyle);
        });
        
        console.log('=== END TAGS DISPLAY UPDATE ===');
    }

    // Add tag functionality
    function addTag(type, value, color) {
        const currentTagsDisplay = document.getElementById('tagsDisplay');
        const currentTagDropdown = document.getElementById('tagDropdown');
        
        if (!currentTagsDisplay) {
            console.log('tagsDisplay element not found - cannot add tag');
            return;
        }
        
        if (activeTags.find(tag => tag.type === type && tag.value === value)) {
            return; // Tag already exists
        }

        const tag = document.createElement('div');
        tag.className = `tag ${type}`;
        tag.dataset.type = type;
        
        // Determine if required or optional
        const isRequired = requiredFields.includes(type);
        const statusClass = isRequired ? 'required' : 'optional';
        tag.classList.add(statusClass);
        
        console.log(`Adding tag: "${value}" (${type}) - Status: ${statusClass}`);
        console.log(`Tag classes: ${tag.className}`);
        
        tag.innerHTML = `
            <span>${value}</span>
            <button class="tag-remove" onclick="removeTag(this)">×</button>
        `;
        
        currentTagsDisplay.appendChild(tag);
        activeTags.push({ type, value, color });
        
        // Hide dropdown if it exists
        if (currentTagDropdown) {
            currentTagDropdown.classList.remove('show');
        }
    }

    // Remove tag functionality
    window.removeTag = function(button) {
        const tag = button.closest('.tag');
        const type = tag.dataset.type;
        const value = tag.querySelector('span').textContent;
        
        activeTags = activeTags.filter(t => !(t.type === type && t.value === value));
        tag.remove();
    };

    // Search functionality
    function performSearch() {
        const query = searchInput.value.trim();
        if (!query) return;

        // Hide suggestions
        if (suggestions) {
            suggestions.style.display = 'none';
        }

        // Show loading state
        resultsContainer.innerHTML = `
            <div class="loading-card">
                <div class="loading-spinner"></div>
                <p>Выполняется поиск...</p>
            </div>
        `;
        resultsSection.style.display = 'block';

        // Prepare search data
        const searchData = {
            query: query,
            tags: activeTags.reduce((acc, tag) => {
                if (!acc[tag.type]) acc[tag.type] = [];
                acc[tag.type].push(tag.value);
                return acc;
            }, {}),
            required_fields: requiredFields
        };

        // Perform search request
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(searchData)
        })
        .then(response => response.json())
        .then(data => {
            // Log the full response to console
            console.log('Search response:', data);
            
            // Log Mistral AI parsing results
            if (data.parsed) {
                console.log('Mistral AI parsed query:', data.parsed);
                
                if (data.parsed.requirements) {
                    console.log('Requirements analysis:', data.parsed.requirements);
                    
                    // Check if we have any tags to update
                    const currentTagsDisplay = document.getElementById('tagsDisplay');
                    if (currentTagsDisplay) {
                        const existingTags = currentTagsDisplay.querySelectorAll('.tag');
                        console.log('Existing tags before update:', existingTags.length);
                        console.log('tagsDisplay element:', currentTagsDisplay);
                        console.log('All tags found:', existingTags);
                        
                        // Log each tag details
                        existingTags.forEach((tag, index) => {
                            console.log(`Tag ${index}:`, {
                                element: tag,
                                type: tag.dataset.type,
                                text: tag.querySelector('span')?.textContent,
                                classes: tag.className
                            });
                        });
                        
                        if (existingTags.length > 0) {
                            console.log('Calling updateRequiredFieldsFromMistral...');
                            updateRequiredFieldsFromMistral(data.parsed.requirements);
                        } else {
                            console.log('No tags found - skipping tag update');
                        }
                    } else {
                        console.log('tagsDisplay element not found - skipping tag update');
                    }
                } else {
                    console.log('No requirements found in parsed data');
                }
            } else {
                console.log('No parsed data found');
            }
            
            displayResults(data);
        })
        .catch(error => {
            console.error('Search error:', error);
            resultsContainer.innerHTML = `
                <div class="error-card">
                    <p>Ошибка при выполнении поиска</p>
                </div>
            `;
        });
    }

    // Update required fields based on Mistral AI requirements
    function updateRequiredFieldsFromMistral(requirements) {
        console.log('=== MISTRAL REQUIREMENTS ANALYSIS ===');
        console.log('Raw requirements object:', requirements);
        
        requiredFields = [];
        
        // Map Russian field names to English
        const fieldMapping = {
            'навыки': 'skills',
            'курс': 'course', 
            'тип пользователя': 'user_type',
            'факультет': 'faculty',
            'номер группы': 'group'
        };
        
        console.log('Field mapping:', fieldMapping);
        
        // Check each field's requirement status
        for (const [russianField, englishField] of Object.entries(fieldMapping)) {
            const status = requirements[russianField];
            console.log(`Field "${russianField}" (${englishField}): ${status}`);
            
            if (status === 'required') {
                requiredFields.push(englishField);
                console.log(`→ Added "${englishField}" to required fields`);
            } else if (status === 'optional') {
                console.log(`→ Field "${englishField}" is OPTIONAL (should be dashed)`);
            } else {
                console.log(`→ Field "${englishField}" is ${status || 'null'}`);
            }
        }
        
        console.log('Final required fields array:', requiredFields);
        console.log('=== END REQUIREMENTS ANALYSIS ===');
        
        // Update existing tags display
        updateTagsDisplay();
    }

    // Remove the old analyzeQueryContext function and update input handler
    searchInput.addEventListener('input', function() {
        updateCharacterCounter();
        autoResize();
        
        // Character limit
        if (this.value.length > 100) {
            this.value = this.value.substring(0, 100);
            updateCharacterCounter();
        }
    });

    function displayResults(data) {
        if (data.results && data.results.length > 0) {
            // Display actual results
            resultsContainer.innerHTML = data.results.map(result => `
                <div class="result-card">
                    <h3>${result.title}</h3>
                    <p>${result.description}</p>
                    <a href="${result.url}" target="_blank">Подробнее</a>
                </div>
            `).join('');
        } else {
            // No results found
            resultsContainer.innerHTML = `
                <div class="no-results-card">
                    <div class="no-results-icon">○</div>
                    <h3>Результаты не найдены</h3>
                    <p>По запросу "${data.query}" ничего не найдено</p>
                    <div class="suggestions-list">
                        <p>Рекомендации:</p>
                        <ul>
                            <li>Проверьте правильность написания</li>
                            <li>Используйте более общие термины</li>
                            <li>Попробуйте альтернативные формулировки</li>
                        </ul>
                    </div>
                </div>
            `;
        }
    }

    // Event listeners
    searchBtn.addEventListener('click', performSearch);
    
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            performSearch();
        }
    });

    searchInput.addEventListener('paste', function(e) {
        setTimeout(() => {
            if (this.value.length > 100) {
                this.value = this.value.substring(0, 100);
                updateCharacterCounter();
            }
        }, 0);
    });

    // Tags dropdown functionality
    addTagBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        tagDropdown.classList.toggle('show');
    });

    // Tag dropdown item clicks
    tagDropdown.addEventListener('click', function(e) {
        const item = e.target.closest('.tag-dropdown-item');
        if (item) {
            const type = item.dataset.type;
            const color = item.dataset.color;
            const text = item.textContent.trim();
            
            // For now, add with default value - in real app this would open input
            const value = prompt(`Введите значение для "${text}":`, '');
            if (value && value.trim()) {
                addTag(type, value.trim(), color);
            }
        }
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.add-tag-section')) {
            tagDropdown.classList.remove('show');
        }
    });

    // Show/hide suggestions
    if (suggestions) {
        searchInput.addEventListener('focus', function() {
            if (searchInput.value.length > 0) {
                suggestions.style.display = 'block';
            }
        });

        searchInput.addEventListener('input', function() {
            if (this.value.length > 0) {
                suggestions.style.display = 'block';
            } else {
                suggestions.style.display = 'none';
            }
        });

        // Hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.search-card')) {
                suggestions.style.display = 'none';
            }
        });

        // Suggestion item clicks
        document.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', function() {
                searchInput.value = this.textContent;
                suggestions.style.display = 'none';
                performSearch();
            });
        });
    }

    // Add loading and result card styles dynamically
    const style = document.createElement('style');
    style.textContent = `
        .loading-card, .error-card, .no-results-card, .result-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 24px;
            box-shadow: var(--shadow);
            animation: fadeInUp 0.3s ease;
        }

        .loading-card {
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 16px;
        }

        .loading-spinner {
            width: 24px;
            height: 24px;
            border: 2px solid var(--border);
            border-top: 2px solid var(--text-secondary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .error-card {
            text-align: center;
            color: var(--text-secondary);
        }

        .no-results-card {
            text-align: center;
            color: var(--text-secondary);
        }

        .no-results-icon {
            font-size: 2rem;
            margin-bottom: 16px;
            color: var(--text-muted);
        }

        .no-results-card h3 {
            color: var(--text-primary);
            margin-bottom: 8px;
            font-weight: 500;
        }

        .suggestions-list {
            margin-top: 24px;
            text-align: left;
        }

        .suggestions-list ul {
            margin-top: 8px;
            padding-left: 20px;
        }

        .suggestions-list li {
            margin-bottom: 4px;
            font-size: 0.9rem;
        }

        .result-card {
            transition: all 0.2s ease;
        }

        .result-card:hover {
            border-color: var(--border-hover);
        }

        .result-card h3 {
            color: var(--text-primary);
            margin-bottom: 12px;
            font-size: 1.125rem;
            font-weight: 500;
        }

        .result-card p {
            color: var(--text-secondary);
            margin-bottom: 16px;
            line-height: 1.5;
            font-size: 0.95rem;
        }

        .result-card a {
            color: var(--accent);
            text-decoration: none;
            font-weight: 400;
            font-size: 0.9rem;
            transition: color 0.2s ease;
        }

        .result-card a:hover {
            color: var(--accent-hover);
        }
    `;
    document.head.appendChild(style);
}); 