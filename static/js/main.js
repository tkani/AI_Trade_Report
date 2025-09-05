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
        
        // Add the AI model selection to form data
        formData += '&ai_model=' + encodeURIComponent(selectedModel);

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
