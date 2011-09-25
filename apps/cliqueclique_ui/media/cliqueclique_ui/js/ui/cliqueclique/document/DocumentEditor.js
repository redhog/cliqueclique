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

     var doc = cliqueclique.document.NewDocument();
     var content = doc.getContent();
     content.header.subject = this.subject.attr("value");
/*
     content.header.parent_document_id = xyzzy.getDocumentId();
     content.header.child_document_id = xyzzy.getDocumentId();
*/
     var part = doc.createPart("content", "__email_message_Message__", "text/plain; charset=\"utf-8\"");
     part.body = this.content.attr("value");

     dojo.forEach(links, function (link) {
       dojo.forEach(link.items, function (item) {
	 doc.addPostHook(function (data, next_hook) {
	   var params = {document: data.document, item: item}
	   var link_doc = cliqueclique.document.NewDocument();
	   link_doc.makeLink(params[link.src], params[link.dst], link.reversed);
	   link_doc.post(function(link_data) {
	     if (data.links === undefined) data.links = [];
	     data.links.push(link_data);
             next_hook(data);
	   });
         });
       });
     });

     doc.post(
       function (data) {
	 data.document.getDocumentLink(editor)();
	 editor.getHtmlParent().removeChild(editor);
       },
       function (error) { console.error(error); });
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
