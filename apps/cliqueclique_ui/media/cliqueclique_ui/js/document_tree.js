$.fn.documentTree = function (popts) {
  opts = {};
  opts.originalQuery = '"bookmarked"';
  opts.json_data = {};
  opts.json_data.ajax = {};
  opts.json_data.ajax.url = function (n) {
    if (n == -1)
      return "/find/json";
    else
      return "/find/json/" + n.attr("id");	
  };
  opts.json_data.ajax.data = function (n) {
    if (n == -1)
      return { query: opts.originalQuery };
    else
      return { query: '">"' };
  };
  opts.json_data.ajax.success = function (documents) {
    var res = [];
    for (document_id in documents) {
      var doc = Document.instantiate(documents[document_id]);
      res.push({data: {title:doc.getSubject(), attr:{href:document_id}}, attr: { id: document_id }, state: "closed"});
    }
    return res;
  };
  opts.plugins = ["themes", "json_data"];

  for (var name1 in popts) {
    if (name1 == "json_data") {
      for (var name2 in popts.json_data) {
	if (name1 == "ajax") {
	  for (var name3 in popts.json_data) {
	    opts.json_data.ajax[name3] = popts.json_data.ajax[name3];
 	  }
	} else {
	  opts.json_data[name2] = popts.json_data[name2];
	}
      }
    } else if (name1 == "plugins") {
      opts.plugins = opts.plugins.concat(popts.plugins);
    } else {
      opts[name1] = popts[name1];
    }
  }

  return this.jstree(opts);
}
