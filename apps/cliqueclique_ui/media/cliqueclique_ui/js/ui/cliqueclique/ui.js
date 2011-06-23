dojo.provide("cliqueclique.ui");

dojo.require("cliqueclique.document.tree");
dojo.require("cliqueclique.document.selector");
dojo.require("cliqueclique.document.editor");
dojo.require("cliqueclique.document.DocumentView");
dojo.require("cliqueclique.document.DocumentGraphView");
dojo.require("cliqueclique.document.DocumentStatView");
dojo.require("cliqueclique.document.DocumentInfoView");
dojo.require("cliqueclique.document.Document");
dojo.require("cliqueclique.nodeinfo");
dojo.require("dijit.layout.BorderContainer");
dojo.require("dijit.layout.ContentPane");
dojo.require("dijit.layout.AccordionContainer");
dojo.require("dijit.layout.TabContainer");
dojo.require("dojox.layout.TableContainer");

dojo.require("dijit._base.popup");
dojo.require("dojo.html");
dojo.require("cliqueclique.general.OptionalTabContainer");


dojo.require('dijit.MenuBar');
dojo.require('dijit.PopupMenuBarItem');
dojo.require('dijit.MenuItem');
dojo.require('dijit.Menu');

dojo.declare("cliqueclique.ui.TopMenu", [dijit.MenuBar], {
  startup: function () {
    var menu = this;
    var item;
    var submenu;

    submenu = new dijit.Menu();
    item = new dijit.MenuItem({label:"Import"});
    submenu.addChild(item);
    item = new dijit.MenuItem({label:"Test X"});
    submenu.addChild(item);

    item = new dijit.PopupMenuBarItem({label:"File", popup: submenu});
    menu.addChild(item);
    item = new dijit.MenuBarItem({label:"Help"});
    menu.addChild(item);
    // item.connect(item, 'onClick', function (e) { item.load(tn.item); });

    this.inherited(arguments);
  }
});


dojo.declare("cliqueclique.ui.Ui", [dijit.layout.BorderContainer], {
  design:'sidebar',
  style:'border: 0px; height: 100%; width: 100%;',
  gutters: false,
  startup: function () {
    this.inherited(arguments);

    var ui = this;

    ui.menu = new cliqueclique.ui.TopMenu({region: 'top'});
    ui.addChild(ui.menu);

    ui.inner = new dijit.layout.BorderContainer({region: 'center', gutters: false, design: 'sidebar'});
    ui.addChild(ui.inner);

    ui.leftPane = new dijit.layout.AccordionContainer({region: 'left', splitter: true, minSize: 200});
    ui.inner.addChild(ui.leftPane);

    ui.tree = new dijit.Tree({showRoot: false, model: cliqueclique.document.tree.DocumentTreeModel(), style: "width: 200px;", title: 'Bookmarks'});
    ui.leftPane.addChild(ui.tree);
    ui.tree.connect(ui.tree, 'onClick', function (item, node, evt) { item.getDocumentLink(ui.tree)(); });

    ui.menu = new cliqueclique.document.DocumentMenu({});
    ui.menu.startup();
    ui.menu.bindDomNode(ui.tree.domNode);

    ui.docView = cliqueclique.document.DocumentView({region: 'center'});
    ui.inner.addChild(ui.docView);
    ui.registerData("documentLink", {label: 'Display', load:function (document) { return ui.docView.attr("document", document); }}, true, "cliqueclique.document.DocumentLink");

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

    ui.registerData("documentLink",
		    {label: 'Comment',
		     load:function (document) {
		       var docEdit = new cliqueclique.document.editor.DocumentEditor({title: 'New comment'});
		       docEdit.commentToAdd(document);
		       ui.getDataDefault("panels").addChild(docEdit);
		     }},
                     false,
                     "cliqueclique.document.DocumentLink");
    ui.registerData("documentLink",
		    {label: 'Graph',
		     load:function (document) {
		       var docGraph = new cliqueclique.document.DocumentGraphView({document: document});
		       ui.getDataDefault("panels").addChild(docGraph);
		     }},
                     false,
                     "cliqueclique.document.DocumentLink");
    ui.registerData("documentLink",
		    {label: 'Stat',
		     load:function (document) {
		       var docStat = new cliqueclique.document.DocumentStatView({document: document});
		       ui.getDataDefault("panels").addChild(docStat);
		     }},
                     false,
                     "cliqueclique.document.DocumentLink");
    ui.registerData("documentLink",
		    {label: 'Info',
		     load:function (document) {
		       var docInfo = new cliqueclique.document.DocumentInfoView({document: document});
		       ui.getDataDefault("panels").addChild(docInfo);
		     }},
                     false,
                     "cliqueclique.document.DocumentLink");
  }
});
