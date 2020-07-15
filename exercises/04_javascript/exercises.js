function keywordusage(text, keywords){
  var splitted = text.split(" ");
  var res = [];
  var found;

  for (var word in keywords){
    found = false;
    for (var w in splitted){
      if(keywords[word] === splitted[w]){
        found = true;
      }
    }
    res.push(found);
  }

  return res;
}

function frequencies(text, wordlist){
  var splitted = text.split(" ");
  var res = {};
  var cnt;

  for(var word in wordlist){
    cnt = 0;
    for (var w in splitted){
      if(wordlist[word] == splitted[w]){
        cnt++;
      }
    }
    res[wordlist[word]] = cnt;
  }

  return res;
}

function rotate(array, steps){

  if(typeof(steps) === 'undefined'){
    steps = 1;
  }

  var tmp;
  var new_pos;
  var len = array.length;
  var i;

  if(steps > 0){

    for (i=0; i<steps; i++){
      tmp = array.slice();
      for (var elem in array){
        new_pos = (+elem+1);
        if(new_pos >= len){
          new_pos = 0;
        }
        tmp[new_pos] = array[elem];
      }
      array = tmp.slice();
    }

  }else if(steps < 0){

    var max = (-1)*steps;

    for (i=0; i<max; i++){
      tmp = array.slice();
      for (var elem in array){
        new_pos = (+elem-1);
        if(new_pos < 0){
          new_pos = len-1;
        }
        tmp[new_pos] = array[elem];
      }
      array = tmp.slice();
    }
  }

  var res = array.slice();

  return res;
}

//console.log(rotate([1, 2, 3, 4]));
