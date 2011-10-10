dojo.provide("cliqueclique.ui.modules.DocumentViewAttributes");

dojo.require("cliqueclique.document._AbstractDocumentView");
dojo.require("dijit.form.CheckBox");

dojo.declare("cliqueclique.ui.modules.DocumentViewAttributes", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
  widgetsInTemplate: true,
  templateString: "" +
    "<div class='actionBox'>" +
    "  <input dojoType='dijit.form.CheckBox' dojoAttachPoint='bookmarkedInput' dojoAttachEvent='onClick:onBookmarkedInputClick'></input><label dojoAttachPoint='bookmarkedLabel'>bookmarked</label>" +
    "  <input dojoType='dijit.form.CheckBox' dojoAttachPoint='readInput' dojoAttachEvent='onClick:onReadInputClick'></input><label dojoAttachPoint='readLabel'>read</label>" +
    "  <input dojoType='dijit.form.CheckBox' dojoAttachPoint='subscribedInput' dojoAttachEvent='onClick:onSubscribedInputClick'></input><label dojoAttachPoint='subscribedInput'>subscribed</label><br>" +
    "  Download: <a dojoAttachPoint='downloadAsMime' target='_new'>as mime</a> or <a dojoAttachPoint='downloadAsJson' target='_new'>as json</a>" +
    "</div>",
  _setDocumentAttr: function (document) {
    var documentView = this;
    this.inherited(arguments);

    if (!this.item.json_data.read) {
      this.item.setAttribute("read", true);
    }

    this.downloadAsMime.href = "/find/mime/" + this.item.getDocumentId();
    this.downloadAsJson.href = "/find/json/" + this.item.getDocumentId();

    this.bookmarkedInput.attr("value", this.item.json_data.bookmarked);
    this.readInput.attr("value", this.item.json_data.read);
    this.subscribedInput.attr("value", this.item.json_data.local_is_subscribed);
  },
  onBookmarkedInputClick: function () {
   this.item.setAttribute("bookmarked");
  },
  onReadInputClick: function () {
   this.item.setAttribute("read");
  },
  onSubscribedInputClick: function () {
   this.item.setAttribute("local_is_subscribed");
  }
});

cliqueclique.ui.modules.DocumentViewAttributes.register = function (widget) {
  widget.registerData("documentView",
                      {load:function (documentView, document) {
			if (!document) return;
		        var subView = new cliqueclique.ui.modules.DocumentViewAttributes({document: document});
			dojo.place(subView.domNode, documentView.header);
		      }},
		      false,
		      "cliqueclique.ui.modules.DocumentView");
};
