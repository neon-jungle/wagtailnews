function(modal) {
    modal.respond('carChosen', {{ snippet_json|safe }});
    modal.close();
}
