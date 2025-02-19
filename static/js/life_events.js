document.addEventListener('DOMContentLoaded', function() {
    // Get the textarea element
    const textarea = document.querySelector('.markdown-editor');

    // Initialize marked
    marked.setOptions({
        breaks: true,
        gfm: true
    });

    const easyMDE = new EasyMDE({
        element: textarea,
        spellChecker: false,
        autosave: {
            enabled: true,
            delay: 1000,
            uniqueId: 'life-event-editor'
        },
        renderingConfig: {
            singleLineBreaks: false
        },
        initialValue: textarea.value,
        forceSync: true,
        previewRender: function(plainText) {
            const preview = document.querySelector('.preview-container');
            preview.classList.remove('d-none');
            const content = document.getElementById('preview-content');
            content.innerHTML = marked.parse(plainText);
            return marked.parse(plainText);
        },
        toolbar: [
            'bold', 'italic', 'heading', '|',
            'quote', 'unordered-list', 'ordered-list', '|',
            'link', 'image', '|',
            'preview', 'side-by-side', 'fullscreen', '|',
            'guide'
        ]
    });

    // Remove required attribute from original textarea
    textarea.removeAttribute('required');

    // Form submission handling
    const form = document.querySelector('form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate form
        const title = document.getElementById('id_title').value.trim();
        const description = easyMDE.value().trim();
        
        if (!title || !description) {
            alert('Please fill in all required fields');
            return;
        }
        
        // Force sync before submission
        easyMDE.codemirror.save();
        
        // Submit the form normally (non-AJAX)
        form.submit();
    });
}); 