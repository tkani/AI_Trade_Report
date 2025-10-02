// Language translations
const translations = {
    en: {
        brand_name: "AI Trade Report",
        features: "Features",
        pricing: "Pricing",
        support: "Support",
        powered_by: "Powered by GPT-5",
        hero_title: "Professional Market Analysis",
        hero_subtitle: "in Minutes",
        hero_description: "Generate comprehensive trade reports with AI-powered insights, competitive analysis, and strategic recommendations for your business expansion.",
        form_title: "Create Your Market Analysis",
        form_subtitle: "Enter your business details to generate a professional report",
        brand_label: "Brand Name",
        product_label: "Product/Service",
        product_placeholder: "Search and select your product or service",
        product_info: "Select your products or services for market analysis",
        other_info_label: "Other Information",
        other_info_placeholder: "Enter any special questions or additional information you'd like the AI to consider in the analysis...",
        budget_label: "Investment Budget",
        ai_model_label: "AI Model",
        ai_model_info: "Advanced AI with latest market data and insights",
        generate_button: "Generate Report",
        loading_title: "Generating Your Report",
        loading_description: "Our AI is analyzing market data, competitive landscape, and strategic opportunities for your business expansion.",
        step_1: "🔍 Market Research",
        step_2: "📊 Data Analysis",
        step_3: "📝 Report Generation",
        saved_reports_nav: "Saved Reports",
        profile_nav: "Profile",
        logout_nav: "Logout"
    },
    it: {
        brand_name: "AI Trade Report",
        features: "Caratteristiche",
        pricing: "Prezzi",
        support: "Supporto",
        powered_by: "Alimentato da GPT-5",
        hero_title: "Analisi di Mercato Professionale",
        hero_subtitle: "in Minuti",
        hero_description: "Genera report commerciali completi con insights basati su AI, analisi competitiva e raccomandazioni strategiche per l'espansione della tua azienda.",
        form_title: "Crea la Tua Analisi di Mercato",
        form_subtitle: "Inserisci i dettagli della tua azienda per generare un report professionale",
        brand_label: "Nome del Brand",
        product_label: "Prodotto/Servizio",
        product_placeholder: "Cerca e seleziona il tuo prodotto o servizio",
        product_info: "Seleziona i tuoi prodotti o servizi per l'analisi di mercato",
        other_info_label: "Altre Informazioni",
        other_info_placeholder: "Inserisci eventuali domande specifiche o informazioni aggiuntive che vorresti che l'AI consideri nell'analisi...",
        budget_label: "Budget di Investimento",
        ai_model_label: "Modello AI",
        ai_model_info: "AI avanzata con i dati di mercato e insights più recenti",
        generate_button: "Genera Report",
        loading_title: "Generazione del Tuo Report",
        loading_description: "La nostra AI sta analizzando i dati di mercato, il panorama competitivo e le opportunità strategiche per l'espansione della tua azienda.",
        step_1: "🔍 Ricerca di Mercato",
        step_2: "📊 Analisi dei Dati",
        step_3: "📝 Generazione Report",
        saved_reports_nav: "Report Salvati",
        profile_nav: "Profilo",
        logout_nav: "Esci"
    }
};

// Current language
let currentLanguage = 'en';

