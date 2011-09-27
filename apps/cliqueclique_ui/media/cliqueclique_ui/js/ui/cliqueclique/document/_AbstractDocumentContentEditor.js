dojo.provide("cliqueclique.document._AbstractDocumentContentEditor");

dojo.require("cliqueclique.document._AbstractDocumentEditor");
dojo.require("cliqueclique.document.DocumentSelector");
dojo.require("dijit.Editor");
dojo.require("dijit._Widget");
dojo.require("dijit._Templated");

dojo.declare("cliqueclique.document._AbstractDocumentContentEditor", [cliqueclique.document._AbstractDocumentEditor], {
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
});
