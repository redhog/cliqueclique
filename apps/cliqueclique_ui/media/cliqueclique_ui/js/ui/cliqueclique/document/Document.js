dojo.provide("cliqueclique.document.Document");

dojo.require("cliqueclique.general.helpers");

dojo.declare("cliqueclique.document.Document", [], {
  constructor: function (json_data) {
    this.json_data = json_data;
  },
  getObjectId: function () {
    // Some random hashable the value that changes if any attributes changes
    return this.json_data.document.document_id + ":" + this.json_data.bookmarked + ":" + this.json_data.read + ":" + this.json_data.local_is_subscribed;
  },
  getDocumentId: function () {
    return this.json_data.document.document_id;
  },
  getContent: function () {
    try {
      return this.json_data.document.content.parts[0];
    } catch(err) {
      return undefined;
    }
  },
  getParts: function () {
    var content = this.getContent();
    var parts = {};
    try {
      dojo.forEach(content.parts, function (part) {
        parts[part.header['part_type']] = part;
      });
    } catch(err) {
      return undefined;
    }
    return parts;
  },
  getSubject: function () {
    var content = this.getContent()
    try {
      return content.header.subject;
    } catch(err) {
      try {
       return this.getDocumentId().substring(0, 5);
      } catch(err) {
	return undefined;
      }
    }
  },
  getParentDocumentId: function () {
    try {
      return this.getContent().header.parent_document_id;
    } catch(err) {
      return undefined;
    }
  },
  getChildDocumentId: function () {
    try {
      return this.getContent().header.child_document_id;
    } catch(err) {
      return undefined;
    }
  },
  getBody: function () {
    var parts = this.getParts();
    try {
      return parts.content.body;
    } catch(err) {
      try {
        return this.getContent().body;
      } catch(err) {
        try {
          return this.json_data.document.content.body;
        } catch(err) {
	  return undefined;
        }
      }
    }
  },
  getDocumentLink: function (widget) {
    var document = this;
    return function () {
      var link = widget.getDataDefault("documentLink", "cliqueclique.document.DocumentLink");
      if (link) return link.load(document);
      // Do something intelligent here
    };
  },
  setAttribute: function (name, value, onComplete) {
    if (value) value = "true";
    if (value === undefined) value = "toggle";
    if (!value) value = "";

    this.json_data[name] = value; // Set it already client-side, since we might not actually reload the item

    dojo.xhrGet({
      url: "/" + this.getDocumentId() + "/set?" + name + "=" + value,
      load: function(data) {
        if (data.error !== undefined) {
	  console.error(data.error.type + ": " + data.error.description + "\n" + data.error.traceback);
	  return;
        }
	if (onComplete)
	  onComplete();
	else
  	  cliqueclique.document.Document.updated();
      }
    });
  }

});

cliqueclique.document.Document.post = function (json_data__document, callback) {
  if (callback == undefined)
    callback = function () {};
  dojo.xhrGet({
    url: "/post",
    handleAs: "json",
    content: { document: dojo.toJson(json_data__document) },
    load: function(data) {
      if (data.error != undefined) {
        callback(null, data.error);
      } else {
        cliqueclique.document.Document.updated();
        callback(cliqueclique.document.Document(data));
      }
    },
    error: function(error) {
      callback(null, error);
    }
  });
}

cliqueclique.document.Document.post_link = function (src, dst, callback, reversed, subject, parts) {
  if (subject === undefined)
    if (reversed)
      subject = src.getSubject();
    else
      subject = dst.getSubject();

  var direction = reversed ? "reversed" : "natural";

  var real_parts = [{"__email_message_Message__": true,
		     "body": "",
		     "header": {"part_type": "link",
				"link_direction": direction,
				"Content-Type": "text/plain; charset=\"utf-8\""}}];
  if (parts !== undefined)
    dojo.forEach(parts, function (part) {
      real_parts.push(part);
    });

  cliqueclique.document.Document.post(
    {
      "__smime_MIMESigned__": true,
      "header": {},
      "parts": [{"__email_mime_multipart_MIMEMultipart__": true,
		 "parts": real_parts,
		 "header": {"parent_document_id": src.getDocumentId(),
	                    "child_document_id": dst.getDocumentId(),
	                    "subject": subject}}]},
    callback
  );
}

cliqueclique.document.Document.find = function (onComplete, query, context) {
  var url = "/find/json";
  if (context) {
    url = "/find/json/" + context;
  }
  dojo.xhrGet({
    url: url,
    handleAs: "json",
    content: { query: dojo.toJson(query) },
    load: function (documents) {
      if (documents.error !== undefined) {
	console.error(documents.error.type + ": " + documents.error.description + "\n" + documents.error.traceback);
	return;
      }
      var res = [];
      for (document_id in documents) {
	res.push(new cliqueclique.document.Document(documents[document_id]));
      }
      onComplete(res);
    }
  });
}

/* FIXME: Handle attr values with = and spaces in them (and " around such values) correctly */
cliqueclique.document.Document.parseContentType = function (mimePart) {
  var res = {attrs: {}};

  contentTypeParts = cliqueclique.general.helpers.splitWithQuotes(mimePart.header["Content-Type"], /; */);
  var contentType = contentTypeParts[0].split("/");

  for (var i = 1; i < contentTypeParts.length; i++) {
    var nameValue = /^([^=]*)=(.*)$/.exec(contentTypeParts[i]);
    res.attrs[nameValue[1].toLowerCase()] = nameValue[2];
  }

  res.subtype = contentType[1].toLowerCase();
  res.type = contentType[0].toLowerCase();

  return res;
}


cliqueclique.document.Document.updated = function () {};
