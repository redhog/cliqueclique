dojo.provide("cliqueclique.document.Document");

dojo.require("cliqueclique.general.helpers");

dojo.declare("cliqueclique.document.BaseDocument", [], {
  constructor: function (json_data, object_id_base) {
    this.json_data = json_data;
    this.object_id_base = object_id_base;
  },
  getObjectId: function () {
    // Some random hashable the value that changes if any attributes changes
    return (this.object_id_base ? this.object_id_base : "") + this.json_data.document.document_id + ":" + this.json_data.bookmarked + ":" + this.json_data.read + ":" + this.json_data.local_is_subscribed;
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
  chainFunctions: function (functions, next_hook) {
    var data = {document:this};
    return cliqueclique.general.helpers.chainFunctions(
      functions,
      data,
      next_hook);
  }
});



dojo.declare("cliqueclique.document.Document", [cliqueclique.document.BaseDocument], {
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

cliqueclique.document.Document.object_id_counter = 0;

cliqueclique.document.Document.find = function (onComplete, query, context, object_id_base) {
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
       res.push(new cliqueclique.document.Document(documents[document_id], object_id_base));
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



dojo.declare("cliqueclique.document.NewDocument", [cliqueclique.document.BaseDocument], {
  constructor: function () {
    this.inherited(arguments, [{document: {content: {"__smime_MIMESigned__": true,
						     "header": {},
						     "parts": [{"__email_mime_multipart_MIMEMultipart__": true,
								"header": {},
								"parts": []}]}}}]);
    this.post_hooks = [];
  },
  createPart: function (part_type, cls, contentType) {
    var parts = this.getParts();
    var part = parts[part_type]
    if (part === undefined) {
      part = {header:{part_type:part_type}};
      this.getContent().parts.push(part);
    }
    if (cls !== undefined) part[cls] = true;
    if (contentType !== undefined) part.header["Content-Type"] = contentType;
    return part;
  },
  /* Hook is function ({document:document}, next_hook) */
  addPostHook: function (hook) {
    this.post_hooks.push(hook);
  },
  callPostHooks: function (document, callback) {
    document.chainFunctions(
      this.post_hooks,
      function (data) {
	cliqueclique.document.Document.updated();
	callback(data);
      }
    )();
  },
  /* Post the document. Callback is function({document:document}).
     The dictionary parameter can optionally contain other data and/or
     documents created by post hooks. */
  post: function (callback, error_callback) {
    // console.log(["post", this.json_data.document.content]);
    if (!error_callback) {
      error_callback = function (error) {
        if (typeof(error) != 'string') {
 	  error = error.type + ": " + error.description + "\n" + error.traceback;
        }
	console.error(error);
      }
    }
    var new_document = this;
    if (callback == undefined)
      callback = function () {};
    dojo.xhrGet({
      url: "/post",
      handleAs: "json",
      content: { document: dojo.toJson(new_document.json_data.document.content) },
      load: function(data) {
	// Do this in a timeout so that the error function isn't called
	// if callback throws an unhandled exception and so that the
	// traceback is shown if you use a debugging tool
	setTimeout(function () {
	  if (data.error != undefined) {
	    error_callback(data.error);
	  } else {
	    new_document.callPostHooks(cliqueclique.document.Document(data), callback);
	  }
	}, 1);
      },
      error: function(error) {
	error_callback(error);
      }
    });
  },
});

cliqueclique.document.NewDocument.prototype.makeLink = function (src, dst, reversed) {
  var subject;
  if (reversed)
    subject = src.getSubject();
  else
    subject = dst.getSubject();

  var direction = reversed ? "reversed" : "natural";

  var content = this.getContent();
  content.header.parent_document_id = src.getDocumentId();
  content.header.child_document_id = dst.getDocumentId();
  if (content.header == undefined) {
    content.header.subject = subject;
  }
  var part = this.createPart("link", "__email_message_Message__", "text/plain; charset=\"utf-8\"");
  part.body = '';
  part.header.link_direction = direction;
}

