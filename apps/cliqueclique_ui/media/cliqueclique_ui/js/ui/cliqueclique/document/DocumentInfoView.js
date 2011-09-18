dojo.provide("cliqueclique.document.DocumentInfoView");

dojo.require("cliqueclique.document._AbstractDocumentView");

dojo.declare("cliqueclique.document.DocumentInfoView", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
 templateString: "<div><div style='margin: 2px;' dojoAttachPoint='infoView'></div></div>",
  _setDocumentAttr: function (document) {
    var documentView = this;
    this.inherited(arguments);

    var keys = [];
    for (name in this.item.json_data)
      if (name != "document")
        keys.push(name);
    keys.sort();
    var values = this.item.json_data;
    var data = "";
    dojo.forEach(keys, function (name) { 
      data += name + ": " + dojo.toJson(values[name]) + "<br>";
    });
    dojo.html.set(this.infoView, data);
    this.attr("title", "Info: " + this.item.getSubject());
  }
});

cliqueclique.document.DocumentInfoView.register = function (widget) {
  widget.registerData("documentLink",
		      {label: 'Info',
		       load:function (document) {
			 var docInfo = new cliqueclique.document.DocumentInfoView({document: document});
			 widget.getDataDefault("panels").addChild(docInfo);
		       }},
		       false,
		       "cliqueclique.document.DocumentLink");
};