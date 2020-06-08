function one() {
    var output = document.getElementById("output");
    user_inputs = user_inputs + '1'
    
    $.ajax({
        type: 'GET',
        url: "/insanitycheck",
        data: {
          'inputs': user_inputs
        },
        dataType: 'json',
        success: function (data) {
          output.innerHTML = data.output;
        }
      })
    }

function two() {
    var output = document.getElementById("output");
    user_inputs = user_inputs + '2'
    
    $.ajax({
        type: 'GET',
        url: "/insanitycheck",
        data: {
          'inputs': user_inputs
        },
        dataType: 'json',
        success: function (data) {
          output.innerHTML = data.output;
        }
      })
    }
function three() {
    var output = document.getElementById("output");
    user_inputs = user_inputs + '3'
    
    $.ajax({
        type: 'GET',
        url: "/insanitycheck",
        data: {
          'inputs': user_inputs
        },
        dataType: 'json',
        success: function (data) {
          output.innerHTML = data.output;
        }
      })
    }
function four() {
    var output = document.getElementById("output");
    user_inputs = user_inputs + '4'
    
    $.ajax({
        type: 'GET',
        url: "/insanitycheck",
        data: {
          'inputs': user_inputs
        },
        dataType: 'json',
        success: function (data) {
          output.innerHTML = data.output;
        }
      })
    }
function five() {
    var output = document.getElementById("output");
    user_inputs = user_inputs + '5'
    
    $.ajax({
        type: 'GET',
        url: "/insanitycheck",
        data: {
          'inputs': user_inputs
        },
        dataType: 'json',
        success: function (data) {
          output.innerHTML = data.output;
        }
      })
    }
function six() {
    var output = document.getElementById("output");
    user_inputs = user_inputs + '6'
    
    $.ajax({
        type: 'GET',
        url: "/insanitycheck",
        data: {
          'inputs': user_inputs
        },
        dataType: 'json',
        success: function (data) {
          output.innerHTML = data.output;
        }
      })
    }

function launch() {
    var output = document.getElementById("output");
    
    output.innerHTML = '';
    user_inputs = ''
}

window.onload = function(){
    launch();
  }