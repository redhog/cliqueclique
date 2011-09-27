dojo.provide("cliqueclique.document._AbstractDocumentLinksEditor");

dojo.require("cliqueclique.document._AbstractDocumentEditor");
dojo.require("cliqueclique.document.DocumentSelector");
dojo.require("dijit._Widget");
dojo.require("dijit._Templated");

dojo.declare("cliqueclique.document._AbstractDocumentLinksEditor", [cliqueclique.document._AbstractDocumentEditor], {
  editWidgetLinks: dojo.declare("", [dijit._Widget, dijit._Templated], {
    placement: "formMetadata",
    widgetsInTemplate: true,
    templateString: "<tbody>" +
		    "  <tr>" +
		    "    <th>Comment to</th>" +
		    "    <td><div dojoType='cliqueclique.document.DocumentSelector' dojoAttachPoint='commentsTo'></div></td>" +
		    "    <th>Hidden comment to</th>" +
		    "    <td><div dojoType='cliqueclique.document.DocumentSelector' dojoAttachPoint='commentsToHidden'></div></td>" +
		    "  </tr>" +
		    "  <tr>" +
		    "    <th>Has comments in</th>" +
		    "    <td><div dojoType='cliqueclique.document.DocumentSelector' dojoAttachPoint='commentsInHidden'></div></td>" +
		    "    <th>Has back-linking comments in</th>" +
		    "    <td><div dojoType='cliqueclique.document.DocumentSelector' dojoAttachPoint='commentsIn'></div></td>" +
		    "  </tr>" +
                    "</tbody>",
    send: function (doc) {
      var links = [{src: "item", dst:"document", reversed: false, items: this.commentsTo.attr("links")},
		   {src: "document", dst:"item", reversed: true, items: this.commentsToHidden.attr("links")},
		   {src: "document", dst:"item", reversed: false, items: this.commentsInHidden.attr("links")},
		   {src: "item", dst:"document", reversed: true, items: this.commentsIn.attr("links")}];

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
  commentsToAdd: function (document) {
    this.editWidgetLinks.commentsTo.addLink(document);
  },
  commentsInAdd: function (document) {
    this.editWidgetLinks.commentsIn.addLink(document);
  }
});