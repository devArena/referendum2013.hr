function draw_piechart(data, svg) {
  $(svg[0]).empty();

  var width = 300,
    height = 300,
    radius = Math.min(width, height) / 2;

  var total_votes = data[0].value + data[1].value;

  var color_za = d3.rgb(55, 148, 48);
  var color_protiv = d3.rgb(241, 27, 27);
  var color_prazno = d3.rgb(200, 200, 200);

  var svg = svg
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

  var arc_zero = d3.svg.arc()
    .innerRadius(radius - 0.45 * radius)
    .outerRadius(radius - 0.05 * radius)
    .startAngle(0);

  var path_zero = svg.append("path")
    .datum({
      endAngle: 2 * Math.PI
    })
    .attr("fill", color_prazno)
    .attr("d", arc_zero)
    .classed("prazan");

  if (total_votes >= 3) {

    var ratio_protiv = data[0].value / total_votes;
    var ratio_za = data[1].value / total_votes;

    var percentage_protiv = Math.round(ratio_protiv * 100);
    var percentage_za = 100 - percentage_protiv;

    var arc = d3.svg.arc()
      .innerRadius(radius - 0.45 * radius)
      .outerRadius(radius - 0.05 * radius);

    var za_arc = svg.append("path")
      .datum({
        startAngle: 2 * Math.PI,
        endAngle: 2 * Math.PI
      })
      .attr("fill", color_za)
      .attr("d", arc)
      .transition()
      .duration(2000)
      .attrTween("d", function (d) {
        var interpolate = d3.interpolate(d.endAngle, ratio_protiv * 2 * Math.PI);
        return function (t) {
          d.endAngle = interpolate(t);
          return arc(d);
        }
      });

    var protiv_arc = svg.append("path")
      .datum({
        startAngle: 0,
        endAngle: 0
      })
      .attr("fill", color_protiv)
      .attr("d", arc)
      .transition()
      .duration(1500)
      .attrTween("d", function (d) {
        var interpolate = d3.interpolate(d.endAngle, ratio_protiv * 2 * Math.PI);
        return function (t) {
          d.endAngle = interpolate(t);
          return arc(d);
        }
      });

    svg.append("text")
      .attr("dy", ".75em")
      .attr("y", -0.15 * radius)
      .attr("x", 0)
      .attr("text-anchor", "middle")
      .attr("font-family", "sans-serif")
      .attr("font-size", "22px")
      .attr("fill", color_za)
      .text("0")
      .transition()
      .duration(2000)
      .tween("text",
        function () {
          var i = d3.interpolate(this.textContent, Math.round(percentage_za));
          return function (t) {
            this.textContent = "ZA " + Math.round(i(t)) + "%";
          };
        });

    svg.append("text")
      .attr("dy", ".75em")
      .attr("y", 0.05 * radius)
      .attr("x", 0)
      .attr("text-anchor", "middle")
      .attr("font-family", "sans-serif")
      .attr("font-size", "22px")
      .attr("fill", color_protiv)
      .text("0")
      .transition()
      .duration(2000)
      .tween("text",
        function () {
          var i = d3.interpolate(this.textContent, Math.round(percentage_protiv));
          return function (t) {
            this.textContent = "PROTIV " + Math.round(i(t)) + "%";
          };
        });

  } else {

    svg.append("text")
      .attr("y", -0.15 * radius)
      .attr("x", 0)
      .attr("text-anchor", "middle")
      .attr("font-family", "sans-serif")
      .attr("font-size", "22px")
      .attr("fill", color_prazno)
      .text("Nema dosta");

    svg.append("text")
      .attr("y", 0.05 * radius)
      .attr("x", 0)
      .attr("text-anchor", "middle")
      .attr("font-family", "sans-serif")
      .attr("font-size", "22px")
      .attr("fill", color_prazno)
      .text("podataka za");

    svg.append("text")
      .attr("y", 0.25 * radius)
      .attr("x", 0)
      .attr("text-anchor", "middle")
      .attr("font-family", "sans-serif")
      .attr("font-size", "22px")
      .attr("fill", color_prazno)
      .text("prijatelje:-(");
  }
}


