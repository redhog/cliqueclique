dojo.provide("cliqueclique.ui.modules");

dojo.require("cliqueclique.ui.modules.TopMenu");
dojo.require("cliqueclique.ui.modules.LeftTree");
dojo.require("cliqueclique.ui.modules.BottomPane");
dojo.require("cliqueclique.ui.modules.ImportDialog");
dojo.require("cliqueclique.ui.modules.DocumentViewBody");
dojo.require("cliqueclique.ui.modules.DocumentViewAttributes");
dojo.require("cliqueclique.ui.modules.DocumentViewLinks");
dojo.require("cliqueclique.ui.modules.DocumentViewEmpty");
dojo.require("cliqueclique.ui.modules.DocumentView");
dojo.require("cliqueclique.ui.modules.DocumentEditor");
dojo.require("cliqueclique.ui.modules.DocumentLinkEditor");
dojo.require("cliqueclique.ui.modules.DocumentForwardEditor");
dojo.require("cliqueclique.ui.modules.DocumentNameEditor");
dojo.require("cliqueclique.ui.modules.DocumentGraphView");
dojo.require("cliqueclique.ui.modules.DocumentStatView");
dojo.require("cliqueclique.ui.modules.DocumentInfoView");

cliqueclique.ui.modules.register = function (ui) {
  dojo.forEach(
    [cliqueclique.ui.modules.TopMenu,
     cliqueclique.ui.modules.LeftTree,
     cliqueclique.ui.modules.BottomPane,
     cliqueclique.ui.modules.ImportDialog,
     cliqueclique.ui.modules.DocumentViewBody,
     cliqueclique.ui.modules.DocumentViewAttributes,
     cliqueclique.ui.modules.DocumentViewLinks,
     cliqueclique.ui.modules.DocumentViewEmpty,
     cliqueclique.ui.modules.DocumentView,
     cliqueclique.ui.modules.DocumentEditor,
     cliqueclique.ui.modules.DocumentLinkEditor,
     cliqueclique.ui.modules.DocumentForwardEditor,
     cliqueclique.ui.modules.DocumentNameEditor,
     cliqueclique.ui.modules.DocumentGraphView,
     cliqueclique.ui.modules.DocumentStatView,
     cliqueclique.ui.modules.DocumentInfoView],
    function (item, i) {
      item.register(ui)
    }
  );
}
