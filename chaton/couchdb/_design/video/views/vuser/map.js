function(doc) {
    if (doc.doc_type == "Video")
    {
	emit([doc.userid, doc.created], doc);
    }
}
