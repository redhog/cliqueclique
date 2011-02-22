dojo.provide("cliqueclique.document.editor");

dojo.require("cliqueclique.document.selector");

dojo.declare("cliqueclique.document.editor.DocumentEditor", [dijit._Widget, dijit._Templated], {
  widgetsInTemplate: true,
  templateString: "<div>" +
                  "  <table>" +
                  "    <tr>" +
                  "     <th>Comment to</th>" +
                  "     <td><div dojoType='cliqueclique.document.selector.DocumentSelector' dojoAttachPoint='commentTo'></div></td>" +
                  "    </tr>" +
                  "    <tr>" +
                  "     <th>Has comments in</th>" +
                  "     <td><div dojoType='cliqueclique.document.selector.DocumentSelector' dojoAttachPoint='commentIn'></div></td>" +
                  "    </tr>" +
                  "  </table>" +
                  "</div>",
   commentToAdd: function (document) {
   },
   commentInAdd: function (document) {
   }
});
