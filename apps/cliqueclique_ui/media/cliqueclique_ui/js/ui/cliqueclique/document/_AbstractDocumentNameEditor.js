dojo.provide("cliqueclique.document._AbstractDocumentNameEditor");

dojo.require("cliqueclique.document._AbstractDocumentEditor");
dojo.require("cliqueclique.document.DocumentSelector");
dojo.require("dijit.form.CheckBox");
dojo.require("dijit._Widget");
dojo.require("dijit._Templated");

cliqueclique.document.NewDocument.prototype.getName = function () {
  var parts = this.getParts();
  if (!parts.path_part) return "";
  return parts.path_part.header.name;
}

cliqueclique.document.NewDocument.prototype.makeNamePart = function (prev, name) {
  // returns true if this is not the last needed part.
  var content = this.getContent();
  var prevName = prev.getName();
  content.header.parent_document_id = prev.getDocumentId();

  var part = this.createPart("parent_link", "__email_message_Message__", "text/plain; charset=\"utf-8\"");
  part.header.link_direction = 'natural';
  part.header.link_type = 'name_part';
  part.header.name = name.substring(0, prevName.length + 1)
  return prevName.length + 1 < name.length;
}

cliqueclique.document.NewDocument.makeName = function (src, name, callback, error_callback) {
  var new_callback = callback;
  var part = new cliqueclique.document.NewDocument();
  if (part.makeNamePart(prev, name)) {
    new_callback = function (data) {
      cliqueclique.document.NewDocument.makeName(data.document, name, callback, error_callback);
    }
  }
  part.post(new_callback, error_callback);
}

cliqueclique.document.NewDocument.makeNameLink = function (src, name, dst, reversed, callback, error_callback) {
  cliqueclique.document.NewDocument.makeName(
    src,
    name,
    function (path_data) {
      var link = new cliqueclique.document.NewDocument();
      link.makeLink(path_data.document, dst, reversed);
      var link_part = link.getParts().link
      link_part.header.link_type = 'named_document'
      link.post(next_hook);
    }
  );
}


dojo.declare("cliqueclique.document._AbstractDocumentNameEditor", [cliqueclique.document._AbstractDocumentEditor], {
  editWidgetPath: dojo.declare("", [dijit._Widget, dijit._Templated], {
    placement: "formMetadata",
    widgetsInTemplate: true,
    templateString: "<tbody>" +
		    "  <tr>" +
		    "   <th>Reverse visibility (document sees directory)</th>" +
		    "   <td><div dojoType='dijit.form.CheckBox' dojoAttachPoint='reversed'></div></td>" +
		    "  </tr>" +
		    "  <tr>" +
		    "   <th>Directory</th>" +
		    "   <td><div dojoType='cliqueclique.document.DocumentSelector' single='true' dojoAttachPoint='publishIn'></div></td>" +
		    "  </tr>" +
                    "  <tr>" +
                    "    <th>Name</th>" +
                    "    <td><div dojoType='dijit.form.TextBox' dojoAttachPoint='name'></div></td>" +
                    "  </tr>" +
		    "</tbody>",
    send: function (doc) {
      doc.addPostHook(function (data, next_hook) {
	cliqueclique.document.NewDocument.makeNameLink(
	  this.publishIn.attr("links")[0],
	  this.name.attr("value"),
	  data.document,
	  this.reversed.attr("value"),
	  next_hook
	);
      });
    }
  }),
  publishInSet: function (document) {
    this.editWidgetPath.publishIn.addLink(document);
  },
  subjectSet: function (name) {
    this.editWidgetPath.name.attr("value", name);
  },
});
