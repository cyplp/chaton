function(doc) {
    if (doc.doc_type == "Comment")
    {
	emit([doc.videoid, doc.created], doc);
    }
}
