dojo.provide("cliqueclique.ui.modules.DocumentForwardEditor");

dojo.require("cliqueclique.ui");
dojo.require("cliqueclique.document._AbstractDocumentEditor");
dojo.require("cliqueclique.document._AbstractDocumentLinksEditor");
dojo.require("cliqueclique.document._AbstractDocumentSubjectEditor");
dojo.require("cliqueclique.document._AbstractDocumentForwardEditor");
dojo.require("cliqueclique.document.DocumentSelector");
dojo.require("dijit.form.TextBox");
dojo.require("dijit.Editor");

dojo.declare(
  "cliqueclique.ui.modules.DocumentForwardEditor",
  [cliqueclique.document._AbstractDocumentEditor,
   cliqueclique.document._AbstractDocumentSubjectEditor,
   cliqueclique.document._AbstractDocumentLinksEditor,
   cliqueclique.document._AbstractDocumentForwardEditor], {});

cliqueclique.ui.modules.DocumentForwardEditor.register = function (widget) {
  widget.registerData("documentLink",
		      {label: 'Forward',
		       load:function (document) {
			 var docEdit = new cliqueclique.ui.modules.DocumentForwardEditor({title: 'Forward document'});
			 docEdit.forwardDocSet(document);
			 widget.getDataDefault("panels").addChild(docEdit);
		       }},
		       false,
		       "cliqueclique.document.DocumentLink");

};
