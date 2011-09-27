dojo.provide("cliqueclique.ui.Ui");

dojo.require("cliqueclique.document.DocumentTreeModel");
dojo.require("cliqueclique.ui.modules");
dojo.require("cliqueclique.document.Document");
dojo.require("cliqueclique.general.nodeinfo");
dojo.require("dijit.layout.BorderContainer");
dojo.require("dijit.layout.ContentPane");
dojo.require("dijit.layout.AccordionContainer");
dojo.require("dijit.layout.TabContainer");
dojo.require("dojox.layout.TableContainer");

dojo.require("dijit._base.popup");
dojo.require("dojo.html");
dojo.require("cliqueclique.general.OptionalTabContainer");

dojo.declare("cliqueclique.ui.Ui", [dijit.layout.BorderContainer], {
  design:'sidebar',
  style:'border: 0px; height: 100%; width: 100%;',
  gutters: false,
  startup: function () {
    this.inherited(arguments);

    var ui = this;

    ui.inner = new dijit.layout.BorderContainer({region: 'center', gutters: false, design: 'sidebar'});
    ui.addChild(ui.inner);

    cliqueclique.ui.modules.register(ui);
  }
});
