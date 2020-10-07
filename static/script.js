// get data to use in chart
/*var res = fetch('/albm_avg_data')
  .then((response) => {
    return response.json();
  }).then(data => {
    console.log('GET response as JSON:');
    console.log(data);
  }).catch(err => {
    console.log("Error: " + err)
  });*/
/*var ALBUMS = ['MAP OF THE SOUL : 7', 'MAP OF THE SOUL : PERSONA',
"Love Yourself 結 'Answer'", "Love Yourself 轉 'Tear'",
"Love Yourself 承 'Her'", 'You Never Walk Alone', 'Wings',
'The Most Beautiful Moment in Life: Young Forever',
'The Most Beautiful Moment in Life Pt.2',
'The Most Beautiful Moment in Life Pt.1', 'Dark & Wild', 'Skool Luv Affair',
'O!RUL8,2?', '2 Cool 4 Skool'];*/

var ALBUMS = ['MOTS : 7', 'MOTS : PERSONA',
"LY 結 'Answer'", "LY 轉 'Tear'",
"LY 承 'Her'", 'You Never Walk Alone', 'Wings',
'HYYH: Young Forever', 'HYYH Pt.2','HYYH Pt.1', 'Dark & Wild', 
'Skool Luv Affair', 'O!RUL8,2?', '2 Cool 4 Skool'];

/* TYPEWRITER EFFECT FOR TITLE - Used https://typeitjs.com to achieve the effect. */
new TypeIt("#title-text", {
  speed: 0,
  waitUntilVisible: true,
  afterComplete: (step, instance) => {
    document.getElementById("title").style.height = "7em";
    document.getElementById("title").style.transition = "height 0.8s ease-out";
    setTimeout(function() {
      document.getElementById("story").style.display = "block";
      document.getElementById("story").classList.add("fade-in");
    }, 700);
    instance.destroy();
  }
})
  .type("A look at BTS' discography")
  .pause(250)
  .move(-12)
  .delete(4, {delay: 600})
  .type("<span style='color:#551a8b;'>BTS'<span>")
  .move("END")
  .break({delay: 400})
  .type("<b style='font-size:1.9em;'>over the years.</b>")
  .pause(500)
  .go()

/* ALBUM TYPE FILTERS */
var filters = document.getElementsByClassName("album-type-filters")[0]
filters.addEventListener("click", (e) => {
  if (e.target.className != "album-type-filters") {
    var current = document.getElementsByClassName("active")[0];
    current.classList.remove("active");
    e.target.classList.add("active");
    console.log(e.target);
  }
});

// https://en.wikipedia.org/wiki/Pitch_class
var pitchClassNotation = {
  0: "C/B♯/D𝄫",
  1: "C♯/D♭/B𝄪",
  2: "D/C𝄪/E𝄫",
  3: "D♯/E♭/F𝄫",
  4: "E/D𝄪/F♭",
  5: "F/E♯/G𝄫",
  6: "F♯/G♭/E𝄪",
  7: "G/F𝄪/A𝄫",
  8: "G♯/A♭",
  9: "A/G𝄪/B𝄫",
  10: "A♯/B♭/C𝄫",
  11: "B/A𝄪/C♭"
}

//var pitchColors = ['red', '#ff5349', 'orange', '#FFCC00', 'yellow', '#9acd32', 'green', '#1164b4', 'blue', '#8a2be2', 'purple', 'indigo'];
var pitchColors = ['rgba(255, 0, 0, 0.6)', 'rgba(255, 83, 73, 0.6)', 'rgba(255, 165, 0, 0.6)', 'rgba(255, 204, 0, 0.6)', 
'rgba(255, 215, 0, 0.6)', 'rgba(154, 205, 50, 0.6)', 'rgba(0, 128, 0, 0.6)', 'rgba(17, 100, 180, 0.6)', 'rgba(0, 0, 255, 0.6)', 
'rgba(138, 43, 226, 0.6)', 'rgba(128, 0, 128, 0.6)', 'rgba(75, 0, 130, 0.6)'];
var borderColors = ['rgba(255, 0, 0, 1)', 'rgba(255, 83, 73, 1)', 'rgba(255, 165, 0, 1)', 'rgba(255, 204, 0, 1)', 
'rgba(255, 215, 0, 1)', 'rgba(154, 205, 50, 1)', 'rgba(0, 128, 0, 1)', 'rgba(17, 100, 180, 1)', 'rgba(0, 0, 255, 1)', 
'rgba(138, 43, 226, 1)', 'rgba(128, 0, 128, 1)', 'rgba(75, 0, 130, 1)'];

graphKeyDist();
async function graphKeyDist() {
  var res = await fetch('/key_changes')
  .then((response) => {
    return response.json();
  }).then(res => {
    console.log('GET response as JSON:');
    console.log(res);
    console.log(res[2])
    //console.log(res.album_name.values())
    var ctx = document.getElementsByClassName('key-chart')[0].getContext('2d');
    var dataset = [];
    Object.keys(pitchClassNotation).forEach(function(key) {
      dataset.push({
        label: pitchClassNotation[key],
        backgroundColor: pitchColors[key],
        borderColor: borderColors[key],
        borderWidth: 1,
        data: res[key]
      });
    });
    pitchClassNotation.for
    var myChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ALBUMS,
        datasets: dataset
      },
      options: {
        scales: {
          xAxes: [{ stacked: true }],
          yAxes: [{ stacked: true }]
        }
      }
    });
  }).catch(err => {
    console.log("Error: " + err)
  });
}

/* STICKY SIDE CARRIAGE SCROLL - Used https://pudding.cool/process/scrollytelling-sticky/ as a guide. */
const container = d3.select('#scrolly-side');
const stepSel = container.selectAll('.step');

function updateChart(enter) {
	// const sel = container.select(`[data-index='${index}']`);
	// const width = sel.attr('data-width');
  // stepSel.classed('is-active', (d, i) => i === index);
  if (enter) {
    var chart = document.getElementsByClassName('key-chart')[0].getContext('2d');
    chart.options.scales = {
      yAxes: [{
        id: "y-axis-density",
        stacked: true
      }, {
        id: "y-axis-gravity",
        stacked: true
      }]
    };
    chart.data.labels.push(label);
    chart.data.datasets.forEach((dataset) => {
        dataset.data.push(data);
    });
    chart.update();    
  }
}

function init() {
	Stickyfill.add(d3.select('.sticky').node());

	enterView({
		selector: stepSel.nodes(),
		offset: 0.5,
		enter: el => {
      const index = +d3.select(el).attr('data-index');
      console.log("ENTER INDEX " + index);
      if (index == 2) {
        updateChart(True);
      }
      
		},
		exit: el => {
			let index = +d3.select(el).attr('data-index');
      index = Math.max(0, index - 1);
      console.log("EXIT INDEX " + index);
			//updateChart(index);
		}
	});
}

init()