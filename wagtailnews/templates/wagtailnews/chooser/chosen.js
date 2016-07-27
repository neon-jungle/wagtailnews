function(modal) {
    modal.respond('newsItemChosen', {{ newsitem_json|safe }});
    modal.close();
}