$(document).ready(function () {
    // Always show language selection modal on page load
    $('#language-modal').removeClass('hidden');

    // Language selection handlers
    $('.language-btn').click(function() {
        const selectedLang = $(this).data('lang');
        currentLanguage = selectedLang;
        $('#language-input').val(currentLanguage);
        
        // Translate page
        translatePage(currentLanguage);
        
        // Hide modal with animation
        $('#language-modal').addClass('hidden');
        
        // Update HTML lang attribute
        $('#html-lang').attr('lang', currentLanguage);
    });

    // Enhanced form submission with loading steps
    $('#report-form').submit(function (e) {
        e.preventDefault(); // Prevent default form submission
        
        // Show splash screen
        $('#splash-screen').css('display', 'flex');
        
        // Animate loading steps
        animateLoadingSteps();

        // Get form data
        var formData = $(this).serialize();
        var selectedModel = $('#ai_model').val();
        
        // Handle multiple product selections
        var selectedProducts = $('#product-select').val();
        if (selectedProducts && selectedProducts.length > 0) {
            // Convert array to comma-separated string for backend processing
            formData = formData.replace(/product=[^&]*/, 'product=' + encodeURIComponent(selectedProducts.join(', ')));
        }
        
        // Debug: Log the AI model value
        console.log('AI Model value:', selectedModel);
        
        // Ensure we have a valid model
        if (!selectedModel || selectedModel === 'undefined') {
            selectedModel = 'gpt-5';
            $('#ai_model').val('gpt-5');
            console.log('AI Model corrected to:', selectedModel);
        }
        
        // Add the AI model selection to form data
        formData += '&ai_model=' + encodeURIComponent(selectedModel);

        // Set a timeout for the request (increased to 15 minutes)
        const requestTimeout = setTimeout(function() {
            $('#splash-screen').css('display', 'none');
            alert('Report generation is taking longer than expected. This can happen with complex reports. Please try again or contact support if the issue persists.');
        }, 900000); // 15 minutes timeout

        // Show progress updates
        let progressCounter = 0;
        const progressInterval = setInterval(function() {
            progressCounter += 2; // Slower progress to be more realistic
            if (progressCounter <= 85) { // Stop at 85% to avoid showing 100% before completion
                console.log('Generating report... ' + progressCounter + '%');
                // Update loading description with more specific messages
                const messages = [
                    'Our AI is analyzing market data, competitive landscape, and strategic opportunities for your business expansion.',
                    'Processing market research data and generating insights...',
                    'Analyzing competitive landscape and market trends...',
                    'Generating strategic recommendations and implementation plan...',
                    'Finalizing report structure and formatting...',
                    'Almost done! Preparing your comprehensive market analysis...'
                ];
                const messageIndex = Math.min(Math.floor(progressCounter / 15), messages.length - 1);
                $('.loading-description').text(messages[messageIndex]);
            }
        }, 20000); // Update every 20 seconds for more realistic progress

        // Submit form data via AJAX with retry mechanism
        function submitReport(retryCount = 0) {
            $.ajax({
                url: '/generate',
                type: 'POST',
                data: formData,
                timeout: 900000, // 15 minutes timeout
                success: function (response, status, xhr) {
                    clearTimeout(requestTimeout);
                    clearInterval(progressInterval);
                    
                    // Complete all steps
                    completeAllSteps();
                    
                    // Check if we got a successful response
                    if (response.status === 'success') {
                        // Small delay before redirect for better UX
                        setTimeout(function() {
                            $('#splash-screen').css('display', 'none');
                            window.location.href = response.redirect_url;
                        }, 1000);
                    } else {
                        // If no success, hide splash screen and show error
                        setTimeout(function() {
                            $('#splash-screen').css('display', 'none');
                            alert('Error: ' + (response.message || 'Unknown error occurred'));
                        }, 1000);
                    }
                },
                error: function (xhr, status, error) {
                    clearTimeout(requestTimeout);
                    clearInterval(progressInterval);
                    
                    console.error('Report generation error:', {xhr, status, error, retryCount});
                    
                    // Retry logic for certain errors
                    if (retryCount < 2 && (status === 'timeout' || xhr.status === 500 || xhr.status === 0)) {
                        console.log(`Retrying report generation (attempt ${retryCount + 1}/3)...`);
                        $('#splash-screen .loading-description').text(`Retrying report generation (attempt ${retryCount + 1}/3)...`);
                        setTimeout(() => {
                            submitReport(retryCount + 1);
                        }, 5000); // Wait 5 seconds before retry
                        return;
                    }
                    
                    $('#splash-screen').css('display', 'none');
                    
                    if (status === 'timeout') {
                        alert('Report generation is taking longer than expected. This can happen with complex reports. Please try again in a few minutes.');
                    } else if (xhr.status === 401) {
                        // Authentication required - redirect to login
                        alert('You need to log in to generate reports. Redirecting to login page...');
                        window.location.href = '/login';
                    } else if (xhr.status === 500) {
                        // Server error
                        alert('Server error occurred. Please try again in a few minutes. If the problem persists, contact support.');
                    } else if (xhr.status === 0) {
                        // Network error
                        alert('Network error. Please check your internet connection and try again.');
                    } else {
                        // Try to parse error response
                        let errorMessage = 'Unknown error occurred';
                        try {
                            const response = JSON.parse(xhr.responseText);
                            if (response.message) {
                                errorMessage = response.message;
                            }
                        } catch (e) {
                            // If parsing fails, use a generic message
                            errorMessage = `Server returned status ${xhr.status}. Please try again.`;
                        }
                        alert('An error occurred while generating the report: ' + errorMessage);
                    }
                }
            });
        }
        
        // Start the report generation
        submitReport();
    });
    
    // Loading steps animation
    function animateLoadingSteps() {
        const steps = $('.step');
        let currentStep = 0;
        
        const stepInterval = setInterval(function() {
            if (currentStep < steps.length) {
                // Mark previous step as completed
                if (currentStep > 0) {
                    steps.eq(currentStep - 1).removeClass('active').addClass('completed');
                }
                
                // Activate current step
                steps.eq(currentStep).addClass('active');
                currentStep++;
            } else {
                clearInterval(stepInterval);
            }
        }, 2000);
    }
    
    // Complete all steps
    function completeAllSteps() {
        $('.step').removeClass('active').addClass('completed');
    }
    
    // Enhanced form interactions
    $('.form-input, .form-select').on('focus', function() {
        $(this).parent().addClass('focused');
    }).on('blur', function() {
        $(this).parent().removeClass('focused');
    });
    
    // Form validation feedback
    $('.form-input').on('input', function() {
        if ($(this).val().length > 0) {
            $(this).addClass('has-value');
        } else {
            $(this).removeClass('has-value');
        }
    });
    
        // Saved Reports Modal Toggle
        $('#toggle-saved-reports').click(function() {
            console.log('Toggle saved reports clicked');
            showSavedReportsModal();
        });

        // Bootstrap modal event handlers
        $('#savedReportsModal').on('show.bs.modal', function () {
            console.log('Bootstrap modal is about to show');
            // Check authentication when modal is about to show
            fetch('/debug/auth')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'authenticated') {
                        console.log('User is authenticated, loading reports');
                        loadSavedReportsModal();
                    } else {
                        console.log('User not authenticated, showing auth message');
                        showAuthRequiredMessage();
                    }
                })
                .catch(error => {
                    console.error('Error checking authentication:', error);
                    showAuthRequiredMessage();
                });
        });

        $('#savedReportsModal').on('hidden.bs.modal', function () {
            console.log('Bootstrap modal is hidden');
            // Reset modal state when hidden
            $('#reports-table-body').empty();
            $('#no-reports-message').hide();
            $('#auth-required-message').hide();
            $('#loading-reports').hide();
            $('#pagination-container').hide();
        });
    
    // Auto-load saved reports if section is visible on page load
    if ($('#saved-reports-section').is(':visible')) {
        loadSavedReports();
    }
});

