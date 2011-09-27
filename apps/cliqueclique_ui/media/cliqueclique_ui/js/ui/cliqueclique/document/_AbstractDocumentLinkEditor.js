dojo.provide("cliqueclique.document._AbstractDocumentLinkEditor");

dojo.require("cliqueclique.document._AbstractDocumentEditor");
dojo.require("cliqueclique.document.DocumentSelector");
dojo.require("dijit.form.CheckBox");
dojo.require("dijit._Widget");
dojo.require("dijit._Templated");

dojo.declare("cliqueclique.document._AbstractDocumentLinkEditor", [cliqueclique.document._AbstractDocumentEditor], {
  editWidgetLink: dojo.declare("", [dijit._Widget, dijit._Templated], {
    placement: "formMetadata",
    widgetsInTemplate: true,
    templateString: "<tbody>" +
		    "  <tr>" +
		    "   <th>Reverse visibility (comment sees commented)</th>" +
		    "   <td><div dojoType='dijit.form.CheckBox' dojoAttachPoint='reversed'></div></td>" +
		    "  </tr>" +
		    "  <tr>" +
		    "   <th>Comment to</th>" +
		    "   <td><div dojoType='cliqueclique.document.DocumentSelector' single='true' dojoAttachPoint='commentTo'></div></td>" +
		    "  </tr>" +
		    "  <tr>" +
		    "   <th>Has comment in</th>" +
		    "   <td><div dojoType='cliqueclique.document.DocumentSelector' single='true' dojoAttachPoint='commentIn'></div></td>" +
		    "  </tr>" +
		    "</tbody>",
    send: function (doc) {
      doc.makeLink(this.commentTo.attr("links")[0], this.commentIn.attr("links")[0], this.reversed.attr("value"));
    }
  }),
  commentToSet: function (document) {
    this.editWidgetLink.commentTo.addLink(document);
  },
  commentInSet: function (document) {
    this.editWidgetLink.commentIn.addLink(document);
  }
});
