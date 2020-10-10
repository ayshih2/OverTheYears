var ALBUMS_FULL_NAME = ['2 Cool 4 Skool', 'O!RUL8,2?', 'Skool Luv Affair', 'Dark & Wild', 'The Most Beautiful Moment in Life Pt.1', 
'The Most Beautiful Moment in Life Pt.2', 'The Most Beautiful Moment in Life: Young Forever', 'Wings', 'You Never Walk Alone', 
"Love Yourself 承 'Her'", "Love Yourself 轉 'Tear'", "Love Yourself 結 'Answer'", 'MAP OF THE SOUL : PERSONA', 'MAP OF THE SOUL : 7']


var ALBUMS = ['2 Cool 4 Skool', 'O!RUL8,2?', 'Skool Luv Affair', 'Dark & Wild', 'HYYH Pt.1', 'HYYH Pt.2', 'HYYH: Young Forever', 'Wings', 
'You Never Walk Alone', "LY 承 'Her'", "LY 轉 'Tear'", "LY 結 'Answer'", 'MOTS : PERSONA', 'MOTS : 7']

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

graphSpeechiness()
function graphSpeechiness() {
  // Fetch data from backend if you haven't already
  var res = fetch('/speechiness')
  .then((response) => {
    return response.json();
  }).then(data => {
    var ctx = document.getElementsByClassName('speechiness-chart')[0].getContext('2d');
    console.log("SPEECHINESS");
    console.log(data)
    var dataset = []
    console.log("sepech dataset");
    ALBUMS_FULL_NAME.forEach(album => {
      dataset.push(data[album]);
    });
    console.log(dataset)
    var chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: ALBUMS,
        datasets: [{
          data: dataset,
          label: 'Speechiness',
          pointBackgroundColor: 'rgba(85, 26, 139, 0.6)',
          pointBorderColor: 'rgba(85, 26, 139, 0.6)',
          borderColor: 'rgba(85, 26, 139, 0.6)',
          backgroundColor: 'rgba(85, 26, 139, 0.4)',
        }]
      },
      options: {
        legend: {
          display: false
        },
        scales: {
          yAxes: [{   
            scaleLabel: {
              display: true,
              labelString: 'Speechiness' 
            },
            // ticks: {
            //   min: 0,
            //   max: 1
            // }
          }]
        },
        plugins: {
          deferred: { 
            yOffset: '50%', // defer until 50% of the canvas height are inside the viewport
            delay: 500 
          }
        }
      }
    });
  }).catch(err => {
    console.log("Error: " + err)
  });
  
}

// https://en.wikipedia.org/wiki/Pitch_class
var pitchClassNotation = {
  0: "C",
  1: "C♯",
  2: "D",
  3: "D♯",
  4: "E",
  5: "F",
  6: "F♯",
  7: "G",
  8: "G♯",
  9: "A",
  10: "A♯",
  11: "B"
}

/*var pitchClassNotation = {
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
}*/

var pitchColors = ['rgba(255, 0, 0, 0.6)', 'rgba(255, 83, 73, 0.6)', 'rgba(255, 165, 0, 0.6)', 'rgba(255, 204, 0, 0.6)', 
'rgba(255, 215, 0, 0.6)', 'rgba(154, 205, 50, 0.6)', 'rgba(0, 128, 0, 0.6)', 'rgba(17, 100, 180, 0.6)', 'rgba(0, 0, 255, 0.6)', 
'rgba(138, 43, 226, 0.6)', 'rgba(128, 0, 128, 0.6)', 'rgba(75, 0, 130, 0.6)'];
var borderColors = ['rgba(255, 0, 0, 1)', 'rgba(255, 83, 73, 1)', 'rgba(255, 165, 0, 1)', 'rgba(255, 204, 0, 1)', 
'rgba(255, 215, 0, 1)', 'rgba(154, 205, 50, 1)', 'rgba(0, 128, 0, 1)', 'rgba(17, 100, 180, 1)', 'rgba(0, 0, 255, 1)', 
'rgba(138, 43, 226, 1)', 'rgba(128, 0, 128, 1)', 'rgba(75, 0, 130, 1)'];