$(document).ready(function () {
  draw_results();
  init_controls();

  change_btn_vote_style(current_vote);

  change_vote_msg(current_vote);

});

function init_controls() {
  $("#btn_yes").click(function (e) {
    user_vote(1);
  });

  $("#btn_no").click(function (e) {
    user_vote(0);
  });

  $('#btn_yes').hover(function () {
    if (current_vote != 1) {
      $(this).removeClass('btn-default');
      $(this).addClass('btn-success');
    }
  }, function () {
    if (current_vote != 1) {
      $(this).removeClass('btn-success');
      $(this).addClass('btn-default');
    }
  });


  $('#btn_no').hover(function () {
    if (current_vote != 0) {
      $(this).removeClass('btn-default');
      $(this).addClass('btn-danger');
    }
  }, function () {
    if (current_vote != 0) {
      $(this).removeClass('btn-danger');
      $(this).addClass('btn-default');
    }
  });

}

function draw_results() {
  results = jQuery.parseJSON(global_results_raw.replace(/&#39;/g, "\""));
  if (results != -1) {
    draw_aggreated_results_all(results, d3.select("#chart_global_results"));
  }

  friends_results = jQuery.parseJSON(friends_results_raw.replace(/&#39;/g, "\""));
  if (friends_results != -1) {
    draw_aggreated_results_friends(friends_results, d3.select("#chart_friends_results"));

  }
}

function draw_aggreated_results_all(results, chart) {
  var mod_results = [{
    'label': 'protiv',
    'value': 0
  }, {
    'label': 'za',
    'value': 0
  }, ];

  if (results.length >= 1) {
    mod_results[results[0].vote].value = Number(results[0].vote_count);
  }
  if (results.length == 2) {
    mod_results[results[1].vote].value = Number(results[1].vote_count);
  }

  var total_votes_all = mod_results[0].value + mod_results[1].value;
  $('.votes-all').text(total_votes_all);

  draw_piechart(mod_results, chart);
}

function draw_aggreated_results_friends(results, chart) {
  var mod_results = [{
    'label': 'protiv',
    'value': 0
  }, {
    'label': 'za',
    'value': 0
  }, ];

  if (results.length >= 1) {
    mod_results[results[0].vote].value = Number(results[0].vote_count);
  }
  if (results.length == 2) {
    mod_results[results[1].vote].value = Number(results[1].vote_count);
  }

  var total_votes_friends = mod_results[0].value + mod_results[1].value;
  $('.votes-friends').text(total_votes_friends);

  draw_piechart(mod_results, chart);
}


function change_btn_vote_style(vote_value) {
  if (vote_value == 1) {
    $('#btn_yes').removeClass('btn-default');
    $('#btn_yes').addClass('btn-success');

    $('#btn_no').removeClass('btn-danger');
    $('#btn_no').addClass('btn-default');
  } else if (vote_value == 0) {
    $('#btn_no').removeClass('btn-default');
    $('#btn_no').addClass('btn-danger');

    $('#btn_yes').removeClass('btn-success');
    $('#btn_yes').addClass('btn-default');
  } else {
    $('#btn_no').attr('class', 'btn btn-large btn-default');
    $('#btn_yes').attr('class', 'btn btn-large btn-default');
  }
}

function change_vote_msg(vote_value) {
  var note = ' Ako želite možete promijeniti glas. Samo je zadnji glas važeći.';
  if (current_vote == 0)
    $('#vote_message').text('Glasali ste PROTIV!' + note);
  else if (current_vote == 1)
    $('#vote_message').text('Glasali ste ZA!' + note);
  else
    $('#vote_message').text('Još niste dali svoj glas!');
}

function user_vote(vote_value) {

  var data = 'vote=' + vote_value;

  //start the ajax
  $.ajax({
    url: "/vote/",
    type: "POST",
    data: data,
    cache: true,
    success: function (data, textStatus, jqXHR) {
      current_vote = data;
      change_btn_vote_style(current_vote);
      change_vote_msg(current_vote);
      draw_results();
    },
    complete: function (jqXHR, textStatus) {},
    error: function (jqXHR, textStatus, errorThrown) {}
  });
}
