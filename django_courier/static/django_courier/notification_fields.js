function selectBackend() {
    var opt = this.options[this.selectedIndex];
    var use_subject = opt.dataset.subject == 'true';
    parent = this.parentNode.parentNode.parentNode;
    // update subject
    field = parent.getElementsByClassName('field-subject');
    django.jQuery(field).toggle(use_subject);
    // update markitup
    var textarea = django.jQuery(parent).find('.field-content textarea');
    textarea.markItUpRemove();
    if (this.value in markItUpSettings) {
        textarea.markItUp(markItUpSettings[this.value]);
    }
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

(function($){
    $(document).ready(function() {
        // show subject based on backends
        var backendSelects = $('.field-backend select');
        backendSelects.each(selectBackend);
        backendSelects.on('change', selectBackend);
        // disable targets
        var useTargetFields = {'use_sender': 'se', 'use_recipient': 're'}
        for (var useField in useTargetFields) {
            var useFieldElem = $('.field-' + useField + ' label+div img')[0]
            var prefix = useTargetFields[useField];
            if (useFieldElem.getAttribute('alt').toLowerCase() != 'true') {
                $('.field-target select').each(function() {
                    for (var i=0;i<this.options.length;i++) {
                        if (this.options[i].value.startsWith(prefix)) {
                            this.options[i].disabled=true;
                        }
                    }
                })
            }
        }
        // also set up CSRF ajax stuff
        var csrftoken = $("[name=csrfmiddlewaretoken]").val();
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
});
    })
})(django.jQuery)