// Function to poll job status
function pollJobStatus(jobId) {
    const pollInterval = setInterval(function() {
        $.ajax({
            url: `/job-status/${jobId}`,
            type: 'GET',
            success: function(status) {
                console.log('Job status:', status);
                
                if (status.status === 'completed') {
                    clearInterval(pollInterval);
                    // Complete all steps
                    completeAllSteps();
                    
                    // Small delay before redirect for better UX
                    setTimeout(function() {
                        $('#splash-screen').css('display', 'none');
                        window.location.href = status.redirect_url;
                    }, 1000);
                } else if (status.status === 'error') {
                    clearInterval(pollInterval);
                    $('#splash-screen').css('display', 'none');
                    alert('Error generating report: ' + status.error);
                } else if (status.status === 'processing') {
                    // Update progress if needed
                    console.log('Progress:', status.progress + '%');
                }
            },
            error: function() {
                clearInterval(pollInterval);
                $('#splash-screen').css('display', 'none');
                alert('Error checking report status.');
            }
        });
    }, 2000); // Poll every 2 seconds
}

// Translation function
function translatePage(language) {
    const lang = translations[language];
    if (!lang) return;
    
    // Translate all elements with data-translate attribute
    $('[data-translate]').each(function() {
        const key = $(this).data('translate');
        if (lang[key]) {
            $(this).text(lang[key]);
        }
    });
    
    // Translate placeholders
    $('[data-placeholder-en], [data-placeholder-it]').each(function() {
        const placeholderKey = language === 'it' ? 'data-placeholder-it' : 'data-placeholder-en';
        const placeholder = $(this).attr(placeholderKey);
        if (placeholder) {
            $(this).attr('placeholder', placeholder);
        }
    });
    
    // Translate select options
    $('option[data-text-en], option[data-text-it]').each(function() {
        const textKey = language === 'it' ? 'data-text-it' : 'data-text-en';
        const text = $(this).attr(textKey);
        if (text) {
            $(this).text(text);
        }
    });
    
    // Update page title
    if (language === 'it') {
        document.title = 'AI Trade Report - Analisi di Mercato Professionale';
    } else {
        document.title = 'AI Trade Report - Professional Market Analysis';
    }
}

