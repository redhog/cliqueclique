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

    ui.leftPane = new dijit.layout.AccordionContainer({region: 'left', splitter: true, minSize: 200});
    ui.inner.addChild(ui.leftPane);

    ui.tree = new dijit.Tree({showRoot: false, model: cliqueclique.document.DocumentTreeModel(), style: "width: 200px;", title: 'Bookmarks'});
    ui.leftPane.addChild(ui.tree);
    ui.tree.connect(ui.tree, 'onClick', function (item, node, evt) { item.getDocumentLink(ui.tree)(); });

    ui.menu = new cliqueclique.document.DocumentMenu({});
    ui.menu.startup();
    ui.menu.bindDomNode(ui.tree.domNode);

    ui.tabCon = cliqueclique.general.OptionalTabContainer({region:'bottom', splitter: true, style:'height: 30%;'});        
    ui.inner.addChild(ui.tabCon);
    ui.tabCon.updateVisibility();

    ui.registerData("panels",
		    {label: 'Bottom pane',
		     addChild: function (widget) {
		       widget.attr("closable", true);
		       widget.attr("style", 'height:100%; overflow: auto;');
		       ui.tabCon.addChild(widget);
		     }},
                     true);

    cliqueclique.ui.modules.register(ui);
  }
});
