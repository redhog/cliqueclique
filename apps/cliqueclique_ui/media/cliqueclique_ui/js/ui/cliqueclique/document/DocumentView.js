dojo.provide("cliqueclique.document.DocumentView");

dojo.require("cliqueclique.document.Document");
dojo.require("cliqueclique.document._AbstractDocumentView");
dojo.require("cliqueclique.document.DocumentLink");
dojo.require("cliqueclique.document.DocumentMenu");
dojo.require("cliqueclique.document.DocumentGraphView");

dojo.declare("cliqueclique.document.DocumentView", [dijit._Widget, dijit._Templated, cliqueclique.document._AbstractDocumentView], {
  templateString: "" +
    "<div>" +
    "  <table>" +
    "    <tr>" +
    "      <th colspan='2' dojoAttachPoint='title'></td>" +
    "    </tr>" +
    "    <tr>" +
    "      <th>Parents:</th>" +
    "      <td dojoAttachPoint='parentDocuments'></td>" +
    "    </tr>" +
    "    <tr>" +
    "      <th>Children:</th>" +
    "      <td dojoAttachPoint='childDocuments'></td>" +
    "    </tr>" +
    "    <tr>" +
    "      <th>Actions:</th>" +
    "      <td>" +
    "        <a dojoAttachPoint='graph' target='_new' dojoAttachEvent='onclick:onGraphClick' href='javascript:void(0);'>Graph</a>" +
    "	     <a dojoAttachPoint='stat' target='_new'>Stat</a>" +
    "      </td>" +
    "    </tr>" +
    "  </table>" +
    "  <p dojoAttachPoint='body'></p>" +
    "</div>",

  postCreate: function () {
    var res = this.inherited(arguments);
    var menu = new cliqueclique.document.DocumentMenu({});
    menu.startup();
    menu.bindDomNode(this.title);

    return res;
  },
  _setDocumentAttr: function (document) {
    var documentView = this;
    this.inherited(arguments);
    dojo.html.set(this.title, this.item.getSubject());
    dojo.html.set(this.body, this.item.getBody());
//    this.graph.href = "/" + this.item.getDocumentId() +  "/graph";
    this.stat.href = "/" + this.item.getDocumentId() +  "/stat";

    dojo.query('> *', documentView.childDocuments).forEach(function(domNode, index, arr){
      dijit.byNode(domNode).destroyRecursive();
    });

    cliqueclique.document.Document.find(function (children) {
      dojo.forEach(children, function (child) {
        var link = new cliqueclique.document.DocumentLink({document: child});
        dojo.place(link.domNode, documentView.childDocuments);
      });
    }, ">", this.item.getDocumentId());


    dojo.query('> *', documentView.parentDocuments).forEach(function(domNode, index, arr){
      dijit.byNode(domNode).destroyRecursive();
    });

    cliqueclique.document.Document.find(function (parents) {
      dojo.forEach(parents, function (parent) {
        var link = new cliqueclique.document.DocumentLink({document: parent});
        dojo.place(link.domNode, documentView.parentDocuments);
      });
    }, "<", this.item.getDocumentId());

  },
  onGraphClick: function () {
   var docGraph = new cliqueclique.document.DocumentGraphView({document: this.item});
    this.getDataDefault("panels", "cliqueclique.ui.Ui").addChild(docGraph);
  }
});