// Select2 Product Input Functionality
function initializeSelect2Input() {
    const productSelect = document.getElementById('product-select');
    if (!productSelect) {
        console.log('Product select element not found');
        return;
    }
    
    console.log('Initializing Select2 for product select');
    
    // Get current language
    const currentLang = document.getElementById('html-lang').lang || 'en';
    const placeholder = translations[currentLang]?.product_placeholder || 'Search and select your products or services';
    
    // Check if Select2 is available
    if (typeof $.fn.select2 === 'undefined') {
        console.error('Select2 is not loaded');
        return;
    }
    
    // Initialize Select2
    try {
        $(productSelect).select2({
        ajax: {
            url: '/api/select2-terms',
            dataType: 'json',
            delay: 300,
            data: function (params) {
                return {
                    q: params.term,
                    page: params.page || 1,
                    per_page: 20
                };
            },
            processResults: function (data, params) {
                params.page = params.page || 1;
                
                return {
                    results: data.results.map(function(item) {
                        return {
                            id: item.id,
                            text: item.text,
                            description: item.description,
                            category: item.category
                        };
                    }),
                    pagination: {
                        more: data.pagination.more
                    }
                };
            },
            cache: true
        },
        placeholder: placeholder,
        allowClear: true,
        multiple: true, // Enable multiple selections
        minimumInputLength: 2,
        tags: true, // Enable custom entries
        tokenSeparators: [',', ';'], // Allow comma and semicolon as separators
        createTag: function (params) {
            // Allow creation of custom tags
            var term = $.trim(params.term);
            if (term === '') {
                return null;
            }
            return {
                id: term,
                text: term,
                isCustom: true // Mark as custom entry
            };
        },
        templateResult: formatProductOption,
        templateSelection: formatProductSelection,
        escapeMarkup: function (markup) { return markup; },
        language: {
            inputTooShort: function () {
                return 'Please enter at least 2 characters';
            },
            noResults: function () {
                return 'No products found. Press Enter to add custom entry.';
            },
            searching: function () {
                return 'Searching...';
            }
        }
    });
    
    console.log('Select2 initialized successfully');
    
    // Ensure proper width after initialization
    setTimeout(function() {
        const container = $(productSelect).next('.select2-container');
        const searchField = container.find('.select2-search__field');
        const searchInline = container.find('.select2-search--inline');
        
        // Force width on all elements
        container.css({
            'width': '100%',
            'max-width': '100%'
        });
        
        if (searchInline.length) {
            searchInline.css({
                'width': '100%',
                'min-width': '300px',
                'flex': '1 1 auto'
            });
        }
        
        if (searchField.length) {
            searchField.css({
                'width': '100%',
                'min-width': '300px',
                'max-width': 'none',
                'flex': '1 1 auto',
                'box-sizing': 'border-box'
            });
        }
        
        // Also force width on the selection area
        const selection = container.find('.select2-selection--multiple');
        if (selection.length) {
            selection.css({
                'width': '100%',
                'max-width': '100%',
                'display': 'flex',
                'flex-wrap': 'wrap'
            });
        }
    }, 100);
    
    // Additional width fix after a longer delay
    setTimeout(function() {
        const searchField = $(productSelect).next('.select2-container').find('.select2-search__field');
        const searchInline = $(productSelect).next('.select2-container').find('.select2-search--inline');
        
        if (searchField.length) {
            searchField.attr('style', searchField.attr('style') + '; width: 100% !important; min-width: 200px !important; max-width: none !important; overflow: visible !important; white-space: nowrap !important;');
        }
        
        if (searchInline.length) {
            searchInline.attr('style', searchInline.attr('style') + '; flex: 1 1 200px !important; min-width: 200px !important; order: 999 !important; margin-left: 4px !important;');
        }
    }, 500);
    
    // Monitor for changes and reapply width fixes
    $(productSelect).on('select2:select select2:unselect', function() {
        setTimeout(function() {
            forceSelect2Width();
            // Also fix tag overflow
            fixTagOverflow();
        }, 100);
    });
    
    // Function to fix tag overflow
    function fixTagOverflow() {
        const choices = $(productSelect).next('.select2-container').find('.select2-selection__choice');
        choices.each(function() {
            const $choice = $(this);
            const $display = $choice.find('.select2-selection__choice__display');
            
            // Ensure proper width constraints
            $choice.css({
                'max-width': '300px',
                'overflow': 'hidden',
                'text-overflow': 'ellipsis',
                'white-space': 'nowrap',
                'flex': '0 0 auto'
            });
            
            if ($display.length) {
                $display.css({
                    'max-width': '250px',
                    'overflow': 'hidden',
                    'text-overflow': 'ellipsis',
                    'white-space': 'nowrap',
                    'display': 'inline-block'
                });
            }
        });
    }
    
    // Make fixTagOverflow available globally
    window.fixTagOverflow = fixTagOverflow;
    
    // Update placeholder when language changes
    $(document).on('languageChanged', function() {
        const newLang = document.getElementById('html-lang').lang || 'en';
        const newPlaceholder = translations[newLang]?.product_placeholder || 'Search and select your products or services';
        $(productSelect).select2('destroy');
        $(productSelect).attr('data-placeholder', newPlaceholder);
        initializeSelect2Input();
    });
    
    } catch (error) {
        console.error('Error initializing Select2:', error);
        // Fallback: show a regular input
        fallbackToRegularInput();
    }
}

