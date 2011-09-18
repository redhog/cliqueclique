dojo.provide("cliqueclique.document.DocumentEditor");

dojo.require("cliqueclique.ui");
dojo.require("cliqueclique.document.DocumentSelector");
dojo.require("dijit.form.TextBox");
dojo.require("dijit.Editor");

dojo.declare("cliqueclique.document.DocumentEditor", [dijit._Widget, dijit._Templated], {
  widgetsInTemplate: true,
  templateString: "<div class='cliquecliqueDocumentEditor'>" +
                  "  <div dojoType='dijit.form.Button' dojoAttachEvent='onClick: send' class='sendButton'>Send</div>" +
                  "  <table class='metadata'>" +
                  "    <tr>" +
                  "     <th>Comment to</th>" +
                  "     <td><div dojoType='cliqueclique.document.DocumentSelector' dojoAttachPoint='commentTo'></div></td>" +
                  "     <th>Hidden comment to</th>" +
                  "     <td><div dojoType='cliqueclique.document.DocumentSelector' dojoAttachPoint='commentToHidden'></div></td>" +
                  "    </tr>" +
                  "    <tr>" +
                  "     <th>Has comments in</th>" +
                  "     <td><div dojoType='cliqueclique.document.DocumentSelector' dojoAttachPoint='commentInHidden'></div></td>" +
                  "     <th>Has back-linking comments in</th>" +
                  "     <td><div dojoType='cliqueclique.document.DocumentSelector' dojoAttachPoint='commentIn'></div></td>" +
                  "    </tr>" +
                  "    <tr>" +
                  "     <th>Subject</th>" +
                  "     <td><div dojoType='dijit.form.TextBox' dojoAttachPoint='subject'></div></td>" +
                  "    </tr>" +
                  "  </table>" +
                  "  <div dojoType='dijit.Editor' dojoAttachPoint='content'></div>" +
                  "</div>",
   _getDocumentAttr: function () {

   },
   send: function () {
     var editor = this;

     var links = [{src: "item", dst:"document", reversed: false, items: this.commentTo.attr("links")},
		  {src: "document", dst:"item", reversed: true, items: this.commentToHidden.attr("links")},
		  {src: "document", dst:"item", reversed: false, items: this.commentInHidden.attr("links")},
		  {src: "item", dst:"document", reversed: true, items: this.commentIn.attr("links")}];

     var header = {subject: this.subject.attr("value")};
/*
     header.parent_document_id = xyzzy.getDocumentId();
     header.child_document_id = xyzzy.getDocumentId();
*/

     cliqueclique.document.Document.post(
       {
         "__smime_MIMESigned__": true,
	 "header": {},
	 "parts": [{"__email_mime_multipart_MIMEMultipart__": true,
		    "parts": [{"__email_message_Message__": true,
	                       "body": this.content.attr("value"),
			       "header": {"part_type": "content",
	                                  "Content-Type": "text/plain; charset=\"utf-8\""}}],
	            "header": header}]},
       function (document, error) {
	 if (document == null) {
	   console.error(error);
	   return;
	 }

	 dojo.forEach(links, function (link) {
	   dojo.forEach(link.items, function (item) {
	     var params = {document: document, item: item}
	     cliqueclique.document.Document.post_link(params[link.src], params[link.dst], function (document, error) {
	       if (document == null) {
		 console.error(error);
		 return;
	       }
	     }, link.reversed);
	   });
	 });

         document.getDocumentLink(editor)();
	 editor.getHtmlParent().removeChild(editor);
       });
   },
   commentToAdd: function (document) {
     this.commentTo.addLink(document);
   },
   commentInAdd: function (document) {
     this.commentIn.addLink(document);
   }
});

cliqueclique.document.DocumentEditor.register = function (widget) {
  widget.registerData("documentLink",
		      {label: 'Comment',
		       load:function (document) {
			 var docEdit = new cliqueclique.document.DocumentEditor({title: 'New comment'});
			 docEdit.commentToAdd(document);
			 widget.getDataDefault("panels").addChild(docEdit);
		       }},
		       false,
		       "cliqueclique.document.DocumentLink");

};
