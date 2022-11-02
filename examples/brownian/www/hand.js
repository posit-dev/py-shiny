

function mediapipeHand({uiName, videoId, canvasId, options = {}, debug = false} = {}) {

  // Code taken from https://google.github.io/mediapipe/solutions/hands.html
  // and modified to set the Shiny input value when a hand is detected.

  const videoElement = document.getElementById(videoId);
  const canvasElement = document.getElementById(canvasId);
  const canvasCtx = canvasElement.getContext('2d');

  function onResults(results) {
    // Set Shiny input value
    if (results.multiHandLandmarks.length > 0) {
      Shiny.setInputValue(uiName, results.multiHandLandmarks[0]);
    } else {
      Shiny.setInputValue(uiName, null)
    }

    // Do not draw anything unless debugging
    if (!debug) return;

    // Draw hand on canvas
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    canvasCtx.drawImage(
        results.image, 0, 0, canvasElement.width, canvasElement.height);
    if (results.multiHandLandmarks) {
      for (const landmarks of results.multiHandLandmarks) {
        drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS,
                      {color: '#00FF00', lineWidth: 5});
        drawLandmarks(canvasCtx, landmarks, {color: '#FF0000', lineWidth: 2});
      }
    }
    canvasCtx.restore();
  }
  const hands = new Hands({locateFile: (file) => {
    return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
  }});
  hands.setOptions(options);
  hands.onResults(onResults);

  const camera = new Camera(videoElement, {
    onFrame: async () => {
      await hands.send({image: videoElement});
    },
    width: 1280,
    height: 720
  });
  camera.start();

}