function fallbackToRegularInput() {
    console.log('Falling back to regular input');
    const productSelect = document.getElementById('product-select');
    if (!productSelect) return;
    
    // Create a regular input field
    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'product';
    input.id = 'product-input-fallback';
    input.className = 'form-input';
    input.placeholder = 'Enter your product or service';
    input.required = true;
    
    // Replace the select with input
    productSelect.parentNode.replaceChild(input, productSelect);
    
    // Initialize the old searchable functionality
    initializeSearchableInputFallback();
}

function initializeSearchableInputFallback() {
    const productInput = document.getElementById('product-input-fallback');
    if (!productInput) return;
    
    let searchTimeout;
    
    productInput.addEventListener('input', function(e) {
        const query = e.target.value.trim();
        
        clearTimeout(searchTimeout);
        
        if (query.length < 2) {
            return;
        }
        
        searchTimeout = setTimeout(() => {
            searchTermsFallback(query);
        }, 300);
    });
}

function searchTermsFallback(query) {
    fetch(`/api/search-terms?q=${encodeURIComponent(query)}&limit=5`)
        .then(response => response.json())
        .then(data => {
            console.log('Search results:', data.terms);
            // You could implement a simple dropdown here if needed
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

function formatProductOption(product) {
    if (product.loading) {
        return product.text;
    }
    
    // Check if this is a custom entry
    if (product.isCustom) {
        const $container = $(
            '<div class="select2-result-text">' +
                '<div class="select2-result-term">' + product.text + '</div>' +
                '<div class="select2-result-description">Custom entry - Press Enter to add</div>' +
                '<div class="select2-result-category">CUSTOM</div>' +
            '</div>'
        );
        return $container;
    }
    
    const $container = $(
        '<div class="select2-result-text">' +
            '<div class="select2-result-term">' + product.text + '</div>' +
            '<div class="select2-result-description">' + (product.description || '') + '</div>' +
            (product.category ? '<div class="select2-result-category">' + product.category + '</div>' : '') +
        '</div>'
    );
    
    return $container;
}

function formatProductSelection(product) {
    return product.text;
}

// Initialize Select2 when DOM is ready
$(document).ready(function() {
    console.log('DOM ready, initializing Select2...');
    initializeSelect2Input();
});

// Also try to initialize after window load
$(window).on('load', function() {
    console.log('Window loaded, checking Select2...');
    setTimeout(function() {
        // Check if Select2 is already initialized
        if ($('#product-select').hasClass('select2-hidden-accessible')) {
            console.log('Select2 already initialized');
            // Force width even if already initialized
            forceSelect2Width();
            return;
        }
        console.log('Trying to initialize Select2 after window load');
        initializeSelect2Input();
    }, 500);
});

// Function to force Select2 width
function forceSelect2Width() {
    console.log('Forcing Select2 width...');
    const container = $('#product-select').next('.select2-container');
    const searchField = container.find('.select2-search__field');
    const searchInline = container.find('.select2-search--inline');
    const selection = container.find('.select2-selection--multiple');
    
    // Apply aggressive width fixes
    container.css({
        'width': '100% !important',
        'max-width': '100% !important',
        'min-width': '100% !important'
    });
    
    if (searchInline.length) {
        searchInline.css({
            'width': '100% !important',
            'min-width': '300px !important',
            'flex': '1 1 auto !important'
        });
    }
    
    if (searchField.length) {
        searchField.css({
            'width': '100% !important',
            'min-width': '200px !important',
            'max-width': 'none !important',
            'flex': '1 1 auto !important',
            'overflow': 'visible !important',
            'white-space': 'nowrap !important',
            'text-overflow': 'ellipsis !important'
        });
    }
    
    if (selection.length) {
        selection.css({
            'width': '100% !important',
            'max-width': '100% !important',
            'display': 'flex !important',
            'flex-wrap': 'wrap !important'
        });
    }
    
    console.log('Select2 width forced');
    
    // Also fix tag overflow
    fixTagOverflow();
}

// Function to fix tag overflow
function fixTagOverflow() {
    const choices = $('#product-select').next('.select2-container').find('.select2-selection__choice');
    choices.each(function() {
        const $choice = $(this);
        const $display = $choice.find('.select2-selection__choice__display');
        
        // Ensure proper width constraints
        $choice.css({
            'max-width': '300px',
            'overflow': 'hidden',
            'text-overflow': 'ellipsis',
            'white-space': 'nowrap',
            'flex': '0 0 auto'
        });
        
        if ($display.length) {
            $display.css({
                'max-width': '250px',
                'overflow': 'hidden',
                'text-overflow': 'ellipsis',
                'white-space': 'nowrap',
                'display': 'inline-block'
            });
        }
    });
}

// Make forceSelect2Width available globally for debugging
window.forceSelect2Width = forceSelect2Width;

// Modal Functions
function showSavedReportsModal() {
    console.log('Showing saved reports modal');
    // Use Bootstrap modal API
    const modal = new bootstrap.Modal(document.getElementById('savedReportsModal'));
    modal.show();
}

function showAuthRequiredMessage() {
    $('#loading-reports').hide();
    $('#no-reports-message').hide();
    $('#auth-required-message').show();
    $('#reports-table-body').empty();
    $('#pagination-container').hide();
}

// Saved Reports Functionality - Global functions
function loadSavedReportsModal() {
    console.log('Loading saved reports for modal...');
    
    // Show loading state
    $('#loading-reports').show();
    $('#no-reports-message').hide();
    $('#auth-required-message').hide();
    $('#reports-table-body').empty();
    $('#pagination-container').hide();
    
    // Fetch saved reports
    fetch('/my-reports')
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                if (response.status === 401) {
                    throw new Error('Authentication required. Please log in to view saved reports.');
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Received data:', data);
            $('#loading-reports').hide();
            
            if (data.status === 'success' && data.reports && data.reports.length > 0) {
                console.log('Displaying', data.reports.length, 'reports in table');
                displaySavedReportsTable(data.reports);
                $('#no-reports-message').hide();
                $('#auth-required-message').hide();
            } else {
                console.log('No reports found or empty response');
                $('#no-reports-message').show();
                $('#auth-required-message').hide();
                $('#reports-table-body').empty();
                $('#pagination-container').hide();
            }
        })
        .catch(error => {
            console.error('Error loading saved reports:', error);
            $('#loading-reports').hide();
            
            if (error.message.includes('Authentication required')) {
                showAuthRequiredMessage();
            } else {
                $('#reports-table-body').html('<tr><td colspan="5" class="error-message" style="text-align: center; padding: 2rem; color: #dc2626;">Error loading reports. Please try again.</td></tr>');
            }
        });
}

// Display saved reports in table format
function displaySavedReportsTable(reports) {
    const tableBody = $('#reports-table-body');
    if (!tableBody.length) {
        console.warn('Reports table body element not found');
        return;
    }
    
    tableBody.empty();
    
    reports.forEach(report => {
        const tableRow = createReportTableRow(report);
        tableBody.append(tableRow);
    });
    
    // Initialize table features
    initializeTableFeatures();
}

// Display saved reports (legacy function for compatibility)
function displaySavedReports(reports) {
    const reportsList = $('#saved-reports-list');
    if (!reportsList.length) {
        console.warn('Saved reports list element not found');
        return;
    }
    
    reportsList.empty();
    
    reports.forEach(report => {
        const reportItem = createReportItem(report);
        reportsList.append(reportItem);
    });
}

// Create report table row HTML
function createReportTableRow(report) {
    if (!report || !report.id) {
        console.warn('Invalid report data:', report);
        return $('<tr><td colspan="5" class="text-center text-danger">Invalid report data</td></tr>');
    }
    
    const createdDate = new Date(report.created_at).toLocaleDateString();
    const createdTime = new Date(report.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    return $(`
        <tr data-report-id="${report.id}">
            <td>
                <span class="badge bg-primary">${escapeHtml(report.brand || 'N/A')}</span>
            </td>
            <td>
                <span class="fw-medium">${escapeHtml(report.product || 'N/A')}</span>
            </td>
            <td>
                <span class="badge bg-info">${escapeHtml(report.enterprise_size || 'N/A')}</span>
            </td>
            <td>
                <div class="small">${createdDate}</div>
                <div class="small text-muted">${createdTime}</div>
            </td>
            <td>
                <div class="btn-group" role="group">
                    <a href="/report/${report.file_path || ''}" class="btn btn-sm btn-outline-primary" title="View Report">
                        <i class="bi bi-eye"></i>
                    </a>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteReport(${report.id})" title="Delete Report">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `);
}

// Create report item HTML (legacy function for compatibility)
function createReportItem(report) {
    if (!report || !report.id) {
        console.warn('Invalid report data:', report);
        return $('<div>Invalid report data</div>');
    }
    
    const createdDate = new Date(report.created_at).toLocaleDateString();
    const createdTime = new Date(report.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    return $(`
        <div class="saved-report-item" data-report-id="${report.id}">
            <div class="report-item-header">
                <h3 class="report-item-title">${escapeHtml(report.title || 'Untitled Report')}</h3>
                <div class="report-item-date">${createdDate} ${createdTime}</div>
            </div>
            <div class="report-item-details">
                <div class="report-detail-row">
                    <span class="report-detail-label">Brand:</span>
                    <span class="report-detail-value">${escapeHtml(report.brand || 'N/A')}</span>
                </div>
                <div class="report-detail-row">
                    <span class="report-detail-label">Product:</span>
                    <span class="report-detail-value">${escapeHtml(report.product || 'N/A')}</span>
                </div>
                <div class="report-detail-row">
                    <span class="report-detail-label">Budget:</span>
                    <span class="report-detail-value">${escapeHtml(report.budget || 'N/A')}</span>
                </div>
                <div class="report-detail-row">
                    <span class="report-detail-label">Size:</span>
                    <span class="report-detail-value">${escapeHtml(report.enterprise_size || 'N/A')}</span>
                </div>
            </div>
            <div class="report-item-actions">
                <a href="/report/${report.file_path || ''}" class="report-action-btn primary">
                    <span>👁️</span>
                    <span>View Report</span>
                </a>
                <button class="report-action-btn secondary" onclick="deleteReport(${report.id})">
                    <span>🗑️</span>
                    <span>Delete</span>
                </button>
            </div>
        </div>
    `);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    if (typeof text !== 'string') {
        return '';
    }
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

// Table Features
function initializeTableFeatures() {
    // Initialize sorting only
    initializeTableSorting();
}

// Table Sorting
function initializeTableSorting() {
    $('.reports-table th.sortable').click(function() {
        const column = $(this).data('sort');
        const currentSort = $(this).hasClass('asc') ? 'asc' : ($(this).hasClass('desc') ? 'desc' : 'none');
        
        // Reset all sort indicators
        $('.reports-table th.sortable').removeClass('asc desc');
        
        // Set new sort direction
        let newSort = 'asc';
        if (currentSort === 'asc') {
            newSort = 'desc';
        }
        
        $(this).addClass(newSort);
        
        // Sort the table
        sortTable(column, newSort);
    });
}

function sortTable(column, direction) {
    const tbody = $('#reports-table-body');
    const rows = tbody.find('tr').toArray();
    
    rows.sort((a, b) => {
        const aVal = $(a).find(`td:nth-child(${getColumnIndex(column)})`).text().trim();
        const bVal = $(b).find(`td:nth-child(${getColumnIndex(column)})`).text().trim();
        
        // Handle date sorting
        if (column === 'created_at') {
            const aDate = new Date($(a).find('td:nth-child(4) .small:first').text());
            const bDate = new Date($(b).find('td:nth-child(4) .small:first').text());
            return direction === 'asc' ? aDate - bDate : bDate - aDate;
        }
        
        // Handle text sorting
        const comparison = aVal.localeCompare(bVal, undefined, { numeric: true });
        return direction === 'asc' ? comparison : -comparison;
    });
    
    // Re-append sorted rows
    tbody.empty();
    rows.forEach(row => tbody.append(row));
}

function getColumnIndex(column) {
    const columnMap = {
        'brand': 1,
        'product': 2,
        'enterprise_size': 3,
        'created_at': 4
    };
    return columnMap[column] || 1;
}

// Removed search and filter functions as they are no longer needed

// Delete report function
window.deleteReport = function(reportId) {
    if (!reportId) {
        console.error('No report ID provided for deletion');
        return;
    }
    
    if (confirm('Are you sure you want to delete this report? This action cannot be undone.')) {
        fetch(`/delete-report/${reportId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                // Remove the report item from both table and list
                $(`tr[data-report-id="${reportId}"]`).fadeOut(300, function() {
                    $(this).remove();
                });
                $(`.saved-report-item[data-report-id="${reportId}"]`).fadeOut(300, function() {
                    $(this).remove();
                });
                
                // Check if no reports left
                if ($('#reports-table-body tr').length === 0 && $('#saved-reports-list .saved-report-item').length === 0) {
                    $('#no-reports-message').show();
                }
            } else {
                alert('Error deleting report: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error deleting report:', error);
            alert('Error deleting report. Please try again.');
        });
    }
};