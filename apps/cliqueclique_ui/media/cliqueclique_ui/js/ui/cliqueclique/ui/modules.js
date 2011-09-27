dojo.provide("cliqueclique.ui.modules");

dojo.require("cliqueclique.ui.modules.TopMenu");
dojo.require("cliqueclique.ui.modules.LeftTree");
dojo.require("cliqueclique.ui.modules.BottomPane");
dojo.require("cliqueclique.ui.modules.ImportDialog");
dojo.require("cliqueclique.ui.modules.DocumentView");
dojo.require("cliqueclique.ui.modules.DocumentEditor");
dojo.require("cliqueclique.ui.modules.DocumentLinkEditor");
dojo.require("cliqueclique.ui.modules.DocumentGraphView");
dojo.require("cliqueclique.ui.modules.DocumentStatView");
dojo.require("cliqueclique.ui.modules.DocumentInfoView");

cliqueclique.ui.modules.register = function (ui) {
  cliqueclique.ui.modules.TopMenu.register(ui);
  cliqueclique.ui.modules.LeftTree.register(ui);
  cliqueclique.ui.modules.BottomPane.register(ui);
  cliqueclique.ui.modules.ImportDialog.register(ui);
  cliqueclique.ui.modules.DocumentView.register(ui);
  cliqueclique.ui.modules.DocumentEditor.register(ui);
  cliqueclique.ui.modules.DocumentLinkEditor.register(ui);
  cliqueclique.ui.modules.DocumentGraphView.register(ui);
  cliqueclique.ui.modules.DocumentStatView.register(ui);
  cliqueclique.ui.modules.DocumentInfoView.register(ui);
}