var chart = null;
var pitchOnlyConfigs = {}
var pitchAndModeConfigs = {};
var hasFetchedPitches = false;
var hasFetchedModes = false;
var showingPitchGraph = true;
//graphKeyDist();
async function graphKeyDist() {
  if (!hasFetchedPitches) {
    // Fetch data from backend if you haven't already
    var res = await fetch('/key_changes')
    .then((response) => {
      return response.json();
    }).then(res => {
      var ctx = document.getElementsByClassName('key-chart')[0].getContext('2d');
      var dataset = []
      Object.keys(pitchClassNotation).forEach(function(key) {
        dataset.push({
          label: pitchClassNotation[key],
          backgroundColor: pitchColors[key],
          borderColor: borderColors[key],
          borderWidth: 1,
          data: res[key]
        });
      });
      pitchOnlyConfigs = {
        responsive: true,
        type: 'bar',
        data: {
          labels: ALBUMS,
          datasets: dataset
        },
        options: {
          scales: {
            xAxes: [{ stacked: true }],
            yAxes: [{ 
              stacked: true,      
              scaleLabel: {
                display: true,
                labelString: 'Number of Songs'
              }
            }]
          }
        }
      };
      chart = new Chart(ctx, pitchOnlyConfigs);
      hasFetchedPitches = true;
    }).catch(err => {
      console.log("Error: " + err)
    });
  }
}


/* STICKY SIDE CARRIAGE SCROLL - Used https://pudding.cool/process/scrollytelling-sticky/ as a guide. */
const container = d3.select('#scrolly-overlay');
const stepSel = container.selectAll('.step');

/*
 * Updates the chart based on how many of the information divs about pitch/key the user has scrolled by. Rather than just updating the dataset, the chart 
 * must be destroyed and reinitialized each time in order for there to be a fluid animation between the two datasets.
 */
async function updateChart(enter) {
  var ctx = document.getElementsByClassName('key-chart')[0].getContext('2d');
  if (enter) {
    // Get data (pitch and mode of each song from every album) if haven't already
    showingPitchGraph = false;
    if (!hasFetchedModes) {
      var res = await fetch('/mode_changes')
      .then(response => {
        return response.json()
      })
      .then(res => {
        console.log(res)
        var dataset = [];
        Object.keys(pitchClassNotation).forEach(function(key) {
          dataset.push({
            label: pitchClassNotation[key] + " Major",
            type: "bar",
            stack: "major",
            backgroundColor: pitchColors[key],
            borderColor: borderColors[key],
            borderWidth: 1,
            data: res[key]['major']
          });
          dataset.push({
            label: pitchClassNotation[key] + " Minor",
            type: "bar",
            stack: "minor",
            backgroundColor: pattern.draw('zigzag', pitchColors[key]),
            borderColor: borderColors[key],
            borderWidth: 1,
            data: res[key]['minor']
          });
        });
        pitchAndModeConfigs = {
          responsive: true,
          type: 'bar',
          data: {
            labels: ALBUMS,
            datasets: dataset
          },
          options: {
            scales: {
              xAxes: [{ stacked: true }],
              yAxes: [{ 
                stacked: true,      
                scaleLabel: {
                  display: true,
                  labelString: 'Number of Songs'
                }
              }]
            }
          }
        }
        hasFetchedModes = true;
      })
      .catch(err => {
        console.log("Error: " + err)
      });  
    }
    chart.destroy();
    chart = new Chart(ctx, pitchAndModeConfigs);
  } else {
    showingPitchGraph = true;
    chart.destroy();
    chart = new Chart(ctx, pitchOnlyConfigs);
  }
}

function init() {
	enterView({
		selector: stepSel.nodes(),
		offset: 0.5,
		enter: el => {
      console.log(el);
      const album_series = d3.select(el).attr('class').split(' ')[1];
      console.log(album_series);
      console.log(":(")
      d3.selectAll('#album-overview img')
      .style('-webkit-filter', 'grayscale(1)')
      .style('filter', 'grayscale(1)')
      .style('opacity', '0.3');
      d3.selectAll(`img.${album_series}`)
      .style('filter', 'none')
      .style('transition', 'opacity 0.3s')
      .style('opacity', '1');
		},
		exit: el => {
      console.log(el);
      const album_series = d3.select(el).attr('class').split(' ')[1];
      console.log("EXIT");
      console.log(album_series);
      d3.selectAll('#album-overview img')
      .style('-webkit-filter', 'grayscale(1)')
      .style('filter', 'grayscale(1)')
      .style('opacity', '0.3');
      if (album_series != 'mots-series') {
        d3.selectAll(`img.${album_series}`)
        .style('filter', 'none')
        .style('transition', 'opacity 0.3s')
        .style('opacity', '1');
      }
		}
	});
}

init()