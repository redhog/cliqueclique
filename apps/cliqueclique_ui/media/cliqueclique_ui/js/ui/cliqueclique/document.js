dojo.provide("cliqueclique.document");

dojo.declare("cliqueclique.document.Document", [], {
  constructor: function (json_data) {
    this.json_data = json_data;
  },
  getSubject: function () {
    if (   typeof(this.json_data.content) != "undefined"
	&& typeof(this.json_data.content.parts) != "undefined"
	&& this.json_data.content.parts.length > 0
	&& typeof(this.json_data.content.parts[0].header) != "undefined")
      return this.json_data.content.parts[0].header.subject;
    else
      return this.json_data.document_id.substring(0, 5);
  },
  getDocumentId: function () {
    return this.json_data.document_id;
  }
});
