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
        budget_label: "Investment Budget",
        ai_model_label: "AI Model",
        ai_model_info: "Advanced AI with latest market data and insights",
        generate_button: "Generate Report",
        loading_title: "Generating Your Report",
        loading_description: "Our AI is analyzing market data, competitive landscape, and strategic opportunities for your business expansion.",
        step_1: "🔍 Market Research",
        step_2: "📊 Data Analysis",
        step_3: "📝 Report Generation"
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
        budget_label: "Budget di Investimento",
        ai_model_label: "Modello AI",
        ai_model_info: "AI avanzata con i dati di mercato e insights più recenti",
        generate_button: "Genera Report",
        loading_title: "Generazione del Tuo Report",
        loading_description: "La nostra AI sta analizzando i dati di mercato, il panorama competitivo e le opportunità strategiche per l'espansione della tua azienda.",
        step_1: "🔍 Ricerca di Mercato",
        step_2: "📊 Analisi dei Dati",
        step_3: "📝 Generazione Report"
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
        e.preventDefault();
        
        // Show splash screen
        $('#splash-screen').css('display', 'flex');
        
        // Animate loading steps
        animateLoadingSteps();

        var formData = $(this).serialize();
        var selectedModel = $('#ai_model').val();
        
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
        
        // Add selected products to form data
        const selectedProducts = $('#product-select').val();
        if (selectedProducts && selectedProducts.length > 0) {
            formData += '&product=' + encodeURIComponent(selectedProducts.join(', '));
        }

        $.ajax({
            url: '/generate',
            type: 'POST',
            data: formData,
            success: function (res) {
                // Complete all steps
                completeAllSteps();
                
                // Small delay before redirect for better UX
                setTimeout(function() {
                    $('#splash-screen').css('display', 'none');
                    
                    if (res.status === "success") {
                        // Redirect to the report page
                        window.location.href = res.redirect_url;
                    } else {
                        alert("Error: " + res.message);
                    }
                }, 1000);
            },
            error: function () {
                // Hide splash screen
                $('#splash-screen').css('display', 'none');
                alert("An error occurred while generating the report.");
            }
        });
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
});

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
        multiple: true,
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
