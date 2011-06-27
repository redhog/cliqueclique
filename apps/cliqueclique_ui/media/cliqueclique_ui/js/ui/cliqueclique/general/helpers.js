dojo.provide("cliqueclique.general.helpers");

cliqueclique.general.helpers.splitWithQuotes = function (text, sep) {
  var quoteTokens = text.split('"');
  var tokens = [];
  
  for (var i = 0; i < quoteTokens.length; i++) {
    var quoteToken = quoteTokens[i];
    if (i % 2 == 0) {
      var partTokens = quoteToken.split(sep);
      if (i > 0 && partTokens[0] == '')
        partTokens.splice(0, 1);
      tokens.push.apply(tokens, partTokens);
    } else {
      tokens[tokens.length-1] += quoteToken;
    }
  }

  return tokens;
}
