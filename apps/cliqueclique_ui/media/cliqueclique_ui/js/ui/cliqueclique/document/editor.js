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
     console.log("hej");
   },
   post: function () {
     var res = {"__smime_MIMESigned__": true,
		"header": {},
		"parts": [{"__email_mime_multipart_MIMEMultipart__": true,
			   "parts": [{"__email_message_Message__": true,
				      "body": "",
				      "header": {"part_type": "content",
						 "Content-Type": "text/plain; charset=\"us-ascii\""}}],
			   "header": {"child_document_id": "22c49a3f440cefffee5b0183fdbdea365d39a4eebc65d1c4029e4",
				      "parent_document_id": "74f0b3f760a9a2345302d3af0be756fb2a3a7569e9ebd60f8e1b2",
				      "name": "link1"}}]}

   },
   commentToAdd: function (document) {
     this.commentTo.addLink(document);
   },
   commentInAdd: function (document) {
     this.commentIn.addLink(document);
   }
});
