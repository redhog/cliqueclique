dojo.provide("cliqueclique.ui.modules.DocumentLinkEditor");

dojo.require("cliqueclique.ui");
dojo.require("cliqueclique.document.DocumentSelector");
dojo.require("cliqueclique.document._AbstractDocumentEditor");
dojo.require("cliqueclique.document._AbstractDocumentLinkEditor");
dojo.require("dijit.form.CheckBox");

dojo.declare(
  "cliqueclique.ui.modules.DocumentLinkEditor",
  [cliqueclique.document._AbstractDocumentEditor,
   cliqueclique.document._AbstractDocumentLinkEditor], {});

cliqueclique.ui.modules.DocumentLinkEditor.register = function (widget) {
  widget.registerData("documentLink",
		      {label: 'Add as comment to existing',
		       load:function (document) {
			 var docEdit = new cliqueclique.ui.modules.DocumentLinkEditor({title: 'New comment'});
			 docEdit.commentInSet(document);
			 widget.getDataDefault("panels").addChild(docEdit);
		       }},
		       false,
		       "cliqueclique.document.DocumentLink");
  widget.registerData("documentLink",
		      {label: 'Add existing as comment',
		       load:function (document) {
			 var docEdit = new cliqueclique.ui.modules.DocumentLinkEditor({title: 'New comment'});
			 docEdit.commentToSet(document);
			 widget.getDataDefault("panels").addChild(docEdit);
		       }},
		       false,
		       "cliqueclique.document.DocumentLink");
};
