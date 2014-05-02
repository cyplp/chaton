function(doc) {
    if (doc.doc_type == "Video")
    {
	for (tag in doc.tags)
	{
	    emit([doc.tags[tag], doc.created], doc);
	}
    }
}
