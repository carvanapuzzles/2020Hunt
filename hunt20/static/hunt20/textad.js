// Hey there puzzler! I see you're checking out the js for this puzzle. 
// While you could explore the puzzle this way... 
// ...We think it's a lot more sporting if you just move around as intended :)











// Thanks!











function north() {

    var output = document.getElementById("output");
  
    output.value = output.value + "[move north]";
  
    var test_x_pos = x_pos
    var test_y_pos = y_pos + 0.5
  
    var check_pos = JSON.stringify([test_x_pos,test_y_pos])
  
    if (walls.has(check_pos)){
      output.value = output.value + "\r" + "You try to move north and run into a wall";
      output.value = output.value + "\r" + "You remain at " + JSON.stringify(pos);
    }
    else if (Math.abs(test_x_pos)>2 | Math.abs(test_y_pos)>2){
      output.value = output.value + "\r" + "Moving north would take you out of Area 51! You don't want to leave so you remain at " + JSON.stringify(pos);
    }
    else {
      y_pos = y_pos + 1 
      pos = [x_pos,y_pos]
      output.value = output.value + "\r" + "You are now at " + JSON.stringify(pos);
    }
    check();
  }
  function east() {
  
    var output = document.getElementById("output");
  
    output.value = output.value + "[move east]";
  
    var test_x_pos = x_pos + 0.5
    var test_y_pos = y_pos
  
    var check_pos = JSON.stringify([test_x_pos,test_y_pos])
    if (walls.has(check_pos)){
      output.value = output.value + "\r" + "You try to move east and run into a wall";
      output.value = output.value + "\r" + "You remain at " + JSON.stringify(pos);
    }
    else if (Math.abs(test_x_pos)>2 | Math.abs(test_y_pos)>2){
      output.value = output.value + "\r" + "Moving east would take you out of Area 51! You don't want to leave so you remain at " + JSON.stringify(pos);
    }
    else {
      x_pos = x_pos + 1 
      pos = [x_pos,y_pos]
      output.value = output.value + "\r" + "You are now at " + JSON.stringify(pos);
    }
    check();
  }
  function south() {
  
    var output = document.getElementById("output");
  
    output.value = output.value + "[move south]";
  
    var test_x_pos = x_pos
    var test_y_pos = y_pos - 0.5
  
    var check_pos = JSON.stringify([test_x_pos,test_y_pos])
  
    if (walls.has(check_pos)){
      output.value = output.value + "\r" + "You try to move south and run into a wall";
      output.value = output.value + "\r" + "You remain at " + JSON.stringify(pos);
    }
    else if (Math.abs(test_x_pos)>2 | Math.abs(test_y_pos)>2){
      output.value = output.value + "\r" + "Moving south would take you out of Area 51! You don't want to leave so you remain at " + JSON.stringify(pos);
    }
    else {
      y_pos = y_pos - 1 
      pos = [x_pos,y_pos]
      output.value = output.value + "\r" + "You are now at " + JSON.stringify(pos);
    }
    check();
  }
  function west() {
  
    var output = document.getElementById("output");
  
    output.value = output.value + "[move west]";
    
    var test_x_pos = x_pos - 0.5
    var test_y_pos = y_pos
  
    var check_pos = JSON.stringify([test_x_pos,test_y_pos])
  
    if (walls.has(check_pos)){
      output.value = output.value + "\r" + "You try to move west and run into a wall";
      output.value = output.value + "\r" + "You remain at " + JSON.stringify(pos);
    }
    else if (Math.abs(test_x_pos)>2 | Math.abs(test_y_pos)>2){
      output.value = output.value + "\r" + "Moving west would take you out of Area 51! You don't want to leave so you remain at " + JSON.stringify(pos);
    }
    else {
      x_pos = x_pos - 1 
      pos = [x_pos,y_pos]
      output.value = output.value + "\r" + "You move west";
      output.value = output.value + "\r" + "You are now at " + JSON.stringify(pos);
    }
    check();
  }
  
  function check(){
    var output = document.getElementById("output");
    var content = document.getElementById("cluespace")
    console.log("CHECK")
    if (JSON.stringify(pos) in clues){
      console.log("Show me")
      output.value = output.value + "\r" + "You find a research snippet on the ground -->"
      content.innerHTML = "NOTE: " + clues[JSON.stringify(pos)];
    }
    else if (JSON.stringify(pos) in images){
      console.log("Show me 2")
      output.value = output.value + "\r" + "You find a relic the government left behind -->"
      content.innerHTML = images[JSON.stringify(pos)];
    }
    else {
      content.innerHTML = ""
    }
    moves = moves+1
    output.value = output.value + "\r" + ">>[" +moves +"] Awaiting move...";
    output.scrollTop = output.scrollHeight;
  }
  
  function launch() {
    var output = document.getElementById("output");
  
    output.value = '';
    moves = 0 ;
    x_pos = 0 ;
    y_pos = 0 ;
    pos = [x_pos,y_pos]
    
    walls = new Set([
    ])
  
    clues = {}
    clues[JSON.stringify([-2,-2])] = "The being was a fan of borscht vegetables"
    clues[JSON.stringify([0,-1])] = "The being arrived with many ships"
    clues[JSON.stringify([2,-2])] = "The being did not make any noises"

  
    images = {}
    images[JSON.stringify([-2,2])] = "<img src='/static/hunt20/p04/tt_51_1.jpg' class='img-fluid'>"
    images[JSON.stringify([0,1])] = "<img src='/static/hunt20/p04/tt_51_2.jpg' class='img-fluid'>"
    images[JSON.stringify([1,2])] = "<img src='/static/hunt20/p04/tt_51_3.jpg' class='img-fluid'>"

  
  
    output.value = ">>[0] Awaiting move...";
  }
  
  window.onload = function(){
    launch();
  }