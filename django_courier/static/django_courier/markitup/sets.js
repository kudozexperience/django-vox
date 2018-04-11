
var markUpSetPrefix = [
    {name:'Variables', className:'variable', openWith:'{{ ', closeWith:' }}', dropMenu: [
        {name: 'Contact', replaceWith: '{{ contact }}'},
        {name: 'Content', replaceWith: '{{ content }}'},
        {name: 'Sender', replaceWith: '{{ sender }}'},
        {name: 'Recipient', replaceWith: '{{ recipient }}'},
    ]},
    {separator:'---------------' },
]


var markItUpSettingsBasic = {
    onTab:    		{keepDefault:false, replaceWith:'    '},
    onShiftEnter:       {keepDefault:false, openWith:'\n\n'},
    markupSet:  []
}

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
        {name:'Picture', key:"P", className: 'button-img', replaceWith:'![[![Alternative text]!]]([![Url:!:http://]!] "[![Title]!]")'},
        {name:'Link', key:"L", className: 'button-a', openWith:'[', closeWith:']([![Url:!:http://]!] "[![Title]!]")', placeHolder:'Your text to link here...' },
        {separator:'---------------'},
        {name:'Quotes', className: 'button-q', openWith:'> '},
        {name:'Code Block / Code', className: 'button-code',
            openWith:'(!(\t|!|`)!)', closeWith:'(!(`)!)'},
    ]
}

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
}

var markItUpSettings = {
    'email': Object.assign({}, markItUpSettingsHtml),
    'email-md': Object.assign({}, markItUpSettingsMarkdown),
    'twilio': Object.assign({}, markItUpSettingsBasic),
    'slack-webhook': Object.assign({}, markItUpSettingsBasic),
}

for (var backend in markItUpSettings) {
    var settings = markItUpSettings[backend];
    settings.previewParserPath = '../preview/' + backend + '/';
    settings.previewParserVar = 'body';
    settings.markupSet = markUpSetPrefix.concat(settings.markupSet);
    var lms = settings.markupSet.length;
    if (!('separator' in settings.markupSet[lms-1])) {
        settings.markupSet = settings.markupSet.concat(
            {separator:'---------------' })
    }
    settings.markupSet = settings.markupSet.concat(
        [{name:'Preview', className:'preview',  call:'preview'}])
    markItUpSettings[backend] = settings;
}
