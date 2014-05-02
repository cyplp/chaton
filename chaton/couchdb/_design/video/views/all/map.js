function(doc) {
    if (doc.doc_type == "Video")
    {
	emit(doc.created, doc);
    }
}
