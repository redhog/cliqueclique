dojo.provide("cliqueclique.ui");

dojo.require("cliqueclique.document.tree");
dojo.require("cliqueclique.document.selector");
dojo.require("cliqueclique.document.editor");
dojo.require("cliqueclique.document");
dojo.require("cliqueclique.nodeinfo");
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
  startup: function () {
    this.inherited(arguments);

    var ui = this;

    ui.leftPane = new dijit.layout.AccordionContainer({region: 'left', splitter: true, minSize: 200});
    ui.addChild(ui.leftPane);

    ui.tree = new dijit.Tree({showRoot: false, model: cliqueclique.document.tree.DocumentTreeModel(), style: "width: 200px;", title: 'Bookmarks'});
    ui.leftPane.addChild(ui.tree);
    ui.tree.connect(ui.tree, 'onClick', function (item, node, evt) { item.getDocumentLink(ui.tree)(); });

    ui.menu = new cliqueclique.document.DocumentMenu({});
    ui.menu.startup();
    ui.menu.bindDomNode(ui.tree.domNode);

    ui.docView = cliqueclique.document.DocumentView({region: 'center'});
    ui.addChild(ui.docView);
    ui.registerData("documentLink", {label: 'Display', load:function (document) { return ui.docView.attr("document", document); }}, true, "cliqueclique.document.DocumentLink");

    ui.tabCon = cliqueclique.general.OptionalTabContainer({region:'bottom', splitter: true, style:'height: 30%;'});        
    ui.addChild(ui.tabCon);
    ui.tabCon.updateVisibility();

    ui.registerData("panels",
		    {label: 'Bottom pane',
		     addChild: function (widget) {
		       widget.attr("closable", true);
		       widget.attr("style", 'height:100%; overflow: auto;');
		       ui.tabCon.addChild(widget);
		     }},
                     true);

    ui.registerData("documentLink",
		    {label: 'Comment',
		     load:function (document) {
		       var docEdit = new cliqueclique.document.editor.DocumentEditor({title: 'New comment'});
		       docEdit.commentToAdd(document);
		       ui.getDataDefault("panels").addChild(docEdit);
		     }},
                     false,
                     "cliqueclique.document.DocumentLink");
  }
});
