function(modal) {
    modal.respond('newsItemChosen', {{ snippet_json|safe }});
    modal.close();
}
