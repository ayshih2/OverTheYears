// get data to use in chart
var res = fetch('/albm_avg_data')
  .then((response) => {
    return response.json();
  }).then(data => {
    console.log('GET response as JSON:');
    console.log(data);
  }).catch(err => {
    console.log("Error: " + err)
  });

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

/* STICKY SIDE CARRIAGE SCROLL - Used https://pudding.cool/process/scrollytelling-sticky/ as a guide. */
const container = d3.select('#scrolly-side');
const stepSel = container.selectAll('.step');

function updateChart(index) {
  const sel = container.select(`[data-index='${index}']`);
  console.log(sel);
  const width = sel.attr('data-width');
  stepSel.classed('is-active', (d, i) => i === index);
  container.select('.bar-inner').style('width', width);
}

function init() {
  Stickyfill.add(d3.select('.sticky').node());

  enterView({
    selector: stepSel.nodes(),
    offset: 0.5,
    enter: el => {
      const index = +d3.select(el).attr('data-index');
      updateChart(index);
    },
    exit: el => {
      let index = +d3.select(el).attr('data-index');
      index = Math.max(0, index - 1);
      updateChart(index);
    }
  });
}

init()

