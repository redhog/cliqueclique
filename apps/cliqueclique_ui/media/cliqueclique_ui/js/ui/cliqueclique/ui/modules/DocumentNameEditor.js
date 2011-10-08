dojo.provide("cliqueclique.ui.modules.DocumentNameEditor");

dojo.require("cliqueclique.ui");
dojo.require("cliqueclique.document.DocumentSelector");
dojo.require("cliqueclique.document._AbstractDocumentEditor");
dojo.require("cliqueclique.document._AbstractDocumentNameEditor");
dojo.require("cliqueclique.document._AbstractDocumentSubjectEditor");
dojo.require("dijit.form.CheckBox");

dojo.declare(
  "cliqueclique.ui.modules.DocumentNameEditor",
  [cliqueclique.document._AbstractDocumentEditor,
   cliqueclique.document._AbstractDocumentNameEditor,
   cliqueclique.document._AbstractDocumentSubjectEditor], {});

cliqueclique.ui.modules.DocumentNameEditor.register = function (widget) {
  widget.registerData("documentLink",
		      {label: 'Publish in a directory',
		       load:function (document) {
			 var docEdit = new cliqueclique.ui.modules.DocumentNameEditor({title: 'Publish in a directory'});
			 docEdit.toPublishSet(document);
			 widget.getDataDefault("panels").addChild(docEdit);
		       }},
		       false,
		       "cliqueclique.document.DocumentLink");
};
