dojo.provide("cliqueclique.document._AbstractDocumentViewBodyType");

dojo.require("cliqueclique.document._AbstractDocumentViewBody");

dojo.declare("cliqueclique.ui.modules._AbstractDocumentViewBodyType", [cliqueclique.document._AbstractDocumentViewBody], {
  widgetsInTemplate: true,
  templateString: "<div dojoAttachPoint='body'></div>",
});
