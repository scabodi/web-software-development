function addPersonMethods(obj){

  var new_obj = {
    name: obj.name,
    age: obj.age,
    greet: function(greetingString){
      var res = greetingString+", my name is "+ this.name;
      console.log(res);
    },
    compareAge: function(other){
      var diff = this.age - other.age;
      var res = "My name is "+this.name+" and I'm ";
      if(diff > 0){
        res += "older than ";

      }else if(diff < 0 ){
        res += "younger than ";
      }else{//equal
        res += "equally young as ";
      }
      res += other.name;

      console.log(res);
    },

    namesake: function(other){
      var res = "We have";
      if(this.name === other.name){
        res += " the same name, "+other.name+" and I!";
      }else{
        res += " different names, "+other.name+" and I.";
      }
      console.log(res);
    }
  }

  return new_obj;
}
