function hashCode(string) {
    var hash = 0;
    if (string.length == 0) return hash;
    for (i = 0; i < string.length; i++) {
        var chr = string.charCodeAt(i);
        hash = ((hash<<5)-hash)+chr;
        hash = hash & hash; // Convert to 32bit integer
    }
    return hash;
}

function init_content (doc) {
    if (!doc) {
        doc = document;
    }
    var divs = $(doc).contents().find('div[contenteditable]');
    var span_containers = $(doc).contents().find('div[data-content=true]');
    $.each(divs, function () {
        $(this).attr('data-hash', hashCode($(this).html()));
    });
    $.each(span_containers, function () {
        $(this).attr('data-hash', hashCode($(this).html()));
    });
}

function save_content (options) {
    var options = options || {};
    //Params : document, message, author, author_email, ok_callback, error_callback, empty_callback
    options.document = options.document ? options.document : $(document);
    
    // Get all the contenteditable elements
    var divs = $(options.document).contents().find('div[contenteditable]');
    var span_containers = $(options.document).contents().find('div[data-content=true]');

    if (divs.length == 0 && span_containers.length == 0) {
        alert('There is no contenteditable on this document.');
        return false;
    }
    
    var data = [];
    if (divs.length != 0) {
        $.each(divs, function () {
            var $this = $(this);
            if($this.attr('data-hash') != hashCode($this.html())) {
                data.push({
                    "part": $this.attr('data-part'),
                    "document_type": $this.attr('data-document-type'),
                    "document_id": $this.attr('data-document-id'),
                    "version": $this.attr('data-document-version'),
                    "content": $this.html()
                });
            }
            $(this).attr('data-hash', hashCode($(this).html()));
        });
    }
    if (span_containers.length != 0) {
        $.each(span_containers, function () {
            var $this = $(this);
            if($this.attr('data-hash') != hashCode($this.html())) {
                var spans = $this.find('span[contenteditable]');
                var values = [];
                $.each(spans, function () {
                    values.push($(this).html());
                });
                data.push({
                    "part": $this.attr('data-part'),
                    "document_type": $this.attr('data-document-type'),
                    "document_id": $this.attr('data-document-id'),
                    "version": $this.attr('data-document-version'),
                    "content": JSON.stringify(values)
                });
            }
            $this.attr('data-hash', hashCode($this.html()));
        });
    }

    // Check if contents is null
    if (data.length == 0) {
        if ('unchange_callback' in options) options.unchange_callback();
        return false;
    }

    // Get commit options
    var commit_message = options.message ? options.message : null;
    var commit_author = options.author ? options.author : null;
    var commit_author_email = options.author_email ? options.author_email : null;
    // Make ajax
    $.ajax({
        url: '/_pynuts/update_content',
        data: JSON.stringify({
            'data': data,
            'message': commit_message,
            'author': commit_author,
            'author_email': commit_author_email
        }),
        contentType: 'application/json',
        dataType: 'json',
        type: "POST",
        success: function(response){
            if(response && response.documents) {
                $.each(response.documents, function () {
                    var divs = options.document.contents().find(
                        'div[contenteditable]' +
                        '[data-document-type="' + this.document_type + '"]' +
                        '[data-document-id="' + this.document_id + '"]'
                    );
                    divs.attr('data-document-version', this.version);
                    span_containers.attr('data-document-version', this.version);
                });
                if ('success_callback' in options) options.success_callback();
            } else {
                if ('fail_callback' in options) options.fail_callback();
            }
        }
    });
}
