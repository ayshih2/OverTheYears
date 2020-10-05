// https://typeitjs.com
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
