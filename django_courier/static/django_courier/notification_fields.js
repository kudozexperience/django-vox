function selectBackend() {
    var opt = this.options[this.selectedIndex];
    var use_subject = opt.dataset.subject == 'true';
    parent = this.parentNode.parentNode.parentNode;
    field = parent.getElementsByClassName('field-subject');
    django.jQuery(field).toggle(use_subject);
}

(function($){
    $(document).ready(function(){
        // show subject based on backends
        var backendSelects = $('.field-backend select');
        backendSelects.each(selectBackend);
        backendSelects.on('change', selectBackend);
        // disable targets
        var useTargetFields = {'use_sender': 'se', 'use_recipient': 're'}
        var use_sender = $('.field-use_sender label+div img')[0]
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
    })
})(django.jQuery)
