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

    var markItUpSettingsHtmlLight = {
        onShiftEnter:  	{keepDefault:false, replaceWith:'<br />\n'},
        onCtrlEnter:  	{keepDefault:false, openWith:'\n<p>', closeWith:'</p>'},
        onTab:    		{keepDefault:false, replaceWith:'    '},
        markupSet:  [
            {name:'Bold', key:'B', className:'button-b', openWith:'<strong>', closeWith:'</strong>' },
            {name:'Italic', key:'I', className: 'button-i', openWith:'<em>', closeWith:'</em>'  },
            {name:'Link', key:'L', className: 'button-a',
                openWith:'<a href="[![Link:!:http://]!]"(!( title="[![Title]!]")!)>',
                closeWith:'</a>', placeHolder:'Your text to link...' },
        ]
    };

    var markItUpSettings = {
        'html-light': markItUpSettingsHtmlLight,
        'html': markItUpSettingsHtml,
        'markdown': markItUpSettingsMarkdown,
        'basic': markItUpSettingsBasic,
    };

    function parseVariables(recipients, variables) {
        var result = [];
        for (var i=0; i<recipients.length; i++) {
            var rec = recipients[i];
            if (Object.keys(variables).includes(rec)) {
                result = result.concat(parseSubVariables([variables[rec]]));
            }
        }
        result = result.concat(parseSubVariables(variables._static));
        return result;
    }

    function parseSubVariables(variables){
        var result = [];
        for (var i=0; i<variables.length; i++) {
            var variable = variables[i];
            var item = {name: variable.label, replaceWith: '{{ '+variable.value+' }}'};
            if ('attrs' in variable) {
                var attrs_list = [];
                var rel_list = [];
                for (var j=0; j<variable.attrs.length; j++) {
                    var sub = variable.attrs[j];
                    attrs_list.push({name: sub.label, replaceWith: '{{ '+sub.value+' }}'});
                }
                if ('rels' in variable) {
                    var rel_list = parseSubVariables(variable.rels);
                }
                var rel_len = rel_list.length
                if (rel_len < 1 || rel_len + attrs_list.length < 11) {
                    item.dropMenu = attrs_list.concat(rel_list);
                } else {
                    item.dropMenu = [{name: 'Attributes', dropMenu: attrs_list},
                                     {name: 'Relations', dropMenu: rel_list}];
                }
            }
            result.push(item);
        }
        return result;
    }


    function getMarkItUpSettings(backend, editor, recipients, variables, previewUrl) {
        var settings = Object.assign({}, markItUpSettings[editor]);
        if (previewUrl === null) {
            settings.previewParserPath = '../preview/' + backend + '/';
        } else {
            settings.previewParserPath = previewUrl.replace('__backend__', backend)
        }
        settings.previewParserVar = 'body';
        if (variables != null) {
            var variableList = parseVariables(recipients, variables);
            settings.markupSet = [
                {name:'Variables', className:'variable', openWith:'{{ ', closeWith:' }}',
                    dropMenu: variableList},
                {separator:'---------------' },
            ].concat(settings.markupSet);
        }
        var lms = settings.markupSet.length;
        if (lms > 0 && !('separator' in settings.markupSet[lms-1])) {
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

    function findField(name, fieldType, parent=null) {
        var spec = ('.field-' + name + ' ' + fieldType
                    + ', .grp-row.' + name + ' ' + fieldType);
        if (parent===null) return $(spec);
        return parent.find(spec);
    }

    function findFieldRow(name, parent=null) {
        var spec = ('.field-' + name + ', .grp-row.' + name);
        if (parent===null) return $(spec);
        return parent.find(spec);
    }

    function setup(variables) {
        // show subject based on backends
        findField('recipients', 'input').on('change', function() {
            selectRecipient(this, variables);});
        findField('bulk', 'input').on('change', function() {
            selectRecipient(this, variables);});
        var backendSelects = findField('backend', 'select');
        backendSelects.each(function() {selectBackend(this, variables);});
        backendSelects.on('change', function() {selectBackend(this, variables);});
    }

    function selectBackend(elem, variables) {
        // show/hide fields
        var ds = elem.options[elem.selectedIndex].dataset;
        var parent = $(elem).closest('fieldset')
        // update subject
        findFieldRow('subject', parent).toggle(ds.subject == 'true');
        // update attachments
        findFieldRow('attachments', parent).toggle(ds.attachment == 'true');
        // update from address
        findFieldRow('from_address', parent).toggle(ds.from_address == 'true');
        // update markitup
        refreshMarkItUp(parent, variables);
    }

    function selectRecipient(elem, variables) {
        refreshMarkItUp($(elem).closest('fieldset'), variables);
    }

    function refreshMarkItUp(fieldset, variables) {
        var bulk = findField('bulk', 'input', fieldset)[0];
        // find value
        var recipients = [];
        if (bulk && !bulk.checked)
            recipients = findField('recipients', 'input', fieldset).filter(
                    function() { return this.checked; }).map(
                    function() { return this.value; }).get();
        var backendSelect = findField('backend', 'select', fieldset)[0];
        var opt = backendSelect.selectedOptions[0];
        var backend = opt.value;
        var editor = opt.dataset.editor;
        var textarea = findField('content', 'textarea', fieldset);
        textarea.markItUpRemove();
        if (editor in markItUpSettings) {
            var previewUrl = textarea.data('preview-url') || null;
            textarea.markItUp(getMarkItUpSettings(
                backend, editor, recipients, variables, previewUrl));
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
        // only on the change page with the template inline
        if (document.getElementById('template_set-group')) {
            django.jQuery.ajax({
                type: 'POST',
                global: false,
                url: '../variables/',
                success: setup,
            });
        } else {
            setup(null);
        }

    });
})(django.jQuery)
