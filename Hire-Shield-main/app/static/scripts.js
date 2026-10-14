// Example: Confirm before leaving review page with unsaved changes
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    if (!form) return;

    let isDirty = false;
    form.addEventListener('change', () => { isDirty = true; });

    window.addEventListener('beforeunload', function (e) {
        if (isDirty) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
});
