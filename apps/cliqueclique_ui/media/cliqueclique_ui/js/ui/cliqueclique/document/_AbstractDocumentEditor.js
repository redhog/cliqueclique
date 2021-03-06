dojo.provide("cliqueclique.document._AbstractDocumentEditor");

dojo.require("cliqueclique.ui");
dojo.require("cliqueclique.document.DocumentSelector");
dojo.require("dijit.form.TextBox");
dojo.require("dijit.Editor");

dojo.declare("cliqueclique.document._AbstractDocumentEditor", [dijit._Widget, dijit._Templated], {
  widgetsInTemplate: true,
  templateString: "<div class='cliquecliqueDocumentEditor'>" +
                  "  <div dojoType='dijit.form.Button' dojoAttachEvent='onClick: send' class='sendButton'>Send</div>" +
                  "  <table class='metadata' dojoAttachPoint='formMetadata'></table>" +
                  "  <div dojoAttachPoint='formMain'></div>" +
                  "</div>",
  postCreate: function () {
    var res = this.inherited(arguments);

    var editor = this;
    for (var attr in this) {
      if (attr.indexOf("editWidget") == 0 ) {
	var editWidget = new editor[attr]({editor:editor});
	dojo.place(editWidget.domNode, editor[editWidget.placement]);
	editWidget.startup();
	editor[attr] = editWidget;
      }
    }
    return res;
  },
  send: function () {
    var editor = this;

    var doc = new cliqueclique.document.NewDocument();

    for (var attr in this) {
      if (attr.indexOf("editWidget") == 0) {
	editor[attr].send(doc);
      }
    }

    var callback = function (data) {
      data.document.getDocumentLink(editor)();
      editor.getHtmlParent().removeChild(editor);
    }

    if (editor.getDocument !== undefined) {
      doc.callPostHooks(editor.getDocument(), callback);
    } else {
      doc.post(callback);
    }
  },
});
