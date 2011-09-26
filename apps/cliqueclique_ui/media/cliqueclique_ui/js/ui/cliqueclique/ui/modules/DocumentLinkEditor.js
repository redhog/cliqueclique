dojo.provide("cliqueclique.ui.modules.DocumentLinkEditor");

dojo.require("cliqueclique.ui");
dojo.require("cliqueclique.document.DocumentSelector");
dojo.require("dijit.form.CheckBox");

dojo.declare("cliqueclique.ui.modules.DocumentLinkEditor", [cliqueclique.document.BaseDocumentEditor], {
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
  commentToAdd: function (document) {
    this.editWidgetLink.commentTo.addLink(document);
  },
  commentInAdd: function (document) {
    this.editWidgetLink.commentIn.addLink(document);
  }
});

cliqueclique.ui.modules.DocumentLinkEditor.register = function (widget) {
  widget.registerData("documentLink",
		      {label: 'Add as comment to existing',
		       load:function (document) {
			 var docEdit = new cliqueclique.ui.modules.DocumentLinkEditor({title: 'New comment'});
			 docEdit.commentInAdd(document);
			 widget.getDataDefault("panels").addChild(docEdit);
		       }},
		       false,
		       "cliqueclique.document.DocumentLink");
  widget.registerData("documentLink",
		      {label: 'Add existing as comment',
		       load:function (document) {
			 var docEdit = new cliqueclique.ui.modules.DocumentLinkEditor({title: 'New comment'});
			 docEdit.commentToAdd(document);
			 widget.getDataDefault("panels").addChild(docEdit);
		       }},
		       false,
		       "cliqueclique.document.DocumentLink");
};
