dojo.provide("cliqueclique.document.editor");

dojo.require("cliqueclique.document.selector");
dojo.require("dijit.form.TextBox");
dojo.require("dijit.Editor");

dojo.declare("cliqueclique.document.editor.DocumentEditor", [dijit._Widget, dijit._Templated], {
  widgetsInTemplate: true,
  templateString: "<div class='cliquecliqueDocumentEditor'>" +
                  "  <div dojoType='dijit.form.Button' dojoAttachEvent='onClick: send' class='sendButton'>Send</div>" +
                  "  <table class='metadata'>" +
                  "    <tr>" +
                  "     <th>Comment to</th>" +
                  "     <td><div dojoType='cliqueclique.document.selector.DocumentSelector' dojoAttachPoint='commentTo'></div></td>" +
                  "    </tr>" +
                  "    <tr>" +
                  "     <th>Has comments in</th>" +
                  "     <td><div dojoType='cliqueclique.document.selector.DocumentSelector' dojoAttachPoint='commentIn'></div></td>" +
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

     var commentTo = this.commentTo.attr("links");
     var commentIn = this.commentIn.attr("links");

     var header = {};
     if (commentTo.length > 0)
       header.parent_document_id = commentTo[0].getDocumentId();
     if (commentIn.length > 0)
       header.child_document_id = commentIn[0].getDocumentId();

     cliqueclique.document.Document.post(
       {
         "__smime_MIMESigned__": true,
	 "header": {},
	 "parts": [{"__email_mime_multipart_MIMEMultipart__": true,
		    "parts": [{"__email_message_Message__": true,
	                       "body": this.content.attr("value"),
			       "header": {"part_type": "content",
	                                  "subject": this.subject.attr("value"),
					  "Content-Type": "text/plain; charset=\"utf-8\""}}],
	            "header": header}]},
       function (document, error) {
	 if (document == null) {
	   console.log(error);
	   return;
	 }
 	 console.log(document);
         document.getDocumentLink(editor)();
       });
   },
   commentToAdd: function (document) {
     this.commentTo.addLink(document);
   },
   commentInAdd: function (document) {
     this.commentIn.addLink(document);
   }
});
