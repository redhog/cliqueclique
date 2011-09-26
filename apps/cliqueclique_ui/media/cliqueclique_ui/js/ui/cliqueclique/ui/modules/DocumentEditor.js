dojo.provide("cliqueclique.ui.modules.DocumentEditor");

dojo.require("cliqueclique.ui");
dojo.require("cliqueclique.document._AbstractDocumentEditor");
dojo.require("cliqueclique.document.DocumentSelector");
dojo.require("dijit.form.TextBox");
dojo.require("dijit.Editor");

dojo.declare("cliqueclique.ui.modules.DocumentEditor", [cliqueclique.document._AbstractDocumentEditor], {
  editWidgetLinks: dojo.declare("", [dijit._Widget, dijit._Templated], {
    placement: "formMetadata",
    widgetsInTemplate: true,
    templateString: "<tbody>" +
		    "  <tr>" +
		    "    <th>Comment to</th>" +
		    "    <td><div dojoType='cliqueclique.document.DocumentSelector' dojoAttachPoint='commentTo'></div></td>" +
		    "    <th>Hidden comment to</th>" +
		    "    <td><div dojoType='cliqueclique.document.DocumentSelector' dojoAttachPoint='commentToHidden'></div></td>" +
		    "  </tr>" +
		    "  <tr>" +
		    "    <th>Has comments in</th>" +
		    "    <td><div dojoType='cliqueclique.document.DocumentSelector' dojoAttachPoint='commentInHidden'></div></td>" +
		    "    <th>Has back-linking comments in</th>" +
		    "    <td><div dojoType='cliqueclique.document.DocumentSelector' dojoAttachPoint='commentIn'></div></td>" +
		    "  </tr>" +
                    "</tbody>",
    send: function (doc) {
      var links = [{src: "item", dst:"document", reversed: false, items: this.commentTo.attr("links")},
		   {src: "document", dst:"item", reversed: true, items: this.commentToHidden.attr("links")},
		   {src: "document", dst:"item", reversed: false, items: this.commentInHidden.attr("links")},
		   {src: "item", dst:"document", reversed: true, items: this.commentIn.attr("links")}];

      /*
        var content = doc.getContent();
        content.header.parent_document_id = xyzzy.getDocumentId();
        content.header.child_document_id = xyzzy.getDocumentId();
      */

      dojo.forEach(links, function (link) {
	dojo.forEach(link.items, function (item) {
	  doc.addPostHook(function (data, next_hook) {
	    var params = {document: data.document, item: item};
	    var link_doc = cliqueclique.document.NewDocument();
	    link_doc.makeLink(params[link.src], params[link.dst], link.reversed);
	    link_doc.post(function(link_data) {
	      if (data.links === undefined) data.links = [];
	      data.links.push(link_data);
	      next_hook(data);
	    });
	  });
	});
      });
    }
  }),
  editWidgetSubject: dojo.declare("", [dijit._Widget, dijit._Templated], {
    placement: "formMetadata",
    widgetsInTemplate: true,
    templateString: "<tbody>" +
                    "  <tr>" +
                    "    <th>Subject</th>" +
                    "    <td><div dojoType='dijit.form.TextBox' dojoAttachPoint='subject'></div></td>" +
                    "  </tr>" +
		    "</tbody>",
    send: function (doc) {
      var content = doc.getContent();
      content.header.subject = this.subject.attr("value");
    }
  }),
  editWidgetContent: dojo.declare("", [dijit._Widget, dijit._Templated], {
    placement: "formMain",
    widgetsInTemplate: true,
    templateString: "<div>" +
		    "  <div dojoType='dijit.Editor' dojoAttachPoint='content'></div>" +
		    "</div>",
    send: function (doc) {
      var part = doc.createPart("content", "__email_message_Message__", "text/plain; charset=\"utf-8\"");
      part.body = this.content.attr("value");
    }
  }),
  commentToAdd: function (document) {
    this.editWidgetLinks.commentTo.addLink(document);
  },
  commentInAdd: function (document) {
    this.editWidgetLinks.commentIn.addLink(document);
  }
});

cliqueclique.ui.modules.DocumentEditor.register = function (widget) {
  widget.registerData("documentLink",
		      {label: 'Comment',
		       load:function (document) {
			 var docEdit = new cliqueclique.ui.modules.DocumentEditor({title: 'New comment'});
			 docEdit.commentToAdd(document);
			 widget.getDataDefault("panels").addChild(docEdit);
		       }},
		       false,
		       "cliqueclique.document.DocumentLink");

};
