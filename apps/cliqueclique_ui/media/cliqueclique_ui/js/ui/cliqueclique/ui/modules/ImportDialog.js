dojo.provide("cliqueclique.ui.modules.ImportDialog");

dojo.require("cliqueclique.general.Dialog");
dojo.require('dijit._Widget');
dojo.require('dijit._Templated');

dojo.declare("cliqueclique.ui.modules.ImportDialog", [cliqueclique.general.Dialog], {
  title: "Import document",
  postCreate: function () {
    this.inherited(arguments);
    this.attr("content", new cliqueclique.ui.modules.ImportDialog._ImportDialogContent());    
  }
});

dojo.declare("cliqueclique.ui.modules.ImportDialog._ImportDialogContent", [dijit._Widget, dijit._Templated], {
  widgetsInTemplate: true,
  templateString: "" +
    "<b>Some content should go here</b>"
});

cliqueclique.ui.modules.ImportDialog.register = function (widget) {
  widget.importDialog = new cliqueclique.ui.modules.ImportDialog();
  widget.registerData("actions",
		      {label: 'Import document',
		       perform: function () { widget.importDialog.show(); }},
		      false,
		      "cliqueclique.ui.Ui");
}