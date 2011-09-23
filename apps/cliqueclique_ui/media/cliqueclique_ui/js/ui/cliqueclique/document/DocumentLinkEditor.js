dojo.provide("cliqueclique.document.DocumentLinkEditor");

dojo.require("cliqueclique.ui");
dojo.require("cliqueclique.document.DocumentSelector");
dojo.require("dijit.form.CheckBox");

dojo.declare("cliqueclique.document.DocumentLinkEditor", [dijit._Widget, dijit._Templated], {
  widgetsInTemplate: true,
  templateString: "<div class='cliquecliqueDocumentEditor'>" +
                  "  <div dojoType='dijit.form.Button' dojoAttachEvent='onClick: send' class='sendButton'>Send</div>" +
                  "  <table class='metadata'>" +
                  "    <tr>" +
                  "     <th>Reverse visibility (comment sees commented)</th>" +
                  "     <td><div dojoType='dijit.form.CheckBox' dojoAttachPoint='reversed'></div></td>" +
                  "    </tr>" +
                  "    <tr>" +
                  "     <th>Comment to</th>" +
                  "     <td><div dojoType='cliqueclique.document.DocumentSelector' single='true' dojoAttachPoint='commentTo'></div></td>" +
                  "    </tr>" +
                  "    <tr>" +
                  "     <th>Has comment in</th>" +
                  "     <td><div dojoType='cliqueclique.document.DocumentSelector' single='true' dojoAttachPoint='commentIn'></div></td>" +
                  "    </tr>" +
                  "    <tr>" +
                  "     <th>Subject</th>" +
                  "     <td><div dojoType='dijit.form.TextBox' dojoAttachPoint='subject'></div></td>" +
                  "    </tr>" +
                  "  </table>" +
                  "</div>",
   _getDocumentAttr: function () {

   },
   send: function () {
     var editor = this;

     console.log([this.commentTo.attr("links")[0], this.commentIn.attr("links")[0]]);
     cliqueclique.document.Document.post_link(this.commentTo.attr("links")[0], this.commentIn.attr("links")[0], function (document, error) {
       if (!document) {
	 console.error(error);
	 return;
       }
       //console.log(document.getDocumentId());
       document.getDocumentLink(editor)();
       editor.getHtmlParent().removeChild(editor);
     }, this.reversed.attr("value"));
   },
   commentToAdd: function (document) {
     this.commentTo.addLink(document);
   },
   commentInAdd: function (document) {
     this.commentIn.addLink(document);
   }
});

cliqueclique.document.DocumentLinkEditor.register = function (widget) {
  widget.registerData("documentLink",
		      {label: 'Add as comment to existing',
		       load:function (document) {
			 var docEdit = new cliqueclique.document.DocumentLinkEditor({title: 'New comment'});
			 docEdit.commentInAdd(document);
			 widget.getDataDefault("panels").addChild(docEdit);
		       }},
		       false,
		       "cliqueclique.document.DocumentLink");
  widget.registerData("documentLink",
		      {label: 'Add existing as comment',
		       load:function (document) {
			 var docEdit = new cliqueclique.document.DocumentLinkEditor({title: 'New comment'});
			 docEdit.commentToAdd(document);
			 widget.getDataDefault("panels").addChild(docEdit);
		       }},
		       false,
		       "cliqueclique.document.DocumentLink");
};
