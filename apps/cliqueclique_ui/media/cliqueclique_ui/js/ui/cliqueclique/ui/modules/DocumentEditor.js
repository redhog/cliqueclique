dojo.provide("cliqueclique.ui.modules.DocumentEditor");

dojo.require("cliqueclique.ui");
dojo.require("cliqueclique.document._AbstractDocumentEditor");
dojo.require("cliqueclique.document._AbstractDocumentLinksEditor");
dojo.require("cliqueclique.document._AbstractDocumentSubjectEditor");
dojo.require("cliqueclique.document._AbstractDocumentContentEditor");
dojo.require("cliqueclique.document.DocumentSelector");
dojo.require("dijit.form.TextBox");
dojo.require("dijit.Editor");

dojo.declare(
  "cliqueclique.ui.modules.DocumentEditor",
  [cliqueclique.document._AbstractDocumentEditor,
   cliqueclique.document._AbstractDocumentSubjectEditor,
   cliqueclique.document._AbstractDocumentLinksEditor,
   cliqueclique.document._AbstractDocumentContentEditor], {});

cliqueclique.ui.modules.DocumentEditor.register = function (widget) {
  widget.registerData("documentLink",
		      {label: 'Comment',
		       load:function (document) {
			 var docEdit = new cliqueclique.ui.modules.DocumentEditor({title: 'New comment'});
			 docEdit.commentsToAdd(document);
			 widget.getDataDefault("panels").addChild(docEdit);
		       }},
		       false,
		       "cliqueclique.document.DocumentLink");

};
