dojo.provide("cliqueclique.document._AbstractDocumentChangeEditor");

dojo.require("cliqueclique.document._AbstractDocumentEditor");
dojo.require("cliqueclique.document.DocumentSelector");
dojo.require("dijit.form.CheckBox");
dojo.require("dijit._Widget");
dojo.require("dijit._Templated");

dojo.declare("cliqueclique.document._AbstractDocumentChangeEditor", [cliqueclique.document._AbstractDocumentEditor], {
  editWidgetChange: dojo.declare("", [dijit._Widget, dijit._Templated], {
    placement: "formMetadata",
    widgetsInTemplate: true,
    templateString: "<tbody>" +
		    "  <tr>" +
		    "   <th>Document</th>" +
		    "   <td><div dojoType='cliqueclique.document.DocumentSelector' single='true' dojoAttachPoint='toChange'></div></td>" +
		    "  </tr>" +
		    "</tbody>",
    send: function (doc) {
    }
  }),
  getDocument: function () {
    return this.editWidgetPath.toChange.attr("links")[0];
  },
  toChangeSet: function (document) {
    this.editWidgetChange.toChange.addLink(document);
    if (this.subjectSet) {
      this.subjectSet(document.getSubject());
    }
  }
});
