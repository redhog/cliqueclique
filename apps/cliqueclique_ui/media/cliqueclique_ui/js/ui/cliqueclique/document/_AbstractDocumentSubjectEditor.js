dojo.provide("cliqueclique.document._AbstractDocumentSubjectEditor");

dojo.require("cliqueclique.document._AbstractDocumentEditor");
dojo.require("cliqueclique.document.DocumentSelector");
dojo.require("dijit.form.TextBox");
dojo.require("dijit._Widget");
dojo.require("dijit._Templated");

dojo.declare("cliqueclique.document._AbstractDocumentSubjectEditor", [cliqueclique.document._AbstractDocumentEditor], {
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
  subjectSet: function (subject) {
    this.editWidgetSubject.subject.attr("value", subject);
  }
});