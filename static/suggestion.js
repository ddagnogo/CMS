function remplacerAccentues(chaine){
var accentue = "àâçéèêîôû";
var sansaccent = "aaceeeiou";
var result = "";
  for(var i = 0; i < chaine.length; i++){
    if(/[àâçéèêîôû]/.test(chaine.charAt(i))){
      var k = accentue.indexOf(chaine.charAt(i));
        result = result.concat(sansaccent.charAt(k));
    }
    else
     {
    
      result = result.concat(chaine.charAt(i));
     }

  }
  return result;

}



function suggerer(){
var titre = document.getElementById("inputTitre").value;
titre = titre.toLowerCase();
titre = remplacerAccentues(titre);
var result = "";
var tab = titre.split(' ');
var tabTitre = tab.join('-');

  for(var i = 0; i < tabTitre.length; i++){
      if(/[a-z0-9 \-]/.test(tabTitre.charAt(i))){
        result = result.concat(tabTitre.charAt(i));
      }
  }

  if(result !== ""){
    var xhr = new XMLHttpRequest();
  
    xhr.onreadystatechange = function(){
    
      if(xhr.readyState === XMLHttpRequest.DONE){
      
        if(xhr.status === 200){
           document.getElementById("suggestion").innerHTML = xhr.responseText;
         }
      }
  
    };

    xhr.open("GET", "/ajax/"+ result, true);
    xhr.send();
  }
}


function verifierModification(){
var modification = document.getElementById("inputIdentifiant").value;

  if(suggestion !== ""){
    var xhr = new XMLHttpRequest();
  
    xhr.onreadystatechange = function(){
    
      if(xhr.readyState === XMLHttpRequest.DONE){
      
        if(xhr.status === 200){
            document.getElementById("errIdentifiant").innerHTML = xhr.responseText;
          
        }
       
      }
  
    };

    xhr.open("GET", "/ajax/modification/"+ modification, true);
    xhr.send();
  }
  
}


