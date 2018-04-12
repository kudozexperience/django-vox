(function($) {

    var markItUpSettingsBasic = {
        onTab:    		{keepDefault:false, replaceWith:'    '},
        onShiftEnter:       {keepDefault:false, openWith:'\n\n'},
        markupSet:  []
    };

    var markItUpSettingsMarkdown = {
        onTab:    		{keepDefault:false, replaceWith:'    '},
        onShiftEnter:       {keepDefault:false, openWith:'\n\n'},
        markupSet:  [
            {name:'Bold', key:"B", className:'button-b', openWith:'**', closeWith:'**'},
            {name:'Italic', key:"I", className: 'button-i', openWith:'_', closeWith:'_'},
            {separator:'---------------' },
            {name:'Bulleted List', className: 'button-ul', openWith:'- ' },
            {name:'Numeric List', className: 'button-ol', openWith:function(markItUp) {
                return markItUp.line+'. ';
            }},
            {separator:'---------------' },
            {name:'Picture', key:"P", className: 'button-img',
                replaceWith:'![[![Alternative text]!]]([![Url:!:http://]!] "[![Title]!]")'},
            {name:'Link', key:"L", className: 'button-a', openWith:'[',
                closeWith:']([![Url:!:http://]!] "[![Title]!]")',
                placeHolder:'Your text to link here...' },
            {separator:'---------------'},
            {name:'Quotes', className: 'button-q', openWith:'> '},
            {name:'Code Block / Code', className: 'button-code',
                openWith:'(!(\t|!|`)!)', closeWith:'(!(`)!)'},
        ]
    };

    var markItUpSettingsHtml = {
        onShiftEnter:  	{keepDefault:false, replaceWith:'<br />\n'},
        onCtrlEnter:  	{keepDefault:false, openWith:'\n<p>', closeWith:'</p>'},
        onTab:    		{keepDefault:false, replaceWith:'    '},
        markupSet:  [
            {name:'Bold', key:'B', className:'button-b', openWith:'<strong>', closeWith:'</strong>' },
            {name:'Italic', key:'I', className: 'button-i', openWith:'<em>', closeWith:'</em>'  },
            {separator:'---------------' },
            {name:'Bulleted List', className: 'button-ul', openWith:'    <li>', closeWith:'</li>',
                multiline:true, openBlockWith:'<ul>\n', closeBlockWith:'\n</ul>'},
            {name:'Numeric List', className: 'button-ol', openWith:'    <li>', closeWith:'</li>',
                multiline:true, openBlockWith:'<ol>\n', closeBlockWith:'\n</ol>'},
            {separator:'---------------' },
            {name:'Picture', key:'P', className: 'button-img',
                replaceWith:'<img src="[![Source:!:http://]!]" alt="[![Alternative text]!]" />' },
            {name:'Link', key:'L', className: 'button-a',
                openWith:'<a href="[![Link:!:http://]!]"(!( title="[![Title]!]")!)>',
                closeWith:'</a>', placeHolder:'Your text to link...' },
        ]
    };

    var markItUpSettings = {
        'email': markItUpSettingsHtml,
        'email-md': markItUpSettingsMarkdown,
        'twilio': markItUpSettingsBasic,
        'slack-webhook': markItUpSettingsBasic,
    };


    function getMarkItUpSettings(backend, variables) {
        var settings = Object.assign({}, markItUpSettings[backend]);
        settings.previewParserPath = '../preview/' + backend + '/';
        settings.previewParserVar = 'body';
        var variableList = [];
        for (var i=0; i<variables.length; i++) {
            var variable = variables[i];
            var item = {name: variable.label, replaceWith: '{{ '+variable.value+' }}'};
            if ('attrs' in variable) {
                var sub_list = [];
                for (var j=0; j<variable.attrs.length; j++) {
                    var sub = variable.attrs[j];
                    sub_list.push({name: sub.label, replaceWith: '{{ '+sub.value+' }}'});
                }
                item.dropMenu = sub_list;
            }
            variableList.push(item);
        }
        settings.markupSet = [
            {name:'Variables', className:'variable', openWith:'{{ ', closeWith:' }}',
                dropMenu: variableList},
            {separator:'---------------' },
        ].concat(settings.markupSet);
        var lms = settings.markupSet.length;
        if (!('separator' in settings.markupSet[lms-1])) {
            settings.markupSet = settings.markupSet.concat(
                {separator:'---------------' });
        }
        settings.markupSet = settings.markupSet.concat(
            [{name:'Preview', className:'preview',  call:'preview'}]);
        return settings;
    }

    function disableTargetsByPrefix(options, prefix) {
        for (var i=0;i<options.length;i++) {
            if (options[i].value.startsWith(prefix)) {
                options[i].disabled=true;
            }
        }
    }

    function setup(variables) {
        // show subject based on backends
        var backendSelects = django.jQuery('.field-backend select');
        backendSelects.each(function() {selectBackend(this, variables);});
        backendSelects.on('change', function() {selectBackend(this, variables);});
        // disable targets
        var useTargetFields = {'use_sender': 'se', 'use_recipient': 're'};
        for (var useField in useTargetFields) {
            var useFieldElem = $('.field-' + useField + ' label+div img')[0];
            var prefix = useTargetFields[useField];
            if (useFieldElem.getAttribute('alt').toLowerCase() != 'true') {
                $('.field-target select').each(function() {
                    disableTargetsByPrefix(this.options, prefix);
                });
            }
        }
    }

    function selectBackend(elem, variables) {
        var opt = elem.options[elem.selectedIndex];
        var use_subject = opt.dataset.subject == 'true';
        parent = elem.parentNode.parentNode.parentNode;
        // update subject
        field = parent.getElementsByClassName('field-subject');
        django.jQuery(field).toggle(use_subject);
        // update markitup
        var textarea = django.jQuery(parent).find('.field-content textarea');
        textarea.markItUpRemove();
        if (elem.value in markItUpSettings) {
            textarea.markItUp(getMarkItUpSettings(elem.value, variables));
        }
    }

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }


    $(document).ready(function() {
        // set up CSRF ajax stuff
        var csrftoken = $("[name=csrfmiddlewaretoken]").val();
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        django.jQuery.ajax({
            type: 'POST',
            global: false,
            url: '../variables/',
            success: setup,
        });
    });
})(django.jQuery)
