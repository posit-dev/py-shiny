async function main(video, canvas) {
    const stream = await navigator.mediaDevices.getUserMedia({video: true});
    video.srcObject = stream;
    video.play();
    video.addEventListener("canplay", () => {
        // Dimension of the video we want
        const w = 320;
        const h = w * (video.videoHeight/video.videoWidth);

        video.setAttribute("width", w);
        video.setAttribute("height", h);
        canvas.setAttribute("width", w);
        canvas.setAttribute("height", h)
        const ctx = canvas.getContext("2d");
        function capture() {
        ctx.drawImage(video, 0, 0, w, h);
        const imageData = ctx.getImageData(0, 0, w, h);
        console.log(imageData);
        // Shiny.setInputValue
        }
        capture();
        setInterval(capture, 1000);
    });
}
// main(document.getElementById("video"), document.getElementById("canvas"));


const videoElement = document.getElementById("video");
const canvasElement = document.getElementById("canvas");
const canvasCtx = canvasElement.getContext('2d');

function onResults(results) {
  // console.log("results", results);
  if (results.multiHandLandmarks.length > 0) {
    Shiny.setInputValue("hand", results.multiHandLandmarks[0]);
  } else {
    Shiny.setInputValue("hand", null)
  }
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
hands.setOptions({
  maxNumHands: 1,
  modelComplexity: 1,
  minDetectionConfidence: 0.9,
  minTrackingConfidence: 0.9
});
hands.onResults(onResults);

const camera = new Camera(videoElement, {
  onFrame: async () => {
    await hands.send({image: videoElement});
  },
  width: 1280,
  height: 720
});
camera.start();
