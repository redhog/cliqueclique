dojo.provide("cliqueclique.document._AbstractDocumentForwardEditor");

dojo.require("cliqueclique.document._AbstractDocumentEditor");
dojo.require("cliqueclique.document.DocumentSelector");
dojo.require("cliqueclique.document.Document"); // Should be NewDocument...
dojo.require("dijit.form.CheckBox");
dojo.require("dijit._Widget");
dojo.require("dijit._Templated");

cliqueclique.document.NewDocument.prototype.makeForward = function (src) {
  var part = this.createPart("subscription_update", "__email_mime_multipart_MIMEMultipart__");
  part.parts.push({__cliqueclique_document_models_DocumentSubscription_export__: true});
}

dojo.declare("cliqueclique.document._AbstractDocumentForwardEditor", [cliqueclique.document._AbstractDocumentEditor], {
  editWidgetForward: dojo.declare("", [dijit._Widget, dijit._Templated], {
    placement: "formMetadata",
    widgetsInTemplate: true,
    templateString: "<tbody>" +
		    "  <tr>" +
		    "   <th>Forward</th>" +
		    "   <td><div dojoType='cliqueclique.document.DocumentSelector' single='true' dojoAttachPoint='forwardDoc'></div></td>" +
		    "  </tr>" +
		    "</tbody>",
    send: function (doc) {
      doc.makeForward(this.commentTo.attr("links")[0], this.forwardDoc.attr("links")[0], this.reversed.attr("value"));
    }
  }),
  forwardDocSet: function (document) {
    this.editWidgetForward.forwardDoc.addLink(document);
    if (this.subjectSet) {
      this.subjectSet(document.getSubject());
    }
  },
});
